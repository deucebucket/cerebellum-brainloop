# Brainloop

Brainloop bakes factual knowledge into a frozen, sub-2-bit (ternary) Bonsai-8B base model so that the model recalls **and uses** facts it did not originally know — and then routes and pages many such knowledge packs so the total knowledge stored far exceeds what fits in a single model's weights at once. The output is a standard GGUF that runs on stock `llama.cpp`. No fork, no custom C++.

All headline numbers below are measured on the **compiled path** (stock `llama.cpp`, GGUF, held-out phrasings, audited). Where a result is PyTorch-eager mechanism evidence rather than a compiled-path benchmark, it is labelled as such.

## The result that matters

A knowledge pack baked into the frozen base does not just echo target strings — it answers held-out questions that require *using* the recalled facts (enumerate, count, membership, and combined reasoning). Measured on an AST-node-fields testbed (71 node types, held-out phrasings), baked pack vs. the same base with an untrained control adapter:

| Capability (held-out)            | Baked            | Base / control |
|----------------------------------|------------------|----------------|
| Enumerate fields                 | 42 / 53          | 5 / 18         |
| Count fields                     | 53 / 53          | 7 / 18         |
| Membership (presence yes/no)     | 103 / 106        | 28 / 36        |
| Combined reasoning               | 156 / 159 (98%)  | 35 / 54 (65%)  |

Baking, not pretraining leakage: on a set of fully fictional entities the base cannot have seen, trained reasoning reaches 177 / 180 while the control floor stays at 0 / 20 on enumerate.

On real public benchmarks against the **same-size** base model:

| Benchmark (closed-book)                          | Baked  | Base   | Ratio        |
|--------------------------------------------------|--------|--------|--------------|
| stdlib function-signature recall (300 symbols)   | 61.3%  | 26.7%  | 2.3×         |
| PopQA, 1000 most-obscure long-tail entities      | 58.0%  | 31.2%  | +86% rel.    |

Wrong answers were audited as genuine recall, not parser or clipping artifacts.

## How it works

The working recipe is deliberately fork-free:

1. **Train a LoRA** on the F16-unpacked Bonsai base over knowledge data.
2. **Merge** the LoRA into the base weights.
3. **Convert** the merged model to GGUF.

The merge step is load-bearing. A runtime `--lora` adapter does **not** preserve the learned knowledge through stock `llama.cpp` (0 / 15 on a held-out diagnostic); merging the same adapter into the weights before conversion does. Knowledge lives in the weights, not in a side-loaded adapter.

Four data levers turned brittle recall into usable memory:

- **Scale and diverse phrasings** — write strength matters more than step count; multiple phrasings per fact generalize past the training surface form.
- **A use-shaped question battery** — train the behaviors you want (enumerate / count / membership), not just the fact string.
- **Exact 1:1 balanced presence data** — membership questions must be balanced yes/no, or the model answers from a prior instead of from the fact.
- **List-first grounded answers** — `"X has: a, b, c. So the answer is …"` makes the reasoning condition on the recalled facts rather than guessing.

## Storing more than fits: routing and paging

A single merged model has a finite weight capacity. Two independently-baked packs can be combined by task arithmetic and each retains ~95% of its accuracy. A third pack interferes — exact recall collapses, and TIES merging does not rescue it. Naive merged-storage tops out at roughly **2 packs**.

To scale past that ceiling, Brainloop selects instead of merging:

- **Router** — a tf-idf + logistic-regression router hits **97.1%** over 7 packs. A routed mixed-query system scores **76.7%** vs. base **23.3%** (3.3×).
- **Paged memory controller** — one ~9 GB VRAM hot slot serves a multi-pack cold tier on disk (5 packs ≈ 43.5 GB) at high accuracy. A 2-slot LRU hot-cache roughly halves page-ins under skewed query traffic. This is the "store far more than fits in VRAM" result: a fixed VRAM slot, a learned router, and an LRU pager over disk-resident packs.

## Honest size and limits

The native ternary base is **1.16 GB**. The LoRA-merge step un-ternarizes the merged weights, so a baked pack is larger than the base:

- **~3.3 GB** at Q2 (recall holds at this quant), or
- **~8.7 GB** at Q8.

This is the trade for a fork-free, stock-`llama.cpp` artifact. The path that *would* keep the 1.16 GB base intact is runtime injection via `llama.cpp` control vectors — but tested with static vectors, that gives **no** recall lift (E1067, retired). A genuine runtime-injection path needs a future `llama.cpp` fork with a trained injector; that is the open research frontier, and it is **not built**. Until it is, published knowledge numbers come from the merge-and-bake path above.

Earlier 1-bit injection experiments (static residual-stream writes, latch routing, learned delta refiners on the Bonsai PyTorch hook path) are **mechanism evidence only** — they characterize where writes are easy on the ternary residual stream, but they are not compiled-path results and are not claimed as model performance.

## Reproduce

The tooling is a flat set of scripts; run from the repo root.

- **Bake a pack** — train LoRA, merge, export GGUF: `run_bake_export.sh`, `make_popqa_bake.py`, `make_bake_data.py`.
- **Route across packs** — `brainloop_router.py`, `brainloop_router_v2.py` (hardened char-n-gram router), `brainloop_routed_system.py`.
- **Page across packs** — `brainloop_paged_endpoint.py`, `brainloop_memctl.py` (K-slot LRU hot-cache daemon).
- **Evaluate** — `brainloop_eval_popqa.py` and the per-experiment eval scripts; held-out probe sets under `bake_splits/` and `brainloop_runs/`.

**Proof, not just tables.** Per-item compiled-path dumps (question, gold, raw model `out`, `hit`) for every headline number live in `brainloop_runs/` (E1051–E1068). The held-out probes those dumps were scored against live in `bake_splits/`. `evidence/README.md` maps each README claim to the file that produced it; `evidence/SHA256SUMS` is the integrity list. Weights/GGUFs are not in the repo.

Every run, including failures and killed jobs, is logged start/end with command, params, model/checkpoint paths, and result numbers in **`DEADBLOCK_STATUS.md`** (the append-only operations log). It is the source of truth for every number in this README — the AST testbed, PopQA, stdlib signatures, the 2-pack merge ceiling, the router and paging results, and the runtime-`--lora` vs. merge finding.

## Status

Proven on the compiled path (stock `llama.cpp`):

- Knowledge baked into a frozen ternary base is recalled and used on held-out phrasings, including fully fictional entities the base cannot know.
- Real-benchmark gains over the same-size base (stdlib signatures 2.3×, PopQA +86% relative).
- Merge-then-convert preserves memory where runtime `--lora` does not.
- Naive merged storage caps at ~2 packs; routing (97.1% over 7) and paging (one ~9 GB slot over a 43.5 GB cold tier) scale storage well past one model's capacity.

Open / not yet built:

- **Inline runtime injection.** Keeping the 1.16 GB ternary base and injecting knowledge at runtime would avoid the un-ternarized size cost. Static control-vector injection gives no recall lift; the path forward is a trained injector in a `llama.cpp` fork. Until that exists, do not expect runtime adapters to carry baked memory.

---

### Earlier line: Qwen2.5-3B refiner (archived)

A prior generation explored bolt-on refiner blocks for a frozen Qwen2.5-3B, exported as inserted blocks in a standard 38-block GGUF. The verified compiled-path finding there: plain LM-loss training of an inserted block produced the first knowledge-recall gains through a vanilla GGUF (symbol recall 10.0% → up to 25.5%, including Python 3.14 stdlib symbols postdating the base's training data), and a wikitext-trained variant improved wikitext PPL 8.54 → 7.68 (−10.0%) at its training context. The open cost there was a HumanEval regression on corpus-trained variants. This line is superseded by the Bonsai bake-and-route work above; its full tables live in `RESULTS.md`.
