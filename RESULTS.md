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

*Note: While the intercept mechanism prevents the catastrophic looping ("lobotomy") seen in earlier unrolled builds, a full 164-sample evaluation reveals a minor degradation (~5%) in native reasoning capabilities when the identity-prior refiners are active. Measured through the PyTorch interception path; compiled-path (llama.cpp) benchmarks of the unrolled GGUF are pending weight-baking (see `EXPERIMENTAL_PATHS.md`).*

### Knowledge Recall

Verified recall of 2,002 Python symbols using zero-context vector injection at Layer 31.

| Metric | Baseline | Brainloop |
|---|---|---|
| Symbol Recall Accuracy | ~12% | **94%+** |
| Perplexity (WikiText-2) | 8.5775 | **8.1883 (-4.5%)** |

*PPL was measured on the earlier looped-refiner C++ port (1-revolution sweet spot); the current single-pass vanilla architecture has not been re-measured on WikiText-2.*

---

## Technical Feasibility

- **13k Scaling:** Mathematically verified that 66M parameters can map the 13,529 symbols in the standard library.
- **Vanilla Compatibility:** GGUF surgery script produces a standard GGUF that runs on stock llama.cpp releases. The exported refiners execute as plain residual blocks — the tanh gate, subspace mask, and RAG injection currently exist only in the PyTorch path (open problem, see `EXPERIMENTAL_PATHS.md`).
