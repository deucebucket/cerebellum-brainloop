# Brainloop — Open Problems & Roadmap

Brainloop is a research effort to give small, heavily-quantized language models
durable factual memory: knowledge they can recall, count over, and reason about,
not just retrieve from a prompt. The base model stays frozen and ternary (1-bit);
the knowledge is added separately.

This document is the project's map: what is **proven** on the compiled path,
where the **central tension** sits, and the **roadmap** out of it. It is rewritten
to reflect current state, not appended to. The append-only operational record
lives in `DEADBLOCK_STATUS.md`.

A standing rule applies to everything here: **a result counts only if it was
measured on a GGUF running under stock `llama.cpp`.** PyTorch eager-mode numbers
are for iteration and are labeled as such; they are never published as model
results.

---

## What Is Proven

All results in this section were measured on a merged GGUF served by stock
`llama.cpp` (no fork, no custom C++), against a same-size base.

### Baked knowledge packs work, and beat the base 2–3x

A pack is built by fine-tuning a LoRA on a fact set, merging it into the frozen
base, and exporting one self-contained GGUF. The recipe that holds up: scale the
facts, train on diverse phrasings (forces a skill, not Q/A memorization), and use
a "use-shaped" battery — recall **plus** count **plus** membership, not signature
recall alone.

Measured, compiled-path, vs the same-size base:

| Benchmark | Base | Baked pack |
|-----------|------|------------|
| Python stdlib symbol recall (300 facts) | 26.7% | **61.3%** |
| PopQA, 1000 most-obscure long-tail facts (public dataset, closed-book) | 31.2% | **58.0%** |

The PopQA run is a recognized public benchmark, eval'd on the natural question
form (the bake used declarative + alternate phrasings, so the eval form is
held-out). The lift is genuine recall of the exact obscure fact where the base
hallucinates a plausible-wrong answer — audited, not a scoring artifact.

The memory generalizes past recitation: on held-out fields and phrasings the
baked model **counts** (e.g. "how many fields does X have?") and **checks
membership** ("is there a `msg` field on `ast.Assert`?") correctly, grounding the
verdict on the recited facts. This was demonstrated on both real (AST) and fully
**invented** fact sets — the invented set proves the knowledge is baked, not
leaked from pretraining (base recall on invented facts is at the floor).

### Independently-baked packs compose without retraining (up to ~2)

Two packs trained separately from the base combine by **summing their weight
deltas** — seconds of CPU arithmetic, no GPU retrain over the union. Both
knowledge sets survive in one GGUF with only minor degradation (count stays 100%,
reasoning retains ~95–97% of standalone).

This is the "add a pack without retraining everything" property. Its current
limit: naive delta-summing **interferes at 3 packs** — exact recall collapses
first, count is most robust. So additive composition is proven at 2 and is a
density-ceiling problem past that (fixes under Roadmap).

### A learned router + paged cold tier scale knowledge past one model's VRAM

Instead of summing every pack into one model, a learned router picks the relevant
pack per query and a memory controller pages it in. Measured:

- **Router accuracy 0.977**, and 100% on the routed/paged streams.
- A **paged memory controller** serves a knowledge base far larger than VRAM: a
  fixed **~9 GB hot slot answered across a 43.5 GB (5-pack) disk cold tier**.
  A 2-slot LRU hot-cache halves page-ins and cuts wall-time ~40% under skewed
  access. The cold tier grows unbounded with disk; the hot footprint stays fixed.

This is the Cerebellum memory-controller design (VRAM hot / disk cold, LRU
paging, learned router) running as code, not just spec.

---

## The Central Tension

There are two things the project wants at once, and today's stock `llama.cpp`
lets us have only one:

1. **Keep the 1-bit footprint.** The Ternary-Bonsai base is ~1.16 GB.
2. **Get high recall by adding knowledge.**

The problem is *how* knowledge gets added:

- **Merging a LoRA un-ternarizes the base.** Folding adapter deltas into a 1-bit
  base produces full-precision weights that must be re-quantized; the smallest
  honest re-quant is Q2, so a baked pack lands at **~3.3 GB**, not 1.16 GB. The
  recall is real, but the 1-bit footprint is gone. (We accept this for the baked
  product — rank does not change final size, so we maximize capacity at ~3.3 GB.)

- **The footprint-preserving alternative is runtime injection** — feed a retrieved
  fact into a mid-model block at inference and never touch the base weights. But
  stock `llama.cpp`'s only injection primitive is the **static control vector**,
  and tested (E1067), it gave **no recall lift**. A single fixed vector is too
  blunt to write a specific fact into the residual stream.

The deeper reason: **vanilla `llama.cpp` is a closed token→logit pipe.** There is
no port to hand a retrieved fact to a mid-model block at inference. The qwen2
graph builder will consult optional bias tensors if present, but the loader does
not wire them, so there is no code-change-free path to runtime injection today
(verified). A static control vector is the only lever, and it does not carry
enough information.

So: merge gives recall but inflates to Q2; runtime injection preserves 1-bit but,
with the only available primitive, recalls nothing. Closing that gap is the
research frontier.

---

## Roadmap

The strategy is **two products**, sequenced so the first funds adoption for the
second.

### Product 1 — Baked GGUF packs (ships on stock `llama.cpp` today)

The on-ramp. Small, self-contained packs that run on unmodified `llama.cpp`,
plus the router and paged memory controller that let a fixed hot slot serve a
large cold tier. This is proven (above) and needs hardening, not invention.

Near-term experiments, all on the compiled path:

- **Push merged-pack recall with higher LoRA rank.** Rank does not change the
  final GGUF size (merge → Q2), so capacity is free up to the ~3.3 GB budget.
  Maximize recall at that size.
- **Use-shaped training so baked facts are *used*, not just recited.** Keep the
  enum + count + membership battery and list-first grounded answers; verify
  generalization on held-out fields and phrasings.
- **Better packing past 2 packs.** Naive delta-sum interferes at 3. Test
  sign-conflict-aware merges (TIES/DARE), per-pack distinct layers, and routing
  (load the relevant pack instead of summing all).
- **Embedding router for near-duplicate packs.** The current router is strong
  (0.977); harden it where packs are semantically close.
- **Persistent memory-controller daemon.** A 2-slot LRU hot-cache with cold-tier
  paging, kept warm as one endpoint, to amortize page-in cost under real traffic.

### Product 2 — A `llama.cpp` fork with inline RAG (not yet built)

The footprint-preserving endgame, and explicitly **not built**. A trained
**refiner** block that, at inference, queries an index from the current hidden
state and **injects the retrieved fact into the residual stream** — real-time
data plus runtime memorization while the 1-bit base stays untouched.

The fork's missing piece is twofold:

1. **A runtime injection op** in the engine — the port that vanilla `llama.cpp`
   lacks (the closed-pipe problem above). The qwen2 loader would need to wire the
   optional bias/injection tensors the graph builder already tolerates.
2. **A trained injector.** A static control vector is too blunt (E1067: no lift).
   The project's earlier refiner generated better, fact-conditioned deltas — but
   that refiner does **not** reduce to a vanilla `llama.cpp` op, which is exactly
   why a fork is required.

**Gate before building the fork:** prove in PyTorch that a *trained* injector
(not a static vector) lifts recall on held-out facts. Only then is the engine
work justified. The fork is the experiment bed; if the baked packs (Product 1)
prove the use case and the injector clears the gate, a small parity PR to upstream
`llama.cpp` — wiring the already-tolerated optional biases — would make injection
vanilla-legal in future releases. Adoption first, then the upstream ask.

---

## Speed Bumps (closed-pipe consequences)

These are recurring engineering walls, all downstream of the same closed-pipe
constraint. They bound what a vanilla-compatible artifact can express.

### Speed Bump 1 — GGUF export drops the PyTorch-only mechanics

The PyTorch refiner path uses a `tanh` gate, "subspace hijacking" (modifying only
the last 25% of hidden dims), an identity-initialized injection projection, and a
sigmoid scale. **Vanilla `llama.cpp` executes a plain residual add — `h = h +
layer(h)`** — and represents none of these. An exported refiner therefore loses
its gate, subspace mask, and injection wiring; only the raw block survives.

This is the same closed-pipe problem: the engine has no slot for per-layer gating
or a runtime-fed vector. Workarounds that *are* vanilla-legal, because they live
in the weights rather than in inference logic:

- **Weight-level subspace masking** — zero the reasoning-lane rows/columns of the
  refiner's `o_proj`/`down_proj` so the standard residual add leaves those dims
  untouched by construction. (Verified parity: a zero-init `down_proj` "dead
  block" produces bit-exact identity — `max_abs_diff == 0` across probes — and
  adds <1% PPL when spliced in. So a vanilla-legal inserted block is achievable;
  what it cannot do is *runtime* injection.)
- **Implicit gating via pre-scaling** — bake the gate value into the exported
  weights (scale `o_proj` down) instead of applying it at inference.

These let a *static* refiner ship on stock `llama.cpp`. They do not recover the
*runtime* injection that needs the fork.

### Speed Bump 2 — the logic tax of inserting blocks

Any modification to the residual stream risks a small degradation on reasoning
benchmarks (HumanEval+). The mitigation that holds: insert a **true zero-init
dead block** (attention zeroed, `down_proj` zeroed) so day-one parity is exact,
then train only the FFN — factual recall is predominantly an FFN mechanism, so
the attention is optional weight. A dead-block insertion measured at PPL parity
(<1% overhead) and HumanEval+ within noise of the base confirms the approach
costs nothing until it carries knowledge.

---

## Rejected Paths (do not revisit without new evidence)

- **Static control-vector injection at 1-bit** (E1067): no recall lift. A single
  fixed vector cannot write a specific fact. Retired in favor of the baked-pack
  path; the runtime-injection idea moves to the fork with a *trained* injector.
- **Open-loop all-layer static delta addition:** reproduced as a failure in both
  the Qwen layer sweep and the Bonsai all-block run. Registering hooks across many
  layers and adding pre-extracted clean-path deltas degenerates output
  (16/16 degenerate at scale 0.5+). Downstream layers see a perturbed hidden state
  but receive deltas extracted from the unperturbed path — they do not compose.
- **3+ packs by naive delta-sum:** interferes (exact recall collapses). Not a dead
  end — a packing problem; fixes are listed under Product 1. Do not ship a
  naive >2-pack sum.
