"""E1057 — pack router: can a query be routed to the correct knowledge pack?

The merge ceiling (E1054) is the reason to ROUTE instead of merge: keep packs
separate, select the relevant one at inference. Each pack already works
standalone, so the only open question is router accuracy. Train a TF-IDF +
logistic-regression router on each pack's TRAINING queries (label = pack),
test on each pack's HELD-OUT-phrasing eval queries (so the router must
generalize phrasing, and must separate the two structurally-similar fiction
packs whose invented entity names are disjoint).
"""

from __future__ import annotations

import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix

PACKS = {
    "ast": "bake_splits/e1051_ast_battery_v4",
    "fiction1": "bake_splits/e1052_fiction",
    "fiction2": "bake_splits/e1054_fiction2",
    "stdlib": "bake_splits/e1056_stdlib_recall",
}


def load_q(path: str):
    return [json.loads(l)["messages"][0]["content"] for l in open(path, encoding="utf-8")]


def main() -> None:
    Xtr, ytr, Xte, yte = [], [], [], []
    for name, d in PACKS.items():
        for q in load_q(f"{d}/train.jsonl"):
            Xtr.append(q); ytr.append(name)
        for q in load_q(f"{d}/eval.jsonl"):
            Xte.append(q); yte.append(name)

    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    Xtr_v = vec.fit_transform(Xtr)
    clf = LogisticRegression(max_iter=2000, C=10.0)
    clf.fit(Xtr_v, ytr)
    pred = clf.predict(vec.transform(Xte))

    acc = accuracy_score(yte, pred)
    labels = list(PACKS)
    cm = confusion_matrix(yte, pred, labels=labels)
    per = {labels[i]: f"{cm[i][i]}/{cm[i].sum()} ({100*cm[i][i]/cm[i].sum():.1f}%)"
           for i in range(len(labels))}

    print(f"router train queries: {len(Xtr)}  held-out test queries: {len(Xte)}")
    print(f"OVERALL ROUTER ACCURACY: {acc*100:.1f}%  ({sum(p==t for p,t in zip(pred,yte))}/{len(yte)})")
    print("per-pack recall:")
    for k, v in per.items():
        print(f"  {k:9} {v}")
    print("\nconfusion (rows=true, cols=pred):", labels)
    for i, row in enumerate(cm):
        print(f"  {labels[i]:9}", list(row))

    out = Path("brainloop_runs/e1057_router/summary.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "router": "tfidf(1,2)+logreg", "train_queries": len(Xtr),
        "test_queries": len(Xte), "overall_accuracy": acc,
        "per_pack": per, "labels": labels, "confusion": cm.tolist(),
    }, indent=2) + "\n")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
