# Brainloop Results

Knowledge-baking results for small frozen LLMs. The method takes a base model,
trains a small knowledge "pack" (LoRA), merges it into the base weights, and
converts the result to GGUF. The merged model carries the baked facts as ordinary
weights and runs unmodified on stock `llama.cpp` — no custom C++, no runtime
adapters, no retrieval at inference time.

## Provenance and How to Read This Document

All headline numbers below are **compiled-path** results: the model forward runs
in C/CUDA on stock `llama.cpp`, not in a PyTorch hook. Evaluations use held-out
phrasings (the question wording at test time differs from the wording used to
bake the facts), and wrong/right judgments are audited against the detailed output
before a score is recorded.

Two benchmark types appear:

- **Self-constructed** tasks (AST node-fields, stdlib signatures, fictional
  entities) — built for this project to probe whether baked facts survive a quant
  and a phrasing change. Useful for controlled comparison; not externally
  recognized.
- **PopQA** — a recognized public long-tail QA dataset, used closed-book.

Where a result is **mechanism evidence** (PyTorch hook path, or a diagnostic that
is not a shippable benchmark), it is labeled as such and is not presented as a
model score.

Unless noted, comparisons are same model, same quant (Q8), same size — only the
baked knowledge differs.

---

## 1. Why Merge → GGUF (Mechanism)

Baked memory has to survive the path to a vanilla GGUF. A runtime LoRA does not;
merging the LoRA into the base weights before GGUF conversion does.

| Path | Tiny diagnostic recall |
|---|---|
| Base + runtime `--lora` adapter | 0 / 15 |
| LoRA merged into base, then converted to GGUF (Q8) | 8 / 15 |

The runtime-adapter path drops the baked memory entirely. This is why every
result below uses **merge → GGUF**, never a runtime adapter. (Diagnostic-scale
probe; establishes the pipeline, not a headline score.)

---

## 2. Usable Memory — AST Node-Fields (Self-Constructed)

Held-out phrasings over 71 Python AST node types. "Baked" is the merged GGUF;
"Control" is the same base model with no pack. Tasks exercise different access
patterns over the same baked facts.

| Task | Baked | Control |
|---|---|---|
| Enumerate fields | 42 / 53 | 5 / 18 |
| Count fields | 53 / 53 | 7 / 18 |
| Presence / membership | 103 / 106 | 28 / 36 |
| Combined reasoning | 156 / 159 (98%) | 35 / 54 (65%) |

The baked model answers enumeration, counting, and membership questions about the
structured facts, not just verbatim restatement.

---

## 3. Arbitrary-Knowledge Proof — Fictional Entities (Self-Constructed)

To rule out the base model already knowing the answers, this pack uses fictional
entities the base cannot have seen in pretraining. The control floor confirms the
base has no prior signal.

| Task | Baked (trained reasoning) | Control |
|---|---|---|
| Reasoning over fictional entities | 177 / 180 | — |
| Enumerate (control floor) | — | 0 / 20 |

The base scores zero on enumeration of facts it cannot know; the baked model
reasons over them at 177/180. The gain is the baked knowledge, not recovered
pretraining.

---

## 4. Public Benchmark — Stdlib Function-Signature Recall (Self-Constructed)

300 Python standard-library symbols, held-out question phrasing, same Q8 quant
and model size. Audited.

| Metric | Baked | Base | Ratio |
|---|---|---|---|
| Full-signature recall | 61.3% | 26.7% | 2.3× |
| Token-level recall | 69.1% | 37.1% | — |

Self-constructed task. Measures whether baked signatures survive a phrasing change
on the compiled path.

---

## 5. Public Benchmark — PopQA Closed-Book (Recognized Public Dataset)

1,000 of the most obscure long-tail entities in PopQA, evaluated closed-book on
the **natural question** wording. The bake used declarative and alternate
phrasings — the model never saw the eval phrasing during training.

| Metric | Baked | Base |
|---|---|---|
| Accuracy | 58.0% | 31.2% |
| Relative gain | +86% | — |

299 cases were audited as genuine baked-correct / base-wrong (the baked model
gets them right and the base gets them wrong, confirmed against the detailed
output). PopQA is a recognized public dataset; this is the strongest external
signal in the set.

---

## 6. Composition — Stacking Independent Packs

Packs are baked independently and combined by summing their weight deltas
(task arithmetic). The question is how many packs a single merged model can hold
before exact recall collapses.

| Combination | Result |
|---|---|
| 2 packs (task-arithmetic sum) | ~95% retained each — AST reasoning 151/159, fiction 173/180 in the combined model |
| 3 packs | Interference: exact recall collapses to single digits |
| TIES merge on 3 packs | Does not rescue |

**Merged-storage ceiling ≈ 2 packs.** Beyond that, packs interfere and exact
recall is lost. This motivates routing and paging (sections 7–9) instead of
stuffing everything into one merge.

---

## 7. Router — Selecting the Right Pack

A tf-idf + logistic-regression classifier routes an incoming query to one of 7
baked packs.

| Feature set | Routing accuracy |
|---|---|
| Word features | 92.7% |
| Character n-grams | 97.1% (best) |

The two distinct-vocabulary fiction packs, the AST pack, and the two stdlib packs
route at 100%. Char n-grams handle the symbol-heavy vocabularies better than word
features.

---

## 8. Routed System — End to End (Self-Constructed Mixed Stream)

A mixed 180-query stream is routed to per-pack baked models and answered on the
compiled path.

| System | Accuracy |
|---|---|
| Routed | 76.7% |
| Base (no packs) | 23.3% |

Per-pack breakdown: AST 57/60, fiction 54/60, stdlib 27/60. Routing recovers a
3.3× gain over the base on the same query stream.

---

## 9. Paged Memory Controller

A single resident VRAM slot serves a much larger cold tier of packs on disk,
paging packs in on demand. This keeps the merged-storage ceiling (section 6) from
bounding the total knowledge the system can address.

| Property | Result |
|---|---|
| Resident slot | ~9 GB VRAM |
| Cold tier served | 26 GB (3 packs) → 43.5 GB (5 packs) on disk |
| Tiny-stream accuracy | 96.7% |
| Router accuracy | 100% |

Cache policy under skewed access:

| Policy | Page-ins | Cache-hit rate |
|---|---|---|
| K=2 LRU | 7 | 82% |
| K=1 | 13 | 68% |

K=2 LRU is ~40% faster than K=1 under the skewed access pattern.

---

## 10. Size vs. Recall Across Quants

PopQA-style recall holds as the baked model is quantized down. The base stays flat
at its no-knowledge floor regardless of quant.

| Build | Size | Recall |
|---|---|---|
| Native ternary | 1.16 GB | (see section 11 — injection-only, no lift) |
| Baked Q2 | 3.3 GB | ~54% (200-sample PopQA) |
| Baked Q8 | 8.7 GB | 58% |
| Base (any quant) | — | 31% |

Recall is roughly preserved down to Q2; the baked knowledge is robust to
aggressive quantization. The 1.16 GB native-ternary row is the injection
experiment in section 11, not a baked-pack number.

---

## 11. Negative / Honest Result — Static Injection Has No Lift

Static control-vector injection into the 1.16 GB native-ternary model — adding a
fixed knowledge vector to the residual stream at inference time, with no trained
injector — does **not** improve recall.

| Mode | Recall |
|---|---|
| Base | 14 / 40 |
| Oracle static injection | 13 / 40 |

Oracle injection (best-case, the answer's own vector) lands at or below base. The
inline-injection path needs a **trained injector**, not static vectors. Recorded
here so the merge→GGUF result is not mistaken for an injection result — the
working method is weight baking, not runtime injection.

---

## Summary

- Knowledge bakes into vanilla-`llama.cpp` GGUFs via merge → GGUF. Runtime LoRA
  does not preserve it (section 1).
- On a recognized public dataset (PopQA, long-tail closed-book), baked recall is
  58.0% vs. a 31.2% base — +86% relative, audited (section 5).
- A self-constructed stdlib-signature benchmark shows 2.3× recall at matched quant
  and size (section 4).
- Baked facts support reasoning, not just restatement (sections 2–3), and survive
  down to Q2 (section 10).
- A single merge holds ~2 packs before interference; routing (97.1%) and a paged
  controller extend capacity beyond that ceiling (sections 6–9).
- Static runtime injection does not work without a trained injector (section 11).

All headline numbers are compiled-path on stock `llama.cpp`, held-out phrasing,
audited. Injection numbers are mechanism evidence on the PyTorch / ternary path
and are labeled as such.
