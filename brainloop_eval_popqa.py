"""PopQA-style eval against a llama-server: output contains any gold alias.

Reports closed-book accuracy. Use for base vs baked comparison on the held-out
natural PopQA questions.
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def norm(t: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", t.lower())).strip()


def hit(aliases, out):
    o = norm(out)
    for a in aliases:
        na = norm(a)
        if na and na in o:
            return True
    return False


def complete(url, q, n=32):
    body = json.dumps({"prompt": f"Question: {q}\nAnswer:", "temperature": 0.0,
                       "n_predict": n, "stop": ["\n", "Question:"], "cache_prompt": False}).encode()
    req = urllib.request.Request(url + "/completion", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())["content"].strip()
    except Exception:
        return ""  # garbled/bad question -> empty (counts as a miss), don't kill the run


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--eval", default="bake_splits/e1065_popqa/eval.jsonl")
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    probes = [json.loads(l) for l in open(a.eval)]

    def work(p):
        q = p["messages"][0]["content"]
        out = complete(a.url, q)
        return {"q": q, "gold": p["gold_aliases"], "s_pop": p.get("s_pop"),
                "out": out, "hit": hit(p["gold_aliases"], out)}

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        rows = list(ex.map(work, probes))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    n = len(rows); c = sum(r["hit"] for r in rows)
    print(f"PopQA closed-book: {c}/{n} ({100*c/n:.1f}%) -> {a.out}")


if __name__ == "__main__":
    main()
