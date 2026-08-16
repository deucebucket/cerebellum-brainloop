"""E1065 — public-dataset benchmark: PopQA knowledge injection vs base.

PopQA (akariasai/PopQA) is entity-centric factual QA with a deliberate long tail
(low s_pop = obscure entities a small base does not know). We take the most
obscure N facts, BAKE each in declarative + alternative phrasings (NOT the exact
PopQA question), and EVAL on the held-out natural PopQA question, scored
PopQA-style (output contains any gold alias). Baked >> base => baking injected
recallable public-fact knowledge.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

from huggingface_hub import hf_hub_download

N_FACTS = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 1000
OUTDIR = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "bake_splits/e1065_popqa"
SORT_OBSCURE = "--all" not in sys.argv  # --all = use all facts (no obscurity sort/cap)

# bake phrasings: declarative + alt-question forms, deliberately different from the
# PopQA natural question (which is held out for eval).
BAKE_TEMPLATES = [
    "The {prop} of {subj} is {obj}.",
    "{subj} — {prop}: {obj}.",
    "Regarding {subj}, the {prop} is {obj}.",
    "State the {prop} of {subj}.",          # answer = obj
]


def msg(q, a):
    return {"messages": [{"role": "user", "content": q}, {"role": "assistant", "content": a}]}


def main() -> None:
    p = hf_hub_download("akariasai/PopQA", "test.tsv", repo_type="dataset")
    rows = list(csv.DictReader(open(p), delimiter="\t"))
    if SORT_OBSCURE:
        rows.sort(key=lambda x: int(x["s_pop"]))
        rows = rows[:N_FACTS]

    out_dir = Path(OUTDIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    train, ev = [], []
    for r in rows:
        subj, prop, obj = r["subj"], r["prop"], r["obj"]
        aliases = json.loads(r["possible_answers"])
        for t in BAKE_TEMPLATES:
            train.append(msg(t.format(subj=subj, prop=prop, obj=obj), obj))
        # eval = the exact natural PopQA question (held-out surface form)
        ev.append({"messages": [{"role": "user", "content": r["question"]},
                                {"role": "assistant", "content": obj}],
                   "subj": subj, "prop": prop, "gold_aliases": aliases, "s_pop": int(r["s_pop"])})

    (out_dir / "train.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in train), encoding="utf-8")
    (out_dir / "eval.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in ev), encoding="utf-8")
    meta = {"source": "akariasai/PopQA (test.tsv)", "facts": len(rows),
            "train_rows": len(train), "eval_rows": len(ev),
            "selection": "lowest s_pop (most obscure long-tail)",
            "max_s_pop_used": int(rows[-1]["s_pop"]),
            "design": "bake declarative+alt phrasings; eval the exact natural PopQA question; "
                      "score = output contains any gold alias"}
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))
    print("example bake:", train[0]["messages"][0]["content"], "->", train[0]["messages"][1]["content"])
    print("example eval:", ev[0]["messages"][0]["content"], "-> gold", ev[0]["gold_aliases"])


if __name__ == "__main__":
    main()
