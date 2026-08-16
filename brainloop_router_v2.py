"""E1064 — harden the router. Compare feature schemes on the HARDEST routing case:
7 packs incl. the near-identical fiction quartet (fic1-4) + two stdlib packs + ast.

The fiction packs share query structure ("Does X have a Y property?"); the only
signal is the invented entity/property TOKENS. Word TF-IDF underweights rare
novel tokens -> fic confusion. Char n-grams capture the morphology of invented
names, and a word+char union should separate them. Reports per-pack + overall
on held-out-phrasing eval queries.
"""

from __future__ import annotations

import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.pipeline import FeatureUnion

PACKS = {
    "ast": "bake_splits/e1051_ast_battery_v4",
    "fiction1": "bake_splits/e1052_fiction",
    "fiction2": "bake_splits/e1054_fiction2",
    "fiction3": "bake_splits/e1061_fic3",
    "fiction4": "bake_splits/e1062_fic4",
    "stdlib": "bake_splits/e1056_stdlib_recall",
    "stdlib2": "bake_splits/e1060_stdlib2",
}


def load(split):
    X, y = [], []
    for name, d in PACKS.items():
        p = f"{d}/{split}.jsonl"
        if not Path(p).exists():
            continue
        for l in open(p):
            X.append(json.loads(l)["messages"][0]["content"]); y.append(name)
    return X, y


def make_vec(scheme):
    if scheme == "word":
        return TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    if scheme == "char":
        return TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, sublinear_tf=True)
    # word + char union (the hardened scheme)
    return FeatureUnion([
        ("w", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)),
        ("c", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, sublinear_tf=True)),
    ])


def main():
    Xtr, ytr = load("train")
    Xte, yte = load("eval")
    labels = sorted(set(ytr))
    print(f"packs: {len(labels)}  train q: {len(Xtr)}  held-out eval q: {len(Xte)}\n")
    best = None
    for scheme in ["word", "char", "word+char"]:
        vec = make_vec(scheme)
        clf = LogisticRegression(max_iter=3000, C=10.0)
        clf.fit(vec.fit_transform(Xtr), ytr)
        pred = clf.predict(vec.transform(Xte))
        acc = accuracy_score(yte, pred)
        cm = confusion_matrix(yte, pred, labels=labels)
        per = {labels[i]: cm[i][i] / cm[i].sum() for i in range(len(labels))}
        worst = min(per, key=lambda k: per[k])
        print(f"[{scheme:9}] overall {acc*100:5.1f}%   worst pack: {worst} {per[worst]*100:.0f}%")
        if best is None or acc > best[1]:
            best = (scheme, acc, cm, per)
    scheme, acc, cm, per = best
    print(f"\nBEST = {scheme}: {acc*100:.1f}%")
    print("per-pack recall:")
    for k in labels:
        print(f"  {k:9} {per[k]*100:.1f}%")
    print("\nconfusion (rows=true, cols=pred):", labels)
    for i, row in enumerate(cm):
        print(f"  {labels[i]:9}", [int(x) for x in row])
    out = Path("brainloop_runs/e1064_router_hardened/summary.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"best_scheme": scheme, "overall": acc,
                               "per_pack": per, "labels": labels,
                               "confusion": cm.tolist(), "n_packs": len(labels)}, indent=2) + "\n")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
