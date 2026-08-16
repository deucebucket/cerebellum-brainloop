"""E1052 — bake FICTIONAL facts the base cannot know (airtight generality test).

The ast testbed could leak through pretraining. Here every entity and every
property is invented, so any correct answer MUST come from the bake, not prior
knowledge. Same proven recipe: use-battery (enum + count + presence) with
list-FIRST grounded answers, exact 1:1 balanced presence, diverse phrasings.
Control = invented entities NEVER trained -> the base has literally no way to
answer (sanity floor near zero). Eval also uses held-out phrasings and a
held-out property per entity.

Deterministic construction (seeded) for reproducibility.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

SEED = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 1337
OUTDIR = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "bake_splits/e1052_fiction"
N_ENTITIES = 80
PROPS_PER = (3, 6)  # min,max invented properties per entity

# invented morpheme pools -> made-up but pronounceable tokens.
# Distinct vocab per --variant so different fiction packs stay router-separable.
_VOCAB = {
    "a": (
        ["zor", "quib", "vel", "thra", "mox", "glan", "drev", "pim", "sork", "yux",
         "wren", "blon", "korr", "fent", "jal", "vusk", "neth", "plox", "grim", "azzo"],
        ["blax", "tine", "dorn", "win", "ackle", "ulth", "ester", "ovic", "arn", "ux",
         "ippet", "ond", "azu", "ilux", "orne", "eppa", "yle", "unth", "addox", "iqua"],
        ["flux", "gantry", "wobble", "sprocket", "lumen", "drak", "quorn", "fizzle",
         "morrin", "tplex", "vane", "girth", "snath", "plume", "rivet", "carom",
         "dwell", "sumph", "nexel", "gorm", "tarn", "veil", "crux", "delve",
         "harn", "obol", "prand", "skarn", "twixt", "umbra", "vorp", "wisk",
         "yarl", "zind", "brel", "chom", "frith", "klin", "murk", "pell"]),
    "c": (
        ["bron", "kael", "thup", "wim", "garr", "olm", "pesk", "vund", "jix", "morn",
         "snell", "drub", "yont", "klar", "fump", "ozic", "rast", "lonn", "ged", "vask"],
        ["wyrm", "thal", "queld", "robb", "iskan", "ompf", "ardle", "ovin", "uxor",
         "ennick", "olby", "askra", "ulmen", "oth", "eppen", "ylar", "undt", "obux",
         "immel", " archt"],
        ["zellar", "brontide", "wuther", "crannog", "fettle", "gloam", "haar", "ingle",
         "kench", "lanch", "mornel", "noust", "ovel", "pingle", "quern", "rample",
         "swale", "thrum", "ushag", "varl", "welk", "yald", "zorse", "cleg", "dwale",
         "ferth", "gribble", "hawse", "jirble", "keld", "lourd", "mawk", "nirl",
         "orts", "pight", "ruck", "sneb", "tath", "urd", "wonk"]),
    "d": (
        ["xan", "frell", "gob", "huln", "ipt", "jorr", "kesh", "lup", "myn", "nokk",
         "opal", "prit", "qual", "rind", "stog", "tuv", "umb", "vill", "wace", "yorn"],
        ["dril", "esh", "fenn", "glop", "hurn", "iket", "jund", "kosp", "lorn", "myx",
         "nash", "ondu", "pely", "quan", "ript", "sond", "tarn", "umph", "vox", "wend"],
        ["aril", "bosk", "crelm", "dunt", "espre", "frot", "garn", "holm", "ivex",
         "jolt", "kreel", "lorn", "mund", "nelp", "ovum", "prax", "queel", "rond",
         "sprat", "tilk", "umbra", "volt", "wisk", "xeno", "yald", "zorb", "crit",
         "delf", "embo", "fisk", "groat", "hesp", "indo", "jannock", "kelter",
         "limn", "morb", "nurl", "ostle", "prog"]),
}
_VARIANT = sys.argv[sys.argv.index("--variant") + 1] if "--variant" in sys.argv else "a"
ENT_A, ENT_B, PROP_POOL = _VOCAB[_VARIANT]


EXCLUDE = set()
if "--exclude" in sys.argv:
    EXCLUDE = set(json.load(open(sys.argv[sys.argv.index("--exclude") + 1])))


def build_entities(rng: random.Random) -> dict[str, list[str]]:
    ents = {}
    names = set(EXCLUDE)  # never reuse an excluded (other-pack) entity name
    while len(ents) < N_ENTITIES:
        nm = rng.choice(ENT_A).capitalize() + rng.choice(ENT_B)
        if nm in names:
            continue
        names.add(nm)
        k = rng.randint(*PROPS_PER)
        props = rng.sample(PROP_POOL, k)
        ents[nm] = props
    return ents


ENUM_TRAIN = [
    "List the properties of {s} in order.", "What properties does {s} have?",
    "Name the properties of {s}.", "Which properties does {s} define?",
    "Give the property names of {s}.", "Enumerate the properties of {s}.",
]
ENUM_EVAL = "In order, what are the properties of {s}?"
COUNT_TRAIN = [
    "How many properties does {s} have?", "Number of properties in {s}?",
    "Count the properties of {s}.", "How many properties are defined on {s}?",
]
COUNT_EVAL = "What is the property count of {s}?"
PRES_TRAIN = ["Does {s} have a {f} property?", "Is {f} a property of {s}?"]
PRES_EVAL = "Is there a {f} property on {s}?"


def msg(q, a, sym, kind, pool):
    return {"messages": [{"role": "user", "content": q},
                         {"role": "assistant", "content": a}],
            "symbol": sym, "kind": kind, "pool": pool}


def grounded(v, sym, fields):
    return f"{sym} has: {', '.join(fields)}. So the answer is {v}."


def main() -> None:
    rng = random.Random(SEED)
    ents = build_entities(rng)
    names = sorted(ents)
    train_syms = [n for i, n in enumerate(names) if i % 4 != 0]
    ctrl_syms = [n for i, n in enumerate(names) if i % 4 == 0]
    vocab = sorted(PROP_POOL)
    out_dir = Path(OUTDIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    train, ev = [], []

    for si, s in enumerate(train_syms):
        fs = ents[s]
        enum_a = ", ".join(fs)
        for p in ENUM_TRAIN:
            train.append(msg(p.format(s=s), enum_a, s, "enum", "train"))
        for p in COUNT_TRAIN:
            train.append(msg(p.format(s=s), str(len(fs)), s, "count", "train"))
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
            fs = ents[s]
            hard_neg = [f for f in vocab if f not in fs]
            ev.append(msg(ENUM_EVAL.format(s=s), ", ".join(fs), s, "enum_heldout", tag))
            ev.append(msg(COUNT_EVAL.format(s=s), str(len(fs)), s, "count", tag))
            ev.append(msg(PRES_EVAL.format(s=s, f=fs[-1]), "Yes", s, "presence_yes", tag))
            held_neg = hard_neg[(si * 11 + 7) % len(hard_neg)]
            ev.append(msg(PRES_EVAL.format(s=s, f=held_neg), "No", s, "presence_no", tag))

    eval_for(train_syms, "trained")
    eval_for(ctrl_syms, "control")

    (out_dir / "train.jsonl").write_text(
        "".join(json.dumps({"messages": r["messages"]}) + "\n" for r in train), encoding="utf-8")
    (out_dir / "eval.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in ev), encoding="utf-8")
    (out_dir / "entities.json").write_text(json.dumps(ents, indent=2) + "\n", encoding="utf-8")
    meta = {"entities": len(ents), "train_symbols": len(train_syms),
            "control_symbols": len(ctrl_syms), "train_rows": len(train),
            "eval_rows": len(ev), "seed": SEED,
            "note": "fully invented entities+properties; base cannot know them; control entities never trained (floor~0)"}
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))
    print("example:", names[0], "->", ents[names[0]])


if __name__ == "__main__":
    main()
