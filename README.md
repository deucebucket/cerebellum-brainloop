# Cerebellum-Brainloop

Cerebellum-Brainloop implements a dual-stage hidden state interceptor for Qwen2.5-3B. The system uses non-destructive layer wrappers (the base model stays fully frozen) to inject external factual knowledge directly into the model's residual stream.

## Technical Facts

- **Architecture:** Dual refiner wrappers on layers 17 ("Reasoning") and 30 ("Knowledge Gate"), 0-indexed — each refiner is a clone of its wrapped base layer and executes immediately after it (`refiner_vanilla.py`). In the unrolled 38-block GGUF the trained refiners occupy block indices 18 and 32.
- **Subspace Routing:** HID (Hidden Dimension) partitioning ensures that only 25% of dimensions (Dim 1536-2048) are modified, preserving the base model's native logic in the remaining 75%.
- **Zero-Context Injection:** Knowledge is fused via Delta Vectors extracted from "Knowing" vs "Ignorant" model states.
- **Vanilla Compatibility:** GGUF surgery script (`unroll_vanilla_gguf.py`) produces a standard GGUF that runs on stock `llama.cpp` releases without custom C++ forks. Caveat: the exported refiners execute as plain residual blocks — the tanh gate, subspace mask, and RAG injection currently exist only in the PyTorch path. Closing that gap is an open problem (see `EXPERIMENTAL_PATHS.md`).

## Verified Benchmarks (Qwen2.5-3B)

### Logic & Coherence
| Configuration | HumanEval (164-sample) | HumanEval+ (164-sample) | Coherence Test |
|---|---|---|---|
| Qwen2.5-3B Baseline | 62.2% | 56.1% | Pass |
| **Brainloop (Refiners Active)** | **56.7% (-5.5%)** | **51.2% (-4.9%)** | **Pass** |

*Note: While the intercept mechanism prevents catastrophic token looping ("lobotomy"), a full 164-sample evaluation reveals a minor degradation (~5%) in native reasoning capabilities when the identity-prior refiners are active. These scores were measured through the PyTorch interception path; compiled-path (llama.cpp) benchmarks of the unrolled GGUF are pending the weight-baking work described in `EXPERIMENTAL_PATHS.md`.*

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
