# Cerebellum-Brainloop Results

## Architecture: Multi-Stage Intercept

Cerebellum-Brainloop implements a non-destructive intercept strategy for Qwen2.5 models. 

### Golden Config
- **Intercept Points:** after layer 17 (Reasoning) and layer 30 (Knowledge Gate), 0-indexed — blocks 18 and 32 in the unrolled 38-block GGUF
- **Refinement:** single refiner pass per intercept (the refiner is a clone of the wrapped base layer; revolution loops are legacy — the earlier C++ sweep found 1 revolution optimal, and the vanilla rewrite dropped the loop entirely)
- **Optimizer:** AdamW, LR 1e-4, **Weight Decay 0.1**
- **Gate:** tanh-gated residual (Identity prior at 0.0)

### Coherence & Logic (Qwen2.5-3B)

By utilizing identity-initialized layer wrappers and subspace hijacking, we achieved stable coherence, though with a minor penalty to native logic.

| Configuration | Coherence | HumanEval (164-sample) | HumanEval+ (164-sample) |
|---|---|---|---|
| Qwen2.5-3B Baseline | Pass | 62.2% | 56.1% |
| **Brainloop (Refiners Active)** | **Pass** | **56.7% (-5.5%)** | **51.2% (-4.9%)** |

*Correction (2026-06-11): a forensic audit of the benchmark wiring found the refiners were functionally inert during this measurement — the trained gate values were tanh(gate) ≈ -0.005 (0.5% contribution) and the L17 injection projection had received no gradient updates. The 5.5-point drop is attributable to prompt-format differences between the two bench scripts, not the intervention. The "~5% logic tax" previously reported here was a measurement artifact. Compiled-path benchmarks with verified wiring (see Dead-Block results below) show no measurable logic cost from inserted identity-initialized blocks.*

### Knowledge Recall

Verified recall of 2,002 Python symbols using zero-context vector injection at Layer 31.

| Metric | Baseline | Brainloop |
|---|---|---|
| Symbol Recall Accuracy | ~12% | **94%+** |
| Perplexity (WikiText-2) | 8.5775 | **8.1883 (-4.5%)** |

*PPL was measured on the earlier looped-refiner C++ port (1-revolution sweet spot); the current single-pass vanilla architecture has not been re-measured on WikiText-2.*

---

## Dead-Block Compiled-Path Results (2026-06-11)

First results measured entirely on stock llama.cpp (tag b9275, CUDA): a 38-block GGUF with two attention-dead, subspace-masked FFN refiner blocks (1 epoch, injection-free delta training, final delta cosine ~0.44).

| Metric | Baseline (36L) | Dead-Block (38L) |
|---|---|---|
| HumanEval / HumanEval+ (164, greedy) | 62.8% / 57.3% | 62.8% / 56.7% |
| PPL wikitext (c=2048) | 3.4342 ±0.038 | 3.4579 ±0.038 |
| PPL python-stdlib 300KB | 7.1961 ±0.046 | 7.1973 ±0.046 |
| Symbol recall n=200 / post-cutoff n=30 | 10.0% / 0% | 10.0% / 0% |

Structural parity holds (161/164 HumanEval completions token-identical; no looping). Knowledge injection is not yet effective at this training level — the blocks are functionally inert. Failure audit found no extraction artifacts. PPL values here are not comparable to the legacy protocol above.

---

## Technical Feasibility

- **13k Scaling:** Mathematically verified that 66M parameters can map the 13,529 symbols in the standard library.
- **Vanilla Compatibility:** GGUF surgery script produces a standard GGUF that runs on stock llama.cpp releases. The exported refiners execute as plain residual blocks — the tanh gate, subspace mask, and RAG injection currently exist only in the PyTorch path (open problem, see `EXPERIMENTAL_PATHS.md`).
