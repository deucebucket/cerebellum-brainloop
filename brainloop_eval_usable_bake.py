"""E1046 eval — run held-out used-memory probes through a compiled GGUF.

Reads bake_splits/e1046_usable_ast/eval.jsonl (held-out phrasings, per-symbol,
with a `symbol`/`pool` tag and an `ast.If` control). Runs each probe through
llama-cli (qa format, temp 0, single-turn) and scores a normalized
content-contains hit against the ground-truth answer. Dumps raw outputs for
manual audit; aggregates by symbol so trained-vs-control is visible.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

LLAMA_CLI = "/var/home/deucebucket/ai-drive/llama.cpp-pr24260/build-cpu/bin/llama-cli"
TRAINED = {"ast.comprehension", "ast.While", "ast.For"}


def norm(t: str) -> str:
    return re.sub(r"[^a-z0-9]", "", t.lower())


def score_hit(kind: str, gold: str, out: str) -> bool:
    """Kind-aware correctness. Falls back to content-contains when kind absent."""
    o = out.strip()
    low = o.lower()
    if kind == "count":
        m = re.search(r"-?\d+", o)
        return bool(m) and m.group(0) == gold.strip()
    if kind in ("presence_yes", "presence_no"):
        m = re.search(r"[a-z]+", low)
        return bool(m) and m.group(0) == gold.strip().lower()  # first word == yes/no
    # enum / enum_heldout / signature: every gold field token present, in any order
    toks = [norm(t) for t in re.split(r"[,\s]+", gold) if norm(t)]
    no = norm(o)
    return all(t in no for t in toks) if toks else (norm(gold) in no)


def extract(out: str) -> str:
    o = out.replace("\b", "")
    m = re.search(r"Answer:\s*(.*?)(?:\[ Prompt:|Exiting|\Z)", o, re.S)
    t = (m.group(1) if m else o).strip()
    return re.sub(r"\s+", " ", t)


def run_one(model: str, prompt: str, n: int, ctx: int) -> str:
    cmd = [LLAMA_CLI, "-m", model, "-p", f"Question: {prompt}\nAnswer:",
           "-n", str(n), "--temp", "0.0", "-t", "8", "-c", str(ctx),
           "-ngl", "0", "--single-turn", "--no-display-prompt"]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
    return extract(p.stdout)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--eval", default="bake_splits/e1046_usable_ast/eval.jsonl")
    ap.add_argument("--out", required=True)
    ap.add_argument("--n-predict", type=int, default=48)
    ap.add_argument("--ctx", type=int, default=512)
    args = ap.parse_args()

    probes = [json.loads(l) for l in open(args.eval, encoding="utf-8")]
    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    agg = defaultdict(lambda: [0, 0])  # key (pool, kind) -> [total, hit]
    with outp.open("w", encoding="utf-8") as f:
        for i, pr in enumerate(probes, 1):
            q = pr["messages"][0]["content"]
            gold = pr["messages"][1]["content"]
            sym = pr["symbol"]
            kind = pr.get("kind", "")
            pool = pr.get("pool", "trained" if sym in TRAINED else "control")
            out = run_one(args.model, q, args.n_predict, args.ctx)
            hit = score_hit(kind, gold, out)
            agg[(pool, kind)][0] += 1
            agg[(pool, kind)][1] += int(hit)
            f.write(json.dumps({"i": i, "symbol": sym, "pool": pool, "kind": kind,
                                "q": q, "gold": gold, "out": out, "hit": hit}) + "\n")
            f.flush()
            if i % 20 == 0:
                print(f"  ...{i}/{len(probes)}")

    print("\n=== hit-rate by pool x kind (hit/total) ===")
    pools = sorted({k[0] for k in agg})
    kinds = ["enum_heldout", "count", "presence_yes", "presence_no"]
    for pool in pools:
        line = [f"{pool:8}"]
        for kind in kinds:
            t, h = agg.get((pool, kind), [0, 0])
            line.append(f"{kind}={h}/{t}")
        print("  " + "  ".join(line))


if __name__ == "__main__":
    main()
