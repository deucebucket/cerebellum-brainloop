"""E1063 — memory controller with a K-slot LRU hot cache (production shape).

Keeps up to K baked packs resident in VRAM (one llama-server per slot); on a
cache MISS, evicts the LRU slot and pages the requested pack in. With query
locality, a small hot cache amortizes the ~4s page-in to near zero. Reports
accuracy, page-ins, and hit-rate for a given K and access pattern, so we can show
the cold tier (all packs on disk) >> the hot footprint (K packs in VRAM).

Pack registry is auto-built from whatever <name>-q8_0 GGUFs + bake_splits exist.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
import urllib.request
from pathlib import Path

BIN = "/var/home/deucebucket/ai-drive/llama.cpp-mainline/build/bin"
ROOT = "/var/home/deucebucket/ai-drive/cerebellum/cerebellum-dev/conch-poc"
BASE_PORT = 8120

# pack name -> (gguf, bake_split dir)
REGISTRY = {
    "ast":      ("merged_models/e1051_battery_v4_merged-q8_0.gguf", "bake_splits/e1051_ast_battery_v4"),
    "fiction1": ("merged_models/e1052_fiction_merged-q8_0.gguf",    "bake_splits/e1052_fiction"),
    "fiction2": ("merged_models/e1054_fiction2_merged-q8_0.gguf",   "bake_splits/e1054_fiction2"),
    "fiction3": ("merged_models/e1061_fic3_merged-q8_0.gguf",       "bake_splits/e1061_fic3"),
    "fiction4": ("merged_models/e1062_fic4_merged-q8_0.gguf",       "bake_splits/e1062_fic4"),
    "stdlib":   ("merged_models/e1056_stdlib_merged-q8_0.gguf",     "bake_splits/e1056_stdlib_recall"),
    "stdlib2":  ("merged_models/e1060_stdlib2_merged-q8_0.gguf",    "bake_splits/e1060_stdlib2"),
}


def available():
    return {n: v for n, v in REGISTRY.items() if Path(v[0]).exists()}


def norm(t): return re.sub(r"[^a-z0-9]", "", t.lower())


def score_hit(kind, gold, out):
    o = out.strip(); low = o.lower()
    if kind == "count":
        m = re.search(r"-?\d+", o); return bool(m) and m.group(0) == gold.strip()
    if kind in ("presence_yes", "presence_no"):
        v = re.findall(r"\b(yes|no)\b", low); return bool(v) and v[-1] == gold.strip().lower()
    toks = [norm(t) for t in re.split(r"[,\s]+", gold) if norm(t)]
    return all(t in norm(o) for t in toks) if toks else (norm(gold) in norm(o))


class MemCtl:
    def __init__(self, packs, k):
        self.packs = packs
        self.k = k
        self.slots = {}      # pack -> (port, proc)
        self.lru = []        # most-recent last
        self.page_ins = 0

    def _launch(self, pack, port):
        gguf = f"{ROOT}/{self.packs[pack][0]}"
        cmd = (f"LD_LIBRARY_PATH='{BIN}' '{BIN}/llama-server' -m {gguf} -ngl 99 "
               f"--host 127.0.0.1 --port {port} -c 4096 --parallel 2")
        proc = subprocess.Popen(["distrobox", "enter", "ai", "--", "bash", "-lc", cmd],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(60):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2) as r:
                    if b"ok" in r.read():
                        return proc
            except Exception:
                time.sleep(1)
        raise RuntimeError(f"{pack} failed to load on {port}")

    def _evict(self, pack):
        port, _ = self.slots.pop(pack)
        subprocess.run(["bash", "-lc", f"fuser -k {port}/tcp 2>/dev/null"], check=False)
        time.sleep(1)

    def get_port(self, pack):
        if pack in self.slots:                      # cache hit
            self.lru.remove(pack); self.lru.append(pack)
            return self.slots[pack][0], False
        # miss -> page in
        if len(self.slots) >= self.k:
            victim = self.lru.pop(0)
            self._evict(victim)
        port = BASE_PORT + (len(self.slots) % self.k)
        # ensure a free port (reuse victim's slot index range)
        used = {p for p, _ in self.slots.values()}
        port = next(BASE_PORT + i for i in range(self.k) if (BASE_PORT + i) not in used)
        proc = self._launch(pack, port)
        self.slots[pack] = (port, proc); self.lru.append(pack)
        self.page_ins += 1
        return port, True

    def ask(self, port, q):
        body = json.dumps({"prompt": f"Question: {q}\nAnswer:", "temperature": 0.0,
                           "n_predict": 48, "stop": ["\n", "Question:"], "cache_prompt": False}).encode()
        req = urllib.request.Request(f"http://127.0.0.1:{port}/completion", data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())["content"].strip()

    def shutdown(self):
        for pack in list(self.slots):
            self._evict(pack)


def build_router(packs):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    Xtr, ytr = [], []
    for name, (_, d) in packs.items():
        for l in open(f"{d}/train.jsonl"):
            Xtr.append(json.loads(l)["messages"][0]["content"]); ytr.append(name)
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    clf = LogisticRegression(max_iter=2000, C=10.0).fit(vec.fit_transform(Xtr), ytr)
    return lambda q: str(clf.predict(vec.transform([q]))[0])


def build_stream(packs, per, pattern, seed=7):
    per_pack = {}
    for name, (_, d) in packs.items():
        per_pack[name] = [json.loads(l) for l in open(f"{d}/eval.jsonl")][:per]
    names = list(packs)
    stream = []
    if pattern == "skew":            # realistic: 2 hot packs dominate, recur with locality
        import random
        rng = random.Random(seed)
        # zipf-ish popularity over packs; sample with short bursts so hot packs recur
        pop = {n: (10 if i < 2 else 1) for i, n in enumerate(names)}
        idx = {n: 0 for n in names}
        total = per * len(names)
        while len(stream) < total:
            cand = [n for n in names if idx[n] < per]
            if not cand:
                break
            weights = [pop[n] for n in cand]
            pack = rng.choices(cand, weights=weights, k=1)[0]
            burst = rng.randint(1, 3)
            for _ in range(burst):
                if idx[pack] < per:
                    stream.append((pack, per_pack[pack][idx[pack]])); idx[pack] += 1
        return [{"true_pack": n, "kind": r.get("kind", "recall"),
                 "q": r["messages"][0]["content"], "gold": r["messages"][1]["content"]}
                for n, r in stream]
    if pattern == "bursty":          # locality: all of pack A, then pack B, ...
        for name in names:
            for r in per_pack[name]:
                stream.append((name, r))
    elif pattern == "roundrobin":    # worst case: switch pack every query
        for i in range(per):
            for name in names:
                stream.append((name, per_pack[name][i]))
    else:                            # interleaved blocks of 5 (realistic locality)
        blk = 5
        idx = {n: 0 for n in names}
        order = names * (per // blk + 1)
        for name in order:
            for _ in range(blk):
                if idx[name] < per:
                    stream.append((name, per_pack[name][idx[name]])); idx[name] += 1
    return [{"true_pack": n, "kind": r.get("kind", "recall"),
             "q": r["messages"][0]["content"], "gold": r["messages"][1]["content"]}
            for n, r in stream]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slots", type=int, default=2)
    ap.add_argument("--per", type=int, default=8)
    ap.add_argument("--pattern", default="blocks", choices=["bursty", "roundrobin", "blocks", "skew"])
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    packs = available()
    route = build_router(packs)
    stream = build_stream(packs, a.per, a.pattern, a.seed)
    ctl = MemCtl(packs, a.slots)
    correct = route_ok = 0
    t0 = time.time()
    try:
        for i, s in enumerate(stream, 1):
            pack = route(s["q"])
            port, miss = ctl.get_port(pack)
            out = ctl.ask(port, s["q"])
            hit = score_hit(s["kind"], s["gold"], out)
            correct += hit; route_ok += (pack == s["true_pack"])
            print(f"[{i:03d}/{len(stream)}] true={s['true_pack']:9} routed={pack:9} "
                  f"{'MISS->page' if miss else 'cache-hit '} ok={int(hit)}", flush=True)
    finally:
        ctl.shutdown()
    n = len(stream)
    out = {"packs": list(packs), "n_packs": len(packs), "slots": a.slots,
           "pattern": a.pattern, "queries": n, "accuracy": correct / n,
           "router_accuracy": route_ok / n, "page_ins": ctl.page_ins,
           "cache_hit_rate": 1 - ctl.page_ins / n, "wall_sec": round(time.time() - t0, 1),
           "hot_gb": round(8.7 * a.slots, 1), "cold_gb": round(8.7 * len(packs), 1)}
    RUN = Path(f"brainloop_runs/e1063_memctl_k{a.slots}_{a.pattern}")
    RUN.mkdir(parents=True, exist_ok=True)
    (RUN / "results.json").write_text(json.dumps(out, indent=2) + "\n")
    print("\n=== MEMORY CONTROLLER ===")
    for k, v in out.items():
        print(f"  {k:16} {v}")


if __name__ == "__main__":
    main()
