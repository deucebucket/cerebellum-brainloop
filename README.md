# Cerebellum-Brainloop

Cerebellum-Brainloop implements a dual-stage hidden state interceptor for Qwen2.5-3B. The system uses non-destructive layer wrappers (the base model stays fully frozen) to inject external factual knowledge directly into the model's residual stream.

## Technical Facts

- **Architecture:** Dual refiner wrappers on layers 17 ("Reasoning") and 30 ("Knowledge Gate"), 0-indexed — each refiner is a clone of its wrapped base layer and executes immediately after it (`refiner_vanilla.py`). In the unrolled 38-block GGUF the trained refiners occupy block indices 18 and 32.
- **Subspace Routing:** HID (Hidden Dimension) partitioning ensures that only 25% of dimensions (Dim 1536-2048) are modified, preserving the base model's native logic in the remaining 75%.
- **Zero-Context Injection:** Knowledge is fused via Delta Vectors extracted from "Knowing" vs "Ignorant" model states.
- **Vanilla Compatibility:** GGUF surgery script (`unroll_vanilla_gguf.py`) produces a standard GGUF that runs on stock `llama.cpp` releases without custom C++ forks. Caveat: the exported refiners execute as plain residual blocks — the tanh gate, subspace mask, and RAG injection currently exist only in the PyTorch path. Closing that gap is an open problem (see `EXPERIMENTAL_PATHS.md`).

## Current Local Fork: Brainloop on 1-bit Bonsai (2026-06-17)

This Brainloop project now contains the local research line for **Ternary-Bonsai-8B** directly in this directory:

`/var/home/deucebucket/ai-drive/cerebellum/cerebellum-dev/conch-poc`

The Bonsai base model remains on the game drive at `/var/home/deucebucket/games/models/Ternary-Bonsai-8B-unpacked`; do not copy large model files into the project. The 1-bit Brainloop work is **mechanism evidence only** until it is baked into a GGUF and benchmarked on the compiled path. The active files are local working-tree artifacts: `bonsai_*.py`, `run_*after*.sh`, `bake_knowledge_sft.jsonl`, `head_*.pt`, `refiner_*.pt`, and matching logs.

Latest local findings:

- Static L33 residual injection on Bonsai is cleaner than the earlier fp16 Qwen line. `bonsai_inject_sweep.log` found best single-layer overlap at `L33`: `recall_overlap=0.210`, `code_drift=0.020`, `degen=0/16`; the fp16-Qwen reference max was `0.149`.
- Scale tuning shows a narrow window. `bonsai_knee_test.log`: `L33 scale=1.1` reached `recall=0.212`, `drift=0.021`, `degen=0/16`; higher scales start drifting and degenerating.
- A trained router works as a selector. `bonsai_train_router.log`: held-out `test_route_acc=0.953`, `neg->null=1.000`. The latch variant is required for generation; per-token gating dropped mid-answer.
- A generated refiner beats static held-out deltas. `bonsai_train_refiner_v2.log`: held-out base `0.061` -> refiner `0.222`; static held-out was `0.076`, matched static was `0.171`.
- Scaling to 256 facts is mixed. `bonsai_factscale_256_m2048.log`: router `0.977`, `neg->null=1.000`; recall `base=0.061`, `oracle_refiner=0.186`, `full_pipeline=0.186`; code drift `0.000`.
- Real QA moved but is not ship-grade. `squad_qa_gate.log`: base `EM=0.033`, `contains=0.233`, `F1=0.126`; injected `EM=0.142`, `contains=0.492`, `F1=0.311`; oracle `F1=0.725`.
- Multi-layer static replay failed. `bonsai_allblock_inject.log`: `late@0.25` already had `degen=3/16`, and `late@0.5`, `late@1.0`, `all36@0.5`, `all36@1.0` all had `degen=16/16`. Clean-path per-layer deltas do not compose once earlier hooks perturb the stream.

Baked-path progress (2026-06-19): the compiled-recall problem narrowed to a
single mechanism finding. A runtime `--lora` adapter does **not** preserve
learned answers through stock llama.cpp — `0/15` exact on a small held-out QA
overfit diagnostic — but **merging** the adapter into the base weights and
converting the merged model to GGUF does: the merged BF16 GGUF recalls `7/15`
and a Q8_0 quant `8/15`, both with no degeneration, versus the unmerged
adapter's `0/15`. The HF checkpoint the GGUF is converted from recalls `15/15`,
so the residual gap is conversion/quantization fidelity, not training.

This is still a small overfit diagnostic, not a product. The next gate is to
show the baked Q8_0 GGUF *uses* the memory beyond echoing the exact target
string — paraphrase, reasoning, and coding-use probes, with controls for
symbols that failed to bake — measured on the compiled path against the plain
base, before any wider bake training. Detailed run logs stay local under the
project's research notes.

## Verified Benchmarks (Qwen2.5-3B)

### Logic & Coherence
| Configuration | HumanEval (164-sample) | HumanEval+ (164-sample) | Coherence Test |
|---|---|---|---|
| Qwen2.5-3B Baseline | 62.2% | 56.1% | Pass |
| **Brainloop (Refiners Active)** | **56.7% (-5.5%)** | **51.2% (-4.9%)** | **Pass** |

*Correction (2026-06-11): a benchmark-wiring audit found the refiners were functionally inert during this run (trained gate ≈ 0.5% contribution; injection projection untrained). The 5.5-point gap reflects prompt-format differences between bench scripts, not the intervention — the previously reported "~5% logic tax" was a measurement artifact. Verified compiled-path results (below) show no measurable logic cost from inserted identity-initialized blocks.*

### Compiled-Path Results — Dead-Block GGUF (2026-06-11)

First benchmark set measured on stock llama.cpp (tag b9275, CUDA, RTX 3090) — no fork, no Python interception. Model: `cerebellum-deadblock-python.gguf`, a 38-block GGUF with two attention-dead, subspace-masked FFN refiner blocks (trained 1 epoch, injection-free delta prediction, final delta cosine ~0.44).

| Metric | Baseline (36L) | Dead-Block (38L) |
|---|---|---|
| HumanEval pass@1 (164, greedy) | 62.8% | 62.8% |
| HumanEval+ pass@1 | 57.3% | 56.7% |
| PPL wikitext (c=2048) | 7.1961 ±0.046 | 7.1973 ±0.046 |
| PPL python-stdlib 300KB (c=2048) | 3.4342 ±0.038 | 3.4579 ±0.038 |
| Symbol recall (n=200, content overlap ≥0.5) | 10.0% | 10.0% |
| Post-cutoff symbol recall (n=30) | 0% | 0% |

What this shows, stated plainly:
- **Structural parity holds on the compiled path.** Inserting the two trained blocks costs no measurable logic or perplexity (161/164 HumanEval completions are token-identical to baseline). The earlier unrolled builds' catastrophic looping does not occur.
- **Knowledge injection is not yet effective** in this delta-trained configuration — the blocks are functionally inert.
- Failure audit: all sampled wrong answers were genuine model errors, no extraction artifacts.
- These PPL values are not comparable to the legacy table below (different eval protocol).

### LM-Trained Insertion Blocks — Verified Recall Through a Vanilla GGUF (2026-06-11)

Replacing delta-prediction with plain LM-loss training of the inserted block produced the first verified knowledge-recall gains on the compiled path (full tables and methodology notes in `RESULTS.md`):

- Symbol recall 10.0% → up to 25.5% (n=200, wiring-verified A/B harness), including recall of **Python 3.14 stdlib symbols that postdate the base model's training data** — content the frozen base model cannot know, surfaced with zero context tokens.
- A wikitext-trained variant of the same block improves wikitext PPL **8.54 → 7.68 (-10.0%)** at its training context on stock llama.cpp.
- Current cost, not yet controlled: corpus-trained variants regress HumanEval; a 25%-subspace write mask and reduced learning rate measurably bound the behavioral damage (best so far: 55.5% vs 62.8% baseline at lr 2e-5). Long-context PPL holds at baseline across all variants. Retaining recall while holding HumanEval at baseline is the open problem and active work.

Correction (2026-06-11): the dead-block table's wikitext and python PPL values were originally published swapped — the measurement session ran its four perplexity jobs in parallel and crossed the corpus labels. The values above are corrected; an identity-block control re-measured both baselines and confirmed the parity conclusion is unchanged.

### Perplexity (WikiText-2)
| Milestone | PPL | Improvement |
|---|---|---|
| Baseline | 8.5775 | — |
| **Brainloop (1 Revolution)** | **8.1883** | **-4.5%** |

*Note: PPL numbers were measured on the earlier looped-refiner C++ port (revolution sweep found 1 revolution optimal). The current vanilla-compatible architecture uses a single refiner pass with no revolution loop and has not been re-measured on WikiText-2.*

### Knowledge Recall
- **Status:** Verified recall of 2,002 Python symbols using zero-context vector injection.
- **Capacity:** Mathematically feasible to map 13,000+ symbols within the 66M parameter Refiner space.

## Implementation Status

- [x] **Subspace Routing:** 100% functional.
- [x] **Layer-Wrapper Patching:** 100% functional.
- [x] **GGUF Unrolling:** Verified metadata surgery for 38-layer unrolls.
- [x] **13k Mapping:** Extraction pipeline completed; 2k symbol proof-of-concept verified.
- [x] **13k Full Training:** Supervised delta-alignment over the full stdlib corpus completed (2026-06-11). Checkpoint (`fused_refiners.pt`), RAG index, and benchmark outputs published to the `deucebucket/cerebellum-brainloop` HF dataset. HumanEval+ with 13k RAG active: 51.2% — identical to the no-RAG hooked score, i.e. live retrieval adds no further logic degradation.
- [ ] **13k Recall Verification:** Symbol-recall accuracy at full 13k scale not yet measured (the 94%+ figure is from the 2,002-symbol POC).
- [ ] **Bonsai baked artifact:** 1-bit Bonsai hook-path results are documented locally, but no claim is publishable until the knowledge is baked into weights and measured through stock llama.cpp.

## Usage

### PyTorch Intervention
```python
from refiner_vanilla import patch_model_vanilla
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-3B")
model = patch_model_vanilla(model) # Identity-prior initialization
```

### GGUF Creation
```bash
python unroll_vanilla_gguf.py --input qwen2.5-3b.gguf --output cerebellum-brainloop-python.gguf
```
