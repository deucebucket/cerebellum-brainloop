"""E1051 — list-FIRST grounded presence (fix the decoupled-verdict failure).

E1048 yes-heavy -> yes-bias; E1049 no-heavy -> no-bias. Membership was driven by
the training yes/no RATIO, not real per-symbol checking. Here presence is EXACTLY
1:1 per symbol, and presence_yes is trained on all-but-last field while eval
tests the HELD-OUT last field -> a true test of whether the model uses its
enumerated field knowledge for membership. enum/code/count unchanged (they work).
"""

from __future__ import annotations

import json
from pathlib import Path

from make_ast_usable_bake import ast_node_fields, code_answer  # noqa

ENUM_TRAIN = [
    "List the fields of ast.{s} in order.", "What fields does ast.{s} have?",
    "Name the fields of ast.{s}.", "Which fields does an ast.{s} node define?",
    "Give the field names of ast.{s}.", "Enumerate the fields of ast.{s}.",
]
ENUM_EVAL = "In order, what are the fields of ast.{s}?"
CODE_TRAIN = [
    "Write Python constructing an ast.{s} node with placeholder arguments.",
    "Show how to build an ast.{s} node in Python.",
    "Give code to instantiate ast.{s}.", "How do you create an ast.{s} node in Python?",
]
CODE_EVAL = "Construct an ast.{s} AST node in one line of Python."
COUNT_TRAIN = [
    "How many fields does ast.{s} have?", "Number of fields in ast.{s}?",
    "Count the fields of ast.{s}.", "How many fields are defined on ast.{s}?",
]
COUNT_EVAL = "What is the field count of ast.{s}?"
PRES_TRAIN = ["Does ast.{s} have a {f} field?", "Is {f} a field of ast.{s}?"]
PRES_EVAL = "Is there a {f} field on ast.{s}?"


def msg(q, a, sym, kind, pool):
    return {"messages": [{"role": "user", "content": q},
                         {"role": "assistant", "content": a}],
            "symbol": f"ast.{sym}", "kind": kind, "pool": pool}


def grounded(v, sym, fields):
    # LIST-FIRST: recite the fields, THEN the verdict, so the answer can
    # condition on the enumeration (fixes the E1050 decoupled-verdict failure).
    return f"ast.{sym} has: {', '.join(fields)}. So the answer is {v}."


def main() -> None:
    nodes = ast_node_fields()
    names = sorted(nodes)
    train_syms = [n for i, n in enumerate(names) if i % 4 != 0]
    ctrl_syms = [n for i, n in enumerate(names) if i % 4 == 0]
    vocab = sorted({f for fs in nodes.values() for f in fs})
    out_dir = Path("bake_splits/e1051_ast_battery_v4")
    out_dir.mkdir(parents=True, exist_ok=True)
    train, ev = [], []

    for si, s in enumerate(train_syms):
        fs = nodes[s]
        enum_a = ", ".join(fs)
        for p in ENUM_TRAIN:
            train.append(msg(p.format(s=s), enum_a, s, "enum", "train"))
        for p in CODE_TRAIN:
            train.append(msg(p.format(s=s), code_answer(s, fs), s, "code", "train"))
        for p in COUNT_TRAIN:
            train.append(msg(p.format(s=s), str(len(fs)), s, "count", "train"))
        # presence: balanced. yes on all-but-last field; no on equal # hard negatives.
        yes_fields = fs[:-1] if len(fs) > 1 else fs
        hard_neg = [f for f in vocab if f not in fs]
        n = len(yes_fields)
        no_fields = [hard_neg[(si * 5 + k) % len(hard_neg)] for k in range(n)]
        for f in yes_fields:
            for p in PRES_TRAIN:
                train.append(msg(p.format(s=s, f=f), grounded("Yes", s, fs), s, "presence_yes", "train"))
        for f in no_fields:
            for p in PRES_TRAIN:
                train.append(msg(p.format(s=s, f=f), grounded("No", s, fs), s, "presence_no", "train"))

    def eval_for(syms, tag):
        for si, s in enumerate(syms):
            fs = nodes[s]
            hard_neg = [f for f in vocab if f not in fs]
            ev.append(msg(ENUM_EVAL.format(s=s), ", ".join(fs), s, "enum_heldout", tag))
            ev.append(msg(COUNT_EVAL.format(s=s), str(len(fs)), s, "count", tag))
            ev.append(msg(CODE_EVAL.format(s=s), code_answer(s, fs), s, "code_heldout", tag))
            ev.append(msg(PRES_EVAL.format(s=s, f=fs[-1]), "Yes", s, "presence_yes", tag))  # held-out last field
            held_neg = hard_neg[(si * 11 + 97) % len(hard_neg)]
            ev.append(msg(PRES_EVAL.format(s=s, f=held_neg), "No", s, "presence_no", tag))

    eval_for(train_syms, "trained")
    eval_for(ctrl_syms, "control")

    (out_dir / "train.jsonl").write_text(
        "".join(json.dumps({"messages": r["messages"]}) + "\n" for r in train), encoding="utf-8")
    (out_dir / "eval.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in ev), encoding="utf-8")
    yes_n = sum(1 for r in train if r["kind"] == "presence_yes")
    no_n = sum(1 for r in train if r["kind"] == "presence_no")
    meta = {"train_symbols": len(train_syms), "control_symbols": len(ctrl_syms),
            "train_rows": len(train), "eval_rows": len(ev),
            "presence_yes_rows": yes_n, "presence_no_rows": no_n,
            "change": "EXACT 1:1 balanced presence; yes trained on all-but-last field, eval on held-out last field"}
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
