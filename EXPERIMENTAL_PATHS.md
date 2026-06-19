# RESEARCH PROMPT: Brainloop Speed Bumps & Experimental Paths

**Directive:** Treat all current architectural "blockers" purely as speed bumps. We are looking for unconventional, mathematically sound workarounds to achieve our dual goals: 1) Zero degradation to base reasoning, and 2) 100% Vanilla `llama.cpp` compatibility (no custom C++ required).

## Speed Bump 1: The Vanilla Compatibility Paradox
**Context:** We want to bake our 38-layer unrolled model into a standard GGUF. However, vanilla `llama.cpp` executes standard residual additions (`h = h + layer(h)`). It does not natively support our `tanh` gate or our "Subspace Hijacking" (which restricts modifications to only the last 25% of the hidden dimensions).
**The Question:** How can we mathematically trick a standard transformer architecture into performing Subspace Hijacking and gated identity-priors without altering the C++ inference code?

**Experimental Paths to Explore:**
1. **Weight-Level Subspace Masking:** Instead of using Python/C++ logic to isolate the Knowledge Lane (Dims 1536-2048), can we surgically zero out the top 75% of the rows/columns in the Refiner's `o_proj` (output projection) and `down_proj` matrices? If the weights for the reasoning lanes are literally `0.0`, the standard `h = h + layer(h)` operation will mathematically leave the reasoning lane untouched.
2. **Implicit Gating via Pre-Scaling:** Vanilla `llama.cpp` doesn't have a dynamic gate parameter. Can we emulate a `gate = 0.01` identity prior by statically scaling down the baked weights of the refiner's `o_proj` by `0.01` before GGUF export? Will this allow the network to train with a high learning rate but execute silently in production until triggered?
3. **Norm Shifting:** Does inserting a cloned layer alter the running RMSNorm statistics of the residual stream? Do we need to bake a compensating inverse-norm into the base model's Layer 18 to account for the Refiner's presence?

## Speed Bump 2: The 5% Logic Degradation
**Context:** We fixed the Causal Masking bug by using a perfect `deepcopy` of the `Qwen2DecoderLayer`, but any modification to the residual stream still risks a slight "logic tax" (~5% drop on HumanEval+).
**The Question:** If the architecture is identical, why does an identity-prior clone still degrade logic, and how do we achieve absolute 100% parity before knowledge injection?

**Experimental Paths to Explore:**
1. **True Zero-Init (The Dead Block):** Instead of cloning Layer 17 (Identity Prior), what if we insert a "Dead Block" where `o_proj` and `down_proj` are initialized to absolute zero? A zero-block guarantees 100% logic parity on day one. Can we successfully train a Dead Block to predict Delta Vectors, effectively waking it up only for knowledge retrieval?
2. **Attention Deactivation:** Does the refiner even need Self-Attention? Factual recall has been shown to be predominantly an FFN (Feed-Forward Network) mechanism. What happens if we zero out the `q_proj`, `k_proj`, and `v_proj` in the Refiner, leaving only the SwiGLU FFN to act as a pure associative memory lookup for our Delta Vectors?
3. **Prompt-Conditional Routing:** Can we train the refiner's internal attention heads to act as a router, attending *only* to the specific RAG-injected tokens and ignoring the native context window entirely?

**Execution Mandate:** Do not accept "impossible" as an answer. Design PyTorch scripts to empirically test Weight-Level Subspace Masking and True Zero-Init immediately.

## Roadmap: Vanilla First, Fork Later, Upstream Last

Sequencing for the injection work, in order of dependency:

1. **Now — vanilla dead blocks.** Attention-dead, subspace-masked FFN refiner blocks that are mathematically exact under standard `h = h + layer(h)` execution. No gate approximation, no custom C++. Every published artifact must load and run on stock llama.cpp, and every published number must be measured there (PyTorch-path numbers are iteration-only and labeled as such).
2. **Next — a measured llama.cpp fork for live inline data.** Runtime retrieval injection and per-layer bias wires need engine support. Verified 2026-06-11: vanilla qwen2 in llama.cpp neither loads nor applies optional FFN/attention bias tensors, so there is no code-change-free path today. A fork is the experiment bed, not the product.
3. **Later — upstream.** The qwen2 graph builder already consults `attn_output.bias` if present; only the loader line is missing, and the llama/Granite arch already treats these biases as optional. If the dead-block models prove the use case, a small parity PR to llama.cpp would make bias wires vanilla-legal in future releases. Adoption first, then the ask.

## 2026-06-17 Update: 1-bit Bonsai Fork Path

The local 1-bit Bonsai line now lives directly in the Brainloop project directory (`/var/home/deucebucket/ai-drive/cerebellum/cerebellum-dev/conch-poc`) and tests the same hidden-state write ideas on `Ternary-Bonsai-8B-unpacked`. The Bonsai base model stays on the game drive at `/var/home/deucebucket/games/models/Ternary-Bonsai-8B-unpacked`; only research code, docs, logs, small datasets, and checkpoints belong here. This is a separate mechanism line from the Qwen2.5-3B compiled GGUF work above.

### What Survived

1. **Single-site L33 writes on 1-bit Bonsai.** Static knowing-delta injection at L33 has a clean window: `scale=1.0` gives `recall=0.210`, `drift=0.020`, `degen=0/16`; `scale=1.1` gives `recall=0.212`, `drift=0.021`, `degen=0/16`.
2. **Router/latch.** The trained router head reaches `test_route_acc=0.953` with `neg->null=1.000`, but answer generation needs a latch. Without latch, route_ok was `2/24`; with latch, `24/24`.
3. **Live delta generation.** Refiner v2 moved held-out recall from base `0.061` to `0.222`, beating static held-out delta injection (`0.076`) and matched static injection (`0.171`).
4. **Fact-bank scale evidence.** The best 256-fact run (`bonsai_factscale_256_m2048.log`) reached router `0.977`, full-pipeline recall `0.186`, and code drift `0.000`.
5. **Real QA movement.** The SQuAD gate improved from base `F1=0.126` to injected `F1=0.311`; oracle context is `F1=0.725`, so there is substantial remaining headroom.

### What Failed

1. **Multi-layer static replay.** Simultaneously registering hooks on `late=L18..L35` or `all36=L0..L35` and injecting pre-extracted clean-path deltas is unstable. `late@0.5` and `all36@0.5` both degenerated `16/16`; `all36@0.25` already had `drift=0.975`, `degen=11/16`.
2. **Robust-value router variant.** `bonsai_router_eval_robust.log` kept `route_ok=24/24` but produced no lift (`0.061 -> 0.062`).
3. **Naive generation quality.** `gen_dump_run.log` shows several injected outputs that drift into error text or repetition (`FileNotFoundError`, `XXX to be filled`, traceback-like strings). Numeric overlap improvements are not enough; generation audits remain mandatory.

### Updated Roadmap

1. **Immediate: baked Bonsai GGUF.** Use `bake_knowledge_sft.jsonl` (1,280 rows, 256 facts x 5 phrasings) for BitLoRA/SFT baking. The goal is one self-contained standard GGUF that can be served by stock llama.cpp.
2. **Gate the baked artifact.** Compare baked Bonsai vs plain Bonsai on SQuAD, stdlib symbol recall, code prompts, degeneration checks, and a small coding benchmark. No PyTorch-hook number is publishable by itself.
3. **Then: dynamic matrix lane.** Keep `mtp_hijack_patch.cpp` / runtime matrix writes as a fork-stage experiment. It should read everywhere and write sparingly, using live hidden state, not clean-path static replay.
4. **Do not spend more time on open-loop all-layer delta addition.** The failure is now reproduced in both the old Qwen layer sweep and the Bonsai all-block run.

### Todo Checklist

- [ ] Preserve all `bonsai_*.py`, `run_*after*.sh`, `*.log`, `head_*.pt`, `refiner_*.pt`, and `bake_knowledge_sft.jsonl` before cleanup.
- [ ] Build the baked Bonsai adapter/model from `bake_knowledge_sft.jsonl`.
- [ ] Run compiled-path QA and code gates against the base model.
- [ ] Audit generated answers, not just overlap/F1.
- [ ] Only after a baked win: design the live matrix writer / third-lane runtime path.
