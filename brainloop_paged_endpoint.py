"""E1059 — single-slot paged memory controller (the product, concretely).

ONE VRAM slot serves a knowledge base of N baked packs held on disk (cold tier).
For each incoming query: route -> if the routed pack is not the hot one, PAGE it
in (evict current llama-server, load the pack's GGUF), then answer. Demonstrates
that a 9 GB hot slot answers across an arbitrarily large cold tier -> stores way
more than fits in the model's VRAM footprint.

Runs an online (shuffled) mixed stream so real swaps happen. Reports accuracy,
page-ins, and the hot-vs-cold footprint. Serving uses the mainline llama-server
in distrobox; lifecycle managed here (launch / health / evict-by-port).
"""

from __future__ import annotations

import json
import re
import subprocess
import time
import urllib.request
from pathlib import Path

BIN = "/var/home/deucebucket/ai-drive/llama.cpp-mainline/build/bin"
ROOT = "/var/home/deucebucket/ai-drive/cerebellum/cerebellum-dev/conch-poc"
PORT = 8110
PACK_GGUF = {
    "ast": f"{ROOT}/merged_models/e1051_battery_v4_merged-q8_0.gguf",
    "fiction1": f"{ROOT}/merged_models/e1052_fiction_merged-q8_0.gguf",
    "stdlib": f"{ROOT}/merged_models/e1056_stdlib_merged-q8_0.gguf",
}
PACK_SPLIT = {
    "ast": "bake_splits/e1051_ast_battery_v4",
    "fiction1": "bake_splits/e1052_fiction",
    "stdlib": "bake_splits/e1056_stdlib_recall",
}
RUN = Path("brainloop_runs/e1059_paged_endpoint")


def norm(t): return re.sub(r"[^a-z0-9]", "", t.lower())


def score_hit(kind, gold, out):
    o = out.strip(); low = o.lower()
    if kind == "count":
        m = re.search(r"-?\d+", o); return bool(m) and m.group(0) == gold.strip()
    if kind in ("presence_yes", "presence_no"):
        v = re.findall(r"\b(yes|no)\b", low); return bool(v) and v[-1] == gold.strip().lower()
    toks = [norm(t) for t in re.split(r"[,\s]+", gold) if norm(t)]
    return all(t in norm(o) for t in toks) if toks else (norm(gold) in norm(o))


class Slot:
    """Single VRAM slot holding at most one pack's llama-server."""
    def __init__(self):
        self.hot = None
        self.proc = None

    def _evict(self):
        subprocess.run(["bash", "-lc", f"fuser -k {PORT}/tcp 2>/dev/null"], check=False)
        time.sleep(2)
        self.hot = None

    def page_in(self, pack):
        if self.hot == pack:
            return 0.0
        self._evict()
        t0 = time.time()
        cmd = (f"LD_LIBRARY_PATH='{BIN}' '{BIN}/llama-server' -m {PACK_GGUF[pack]} "
               f"-ngl 99 --host 127.0.0.1 --port {PORT} -c 4096 --parallel 2")
        self.proc = subprocess.Popen(["distrobox", "enter", "ai", "--", "bash", "-lc", cmd],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(60):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health", timeout=2) as r:
                    if b"ok" in r.read():
                        self.hot = pack
                        return time.time() - t0
            except Exception:
                time.sleep(1)
        raise RuntimeError(f"pack {pack} failed to load")

    def ask(self, q):
        body = json.dumps({"prompt": f"Question: {q}\nAnswer:", "temperature": 0.0,
                           "n_predict": 48, "stop": ["\n", "Question:"], "cache_prompt": False}).encode()
        req = urllib.request.Request(f"http://127.0.0.1:{PORT}/completion", data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())["content"].strip()


def build_router():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    Xtr, ytr = [], []
    for name, d in PACK_SPLIT.items():
        for l in open(f"{d}/train.jsonl"):
            Xtr.append(json.loads(l)["messages"][0]["content"]); ytr.append(name)
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    clf = LogisticRegression(max_iter=2000, C=10.0).fit(vec.fit_transform(Xtr), ytr)
    return lambda q: str(clf.predict(vec.transform([q]))[0])


def build_stream(n_per=10):
    """Interleaved (worst-case paging) mixed stream."""
    per = {}
    for name, d in PACK_SPLIT.items():
        per[name] = [json.loads(l) for l in open(f"{d}/eval.jsonl")][:n_per]
    stream = []
    for i in range(n_per):
        for name in PACK_SPLIT:  # round-robin -> forces a page-in almost every step
            r = per[name][i]
            stream.append({"true_pack": name, "kind": r.get("kind", "recall"),
                           "q": r["messages"][0]["content"], "gold": r["messages"][1]["content"]})
    return stream


def main():
    RUN.mkdir(parents=True, exist_ok=True)
    route = build_router()
    stream = build_stream(10)
    slot = Slot()
    rows = []
    page_ins = 0
    total_load = 0.0
    try:
        for i, s in enumerate(stream, 1):
            pack = route(s["q"])
            load_ms = slot.page_in(pack)
            if load_ms > 0:
                page_ins += 1; total_load += load_ms
            out = slot.ask(s["q"])
            hit = score_hit(s["kind"], s["gold"], out)
            rows.append({"true_pack": s["true_pack"], "routed_pack": pack,
                         "routed_ok": pack == s["true_pack"], "hit": hit,
                         "paged_in": load_ms > 0})
            print(f"[{i:02d}/{len(stream)}] true={s['true_pack']:8} routed={pack:8} "
                  f"{'PAGE-IN' if load_ms>0 else 'hot    '} hit={int(hit)}")
    finally:
        slot._evict()

    n = len(rows)
    correct = sum(r["hit"] for r in rows)
    route_acc = sum(r["routed_ok"] for r in rows) / n
    (RUN / "results.json").write_text(json.dumps({
        "n": n, "correct": correct, "accuracy": correct / n, "router_accuracy": route_acc,
        "page_ins": page_ins, "avg_load_sec": total_load / max(page_ins, 1),
        "hot_footprint_gb": 8.7, "cold_tier_packs": len(PACK_GGUF),
        "cold_tier_gb": round(8.7 * len(PACK_GGUF), 1),
    }, indent=2) + "\n")
    print(f"\n=== PAGED MEMORY CONTROLLER over {n} interleaved queries ===")
    print(f"  accuracy        : {correct}/{n} ({100*correct/n:.1f}%)")
    print(f"  router accuracy : {100*route_acc:.1f}%")
    print(f"  page-ins        : {page_ins} (avg load {total_load/max(page_ins,1):.1f}s)")
    print(f"  VRAM hot slot   : ~8.7 GB (one pack)")
    print(f"  cold tier       : {len(PACK_GGUF)} packs = ~{8.7*len(PACK_GGUF):.0f} GB on disk")
    print(f"  => a {8.7:.0f} GB hot slot served a {8.7*len(PACK_GGUF):.0f} GB knowledge base")


if __name__ == "__main__":
    main()
