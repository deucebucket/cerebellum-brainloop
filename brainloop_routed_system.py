"""E1058 — end-to-end routed system on a MIXED query stream (the product).

A single system answers a mixed stream of queries by ROUTING each to the right
baked pack, then answering from that pack's GGUF. Compares:
  - base       : the plain model answers everything
  - merged     : (optional) one model with all packs merged
  - routed     : router picks the pack; that pack's model answers
Phases (router is CPU; serving is one model at a time on the GPU):
  plan   : build the mixed stream, train router, write the routing plan.
  answer : given a live server --url and --serving <pack|base>, answer the
           queries assigned to that server, append scored rows to results.
  report : aggregate end-to-end accuracy per system.
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PACKS = {
    "ast": "bake_splits/e1051_ast_battery_v4",
    "fiction1": "bake_splits/e1052_fiction",
    "stdlib": "bake_splits/e1056_stdlib_recall",
}
PER_PACK = 60  # queries sampled per pack into the mixed stream
RUN = Path("brainloop_runs/e1058_routed_system")
PLAN = RUN / "plan.jsonl"
RES = RUN / "results.jsonl"


def norm(t): return re.sub(r"[^a-z0-9]", "", t.lower())


def score_hit(kind, gold, out):
    o = out.strip(); low = o.lower()
    if kind == "count":
        m = re.search(r"-?\d+", o); return bool(m) and m.group(0) == gold.strip()
    if kind in ("presence_yes", "presence_no"):
        v = re.findall(r"\b(yes|no)\b", low); return bool(v) and v[-1] == gold.strip().lower()
    toks = [norm(t) for t in re.split(r"[,\s]+", gold) if norm(t)]
    no = norm(o)
    return all(t in no for t in toks) if toks else (norm(gold) in no)


def complete(url, prompt, n=48):
    body = json.dumps({"prompt": prompt, "temperature": 0.0, "n_predict": n,
                       "stop": ["\n", "Question:"], "cache_prompt": False}).encode()
    req = urllib.request.Request(url + "/completion", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())["content"].strip()


def do_plan():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    Xtr, ytr = [], []
    for name, d in PACKS.items():
        for l in open(f"{d}/train.jsonl"):
            Xtr.append(json.loads(l)["messages"][0]["content"]); ytr.append(name)
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    clf = LogisticRegression(max_iter=2000, C=10.0).fit(vec.fit_transform(Xtr), ytr)

    stream = []
    for name, d in PACKS.items():
        rows = [json.loads(l) for l in open(f"{d}/eval.jsonl")]
        for r in rows[:PER_PACK]:
            stream.append({"true_pack": name, "kind": r.get("kind", "recall"),
                           "q": r["messages"][0]["content"], "gold": r["messages"][1]["content"]})
    preds = clf.predict(vec.transform([s["q"] for s in stream]))
    RUN.mkdir(parents=True, exist_ok=True)
    with PLAN.open("w") as f:
        for s, p in zip(stream, preds):
            s["pred_pack"] = str(p); f.write(json.dumps(s) + "\n")
    racc = sum(s["true_pack"] == s["pred_pack"] for s in
               [json.loads(l) for l in open(PLAN)]) / len(stream)
    print(f"planned {len(stream)} queries; router accuracy {racc*100:.1f}%")


def do_answer(url, serving):
    plan = [json.loads(l) for l in open(PLAN)]
    if serving == "base":
        targets = plan  # base answers everything
        col = "base_out"
    else:
        targets = [s for s in plan if s["pred_pack"] == serving]  # routed subset
        col = "routed_out"
    def work(s):
        out = complete(url, f"Question: {s['q']}\nAnswer:")
        return (s["q"], s["true_pack"], col, out, score_hit(s["kind"], s["gold"], out))
    with ThreadPoolExecutor(max_workers=4) as ex:
        rows = list(ex.map(work, targets))
    with RES.open("a") as f:
        for q, tp, c, out, hit in rows:
            f.write(json.dumps({"q": q, "true_pack": tp, "col": c,
                                "serving": serving, "out": out, "hit": hit}) + "\n")
    print(f"answered {len(rows)} queries on {serving}: {sum(r[4] for r in rows)} correct")


def do_report():
    plan = {s["q"]: s for s in (json.loads(l) for l in open(PLAN))}
    res = [json.loads(l) for l in open(RES)]
    base = {r["q"]: r for r in res if r["col"] == "base_out"}
    routed = {r["q"]: r for r in res if r["col"] == "routed_out"}
    n = len(plan)
    b = sum(base[q]["hit"] for q in plan if q in base)
    # routed: a query is correct only if it was answered by the server it was routed to AND hit
    rt = sum(routed[q]["hit"] for q in plan if q in routed)
    print(f"\n=== END-TO-END on mixed stream of {n} queries ===")
    print(f"  BASE   (one model answers all): {b}/{n} ({100*b/n:.1f}%)")
    print(f"  ROUTED (router -> pack model) : {rt}/{n} ({100*rt/n:.1f}%)")
    by = defaultdict(lambda: [0, 0])
    for q, s in plan.items():
        by[s["true_pack"]][1] += 1
        if q in routed and routed[q]["hit"]:
            by[s["true_pack"]][0] += 1
    print("  routed per true-pack:")
    for k, (h, t) in by.items():
        print(f"    {k:9} {h}/{t}")
    Path(RUN / "report.json").write_text(json.dumps(
        {"n": n, "base_correct": b, "routed_correct": rt,
         "base_acc": b / n, "routed_acc": rt / n}, indent=2) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["plan", "answer", "report"])
    ap.add_argument("--url"); ap.add_argument("--serving")
    a = ap.parse_args()
    if a.mode == "plan":
        do_plan()
    elif a.mode == "answer":
        do_answer(a.url, a.serving)
    else:
        do_report()


if __name__ == "__main__":
    main()
