"""E1056 — real stdlib symbol->signature recall benchmark (baked vs base).

Introspects real Python stdlib callables for ground-truth signatures (unique,
specific facts the tiny base does not reliably know). Builds a closed-book recall
SFT with diverse phrasings; holds out one phrasing per symbol for eval so we
measure recall generalization, baked vs plain base, on a real knowledge task.
Connects to the project's headline metric (stdlib symbol recall vs base).
"""

from __future__ import annotations

import importlib
import inspect
import json
import sys
from pathlib import Path

MODULES_A = [
    "os", "os.path", "sys", "json", "re", "math", "random", "collections",
    "itertools", "functools", "shutil", "glob", "textwrap", "string", "base64",
    "hashlib", "datetime", "calendar", "statistics", "bisect", "heapq", "copy",
    "pprint", "csv", "configparser", "argparse", "logging", "subprocess",
    "threading", "queue", "socket", "struct", "zlib", "gzip", "tarfile",
    "zipfile", "pathlib", "tempfile", "urllib.parse", "html", "secrets",
]
MODULES_B = [
    "decimal", "fractions", "uuid", "ipaddress", "enum", "contextlib", "pickle",
    "smtplib", "ftplib", "imaplib", "xmlrpc.client", "wave", "colorsys",
    "difflib", "filecmp", "fnmatch", "getpass", "gettext", "mimetypes",
    "numbers", "operator", "platform", "posixpath", "sched", "selectors",
    "shlex", "signal", "ssl", "stat", "traceback", "types", "unicodedata",
    "warnings", "weakref", "email.utils", "http.client", "sqlite3", "dataclasses",
    "typing", "tokenize", "ast",
]
MODULES = MODULES_B if "--set-b" in sys.argv else MODULES_A
OUTDIR = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "bake_splits/e1056_stdlib_recall"


def sig_of(obj) -> str | None:
    try:
        s = inspect.signature(obj)
    except (ValueError, TypeError):
        return None
    params = [p for p in s.parameters if p not in ("self", "cls")]
    if not params:
        return None
    return ", ".join(params)


def collect() -> dict[str, str]:
    facts = {}
    for modname in MODULES:
        try:
            mod = importlib.import_module(modname)
        except Exception:
            continue
        for name, obj in list(vars(mod).items()):
            if name.startswith("_"):
                continue
            if not (inspect.isfunction(obj) or inspect.isbuiltin(obj) or inspect.isclass(obj)):
                continue
            params = sig_of(obj)
            if params is None:
                continue
            key = f"{modname}.{name}"
            facts[key] = params
    return facts


RECALL_TRAIN = [
    "What are the parameters of {s}?", "List the parameters of {s}.",
    "What arguments does {s} take?", "Give the parameter names of {s}.",
    "Which parameters does {s} accept?",
]
RECALL_EVAL = "In order, what parameters does {s} take?"  # held-out phrasing


def msg(q, a, sym, pool):
    return {"messages": [{"role": "user", "content": q},
                         {"role": "assistant", "content": a}],
            "symbol": sym, "kind": "recall", "pool": pool}


def main() -> None:
    facts = collect()
    syms = sorted(facts)
    # cap for a bounded run; keep specificity
    syms = syms[:300]
    out_dir = Path(OUTDIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    train, ev = [], []
    for s in syms:
        a = facts[s]
        for p in RECALL_TRAIN:
            train.append(msg(p.format(s=s), a, s, "train"))
        ev.append(msg(RECALL_EVAL.format(s=s), a, s, "eval"))
    (out_dir / "train.jsonl").write_text(
        "".join(json.dumps({"messages": r["messages"]}) + "\n" for r in train), encoding="utf-8")
    (out_dir / "eval.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in ev), encoding="utf-8")
    (out_dir / "facts.json").write_text(json.dumps({s: facts[s] for s in syms}, indent=2) + "\n", encoding="utf-8")
    meta = {"symbols": len(syms), "train_rows": len(train), "eval_rows": len(ev),
            "held_out_phrasing": RECALL_EVAL, "modules": MODULES,
            "note": "closed-book stdlib signature recall; eval on held-out phrasing; baked vs base"}
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))
    print("example:", syms[0], "->", facts[syms[0]])


if __name__ == "__main__":
    main()
