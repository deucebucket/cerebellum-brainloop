"""
make_bake_data.py -- turn the fact bank into bitlora knowledge-SFT rows (HOT tier).
The cold-tier refiner GENERATES deltas on the fly; the hot tier BAKES high-value
facts into the weights so they're always-on. This emits ChatML rows (multi-phrasing
question -> doc body answer) that bitlora bakes into Bonsai -> self-contained GGUF.
Ready to fire once factscale confirms the architecture; bake target = the facts that
earn always-on (promote-by-traffic later).
"""
import json, re
DOCS_TXT="python_stdlib_13k.txt"; OUT="bake_knowledge_sft.jsonl"; SEED=42; N=256
PHRASINGS=["What is {s}?","Explain {s}.","What does {s} do?","Describe {s}.","Tell me about {s}."]
def load_docs():
    docs,cur=[],None
    for ln in open(DOCS_TXT,encoding="utf-8"):
        if ln.startswith("# "):
            if cur: docs.append(cur)
            cur=ln[2:].rstrip()+"\n"
        elif cur is not None: cur+=ln
    if cur: docs.append(cur)
    return docs
import torch
docs=load_docs(); g=torch.Generator().manual_seed(SEED)
idx=torch.randperm(len(docs),generator=g)[:N].tolist()
rows=0
with open(OUT,"w") as f:
    for di in idx:
        d=docs[di]; s=d.split("\n",1)[0].strip()
        body=(d.split("\n",1)[1] if "\n" in d else "").strip()
        if not body: continue
        for p in PHRASINGS:
            msg=[{"role":"user","content":p.format(s=s)},{"role":"assistant","content":body}]
            f.write(json.dumps({"messages":msg})+"\n"); rows+=1
print(f"wrote {rows} bake rows -> {OUT} ({N} facts x {len(PHRASINGS)} phrasings)")
