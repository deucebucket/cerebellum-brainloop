"""Fast server-based eval for the used-memory probes (llama-server /completion).

Same kind-aware scoring as brainloop_eval_usable_bake.py, but hits a running
llama-server so the model loads once. Concurrent requests. Aggregates by
pool x kind so trained-vs-control transfer is visible.
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def norm(t: str) -> str:
    return re.sub(r"[^a-z0-9]", "", t.lower())


def score_hit(kind: str, gold: str, out: str) -> bool:
    o = out.strip()
    low = o.lower()
    if kind == "count":
        m = re.search(r"-?\d+", o)
        return bool(m) and m.group(0) == gold.strip()
    if kind in ("presence_yes", "presence_no"):
        # list-first format puts the verdict last; take the final yes/no token
        verdicts = re.findall(r"\b(yes|no)\b", low)
        return bool(verdicts) and verdicts[-1] == gold.strip().lower()
    toks = [norm(t) for t in re.split(r"[,\s]+", gold) if norm(t)]
    no = norm(o)
    return all(t in no for t in toks) if toks else (norm(gold) in no)


def complete(url: str, prompt: str, n: int) -> str:
    body = json.dumps({"prompt": prompt, "temperature": 0.0, "n_predict": n,
                       "stop": ["\n", "Question:"], "cache_prompt": False}).encode()
    req = urllib.request.Request(url + "/completion", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())["content"].strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8090")
    ap.add_argument("--eval", default="bake_splits/e1047_ast_usable/eval.jsonl")
    ap.add_argument("--out", required=True)
    ap.add_argument("--n-predict", type=int, default=16)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    probes = [json.loads(l) for l in open(args.eval, encoding="utf-8")]

    def work(pr):
        q = pr["messages"][0]["content"]
        gold = pr["messages"][1]["content"]
        out = complete(args.url, f"Question: {q}\nAnswer:", args.n_predict)
        return {"symbol": pr["symbol"], "pool": pr.get("pool", "?"),
                "kind": pr.get("kind", ""), "q": q, "gold": gold, "out": out,
                "hit": score_hit(pr.get("kind", ""), gold, out)}

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        rows = list(ex.map(work, probes))

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    with outp.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    agg = defaultdict(lambda: [0, 0])
    for r in rows:
        a = agg[(r["pool"], r["kind"])]
        a[0] += 1
        a[1] += int(r["hit"])
    kinds = ["enum_heldout", "count", "presence_yes", "presence_no"]
    print(f"scored {len(rows)} probes -> {outp}\n")
    print("=== hit-rate by pool x kind (hit/total) ===")
    for pool in sorted({k[0] for k in agg}):
        cells = []
        for kind in kinds:
            t, h = agg.get((pool, kind), [0, 0])
            cells.append(f"{kind}={h}/{t}")
        print(f"  {pool:8}  " + "  ".join(cells))
    # overall trained-vs-control on the reasoning kinds (count+presence)
    def tot(pool, ks):
        return (sum(agg[(pool, k)][1] for k in ks if (pool, k) in agg),
                sum(agg[(pool, k)][0] for k in ks if (pool, k) in agg))
    rk = ["count", "presence_yes", "presence_no"]
    th, tt = tot("trained", rk)
    ch, ct = tot("control", rk)
    print(f"\n  REASONING (count+presence): trained {th}/{tt}   control {ch}/{ct}")


if __name__ == "__main__":
    main()
