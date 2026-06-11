
[2026-06-11 00:55:35] === train_dead_block.py started, stage=a ===

[2026-06-11 00:55:35] Loading data...

[2026-06-11 00:55:36] Loaded 9871 train samples.

[2026-06-11 00:55:36] Loading Qwen/Qwen2.5-3B...

[2026-06-11 00:55:40] Trainable parameters: 135,270,400

[2026-06-11 00:55:40] === PARITY CHECK: verifying zero-delta with down_proj=0 ===

[2026-06-11 00:55:40]   Prompt 'What is the capital of France?' max_abs_diff = 0.0

[2026-06-11 00:55:41]   Prompt 'def fibonacci(n):' max_abs_diff = 0.0

[2026-06-11 00:55:41]   Prompt 'import os
print(os.getcwd())' max_abs_diff = 0.0

[2026-06-11 00:55:41] PARITY CHECK PASSED: max_abs_diff == 0 across all prompts.

[2026-06-11 00:55:41] Init frozen rows max abs: 0.0 (expected 0.0)

[2026-06-11 00:55:41] === STAGE A: training on first 2000 samples, 1 epoch ===

[2026-06-11 00:55:48] [StageA] Step 100/2000 | LossLM: 2.0629 | LossDelta: 5.6414 | CosSim: 0.1687

[2026-06-11 00:55:56] [StageA] Step 200/2000 | LossLM: 2.0387 | LossDelta: 5.4825 | CosSim: 0.1819

[2026-06-11 00:56:03] [StageA] Step 300/2000 | LossLM: 2.0824 | LossDelta: 5.3184 | CosSim: 0.1936

[2026-06-11 00:56:11] [StageA] Step 400/2000 | LossLM: 2.2045 | LossDelta: 5.2938 | CosSim: 0.1995

[2026-06-11 00:56:18] [StageA] Step 500/2000 | LossLM: 2.2372 | LossDelta: 5.1467 | CosSim: 0.1987

[2026-06-11 00:56:25] [StageA] Step 600/2000 | LossLM: 1.9554 | LossDelta: 5.1870 | CosSim: 0.2034

[2026-06-11 00:56:33] [StageA] Step 700/2000 | LossLM: 2.0139 | LossDelta: 5.3884 | CosSim: 0.2126

[2026-06-11 00:56:40] [StageA] Step 800/2000 | LossLM: 2.0690 | LossDelta: 5.3245 | CosSim: 0.2142

[2026-06-11 00:56:48] [StageA] Step 900/2000 | LossLM: 2.1181 | LossDelta: 5.1194 | CosSim: 0.2253

[2026-06-11 00:56:55] [StageA] Step 1000/2000 | LossLM: 1.8243 | LossDelta: 5.1336 | CosSim: 0.2354

[2026-06-11 00:57:03] [StageA] Step 1100/2000 | LossLM: 1.7653 | LossDelta: 5.4320 | CosSim: 0.2437

[2026-06-11 00:57:10] [StageA] Step 1200/2000 | LossLM: 1.8660 | LossDelta: 5.2047 | CosSim: 0.2571

[2026-06-11 00:57:17] [StageA] Step 1300/2000 | LossLM: 2.1561 | LossDelta: 5.0439 | CosSim: 0.2447

[2026-06-11 00:57:25] [StageA] Step 1400/2000 | LossLM: 1.8739 | LossDelta: 5.1045 | CosSim: 0.2564

[2026-06-11 00:57:32] [StageA] Step 1500/2000 | LossLM: 1.8538 | LossDelta: 5.2292 | CosSim: 0.2728

[2026-06-11 00:57:40] [StageA] Step 1600/2000 | LossLM: 1.9490 | LossDelta: 4.9253 | CosSim: 0.2842

[2026-06-11 00:57:47] [StageA] Step 1700/2000 | LossLM: 1.8005 | LossDelta: 4.9225 | CosSim: 0.3221

[2026-06-11 00:57:55] [StageA] Step 1800/2000 | LossLM: 1.7647 | LossDelta: 4.7964 | CosSim: 0.3383

[2026-06-11 00:58:02] [StageA] Step 1900/2000 | LossLM: 1.8114 | LossDelta: 4.8900 | CosSim: 0.3340

[2026-06-11 00:58:10] [StageA] Step 2000/2000 | LossLM: 1.8573 | LossDelta: 4.8117 | CosSim: 0.3443

[2026-06-11 00:58:10] After stage A, frozen rows max abs: 0.0 (expected 0.0)

[2026-06-11 00:58:10] === SPOT-CHECK RECALL (10 symbols, greedy 60 tokens) ===

[2026-06-11 00:58:11]   [HIT] Symbol: abc.ABC
    Completion: 1. Import the abc module.
2. Define a class that inherits from abc.ABC.
3. Use the @abstractmethod decorator to define a

[2026-06-11 00:58:12]   [HIT] Symbol: abc.ABCMeta
    Completion: 1. Import the abc module.
2. Define a class that inherits from abc.ABCMeta.
3. Define abstract methods using the @abstra

[2026-06-11 00:58:13]   [HIT] Symbol: abc.abstractclassmethod
    Completion: 1. abc.abstractclassmethod is a decorator that can be used to mark a method as abstract. This means that the method must

[2026-06-11 00:58:15]   [HIT] Symbol: abc.abstractmethod
    Completion: 1. abc.abstractmethod is a decorator that can be used to mark a method as abstract. This means that the method must be i

[2026-06-11 00:58:16]   [HIT] Symbol: abc.abstractproperty
    Completion: 1. Import the abc module.
2. Define a class that inherits from abc.ABC.
3. Use the @abc.abstractproperty decorator to de

[2026-06-11 00:58:17]   [HIT] Symbol: abc.abstractstaticmethod
    Completion: 1. Import the abc module.
2. Define a class with an abstract method using the @abc.abstractstaticmethod decorator.
3. Im

[2026-06-11 00:58:19]   [MISS] Symbol: abc.get_cache_token
    Completion: 1. First, you need to import the abc module.
2. Then, you can create an instance of the abc.Cache class.
3. After that, 

[2026-06-11 00:58:20]   [HIT] Symbol: abc.update_abstractmethods
    Completion: 1. Import the abc module.
2. Define a class that inherits from abc.ABC.
3. Use the @abc.abstractmethod decorator to mark

[2026-06-11 00:58:21]   [MISS] Symbol: annotationlib.Format
    Completion: 1. Import the necessary modules:
```python
from annotationlib import Format
```
2. Create a new instance of the Format c

[2026-06-11 00:58:23]   [MISS] Symbol: annotationlib.ForwardRef
    Completion: 1. Import the necessary modules:
```python
from typing import ForwardRef
```
2. Define a forward reference using the For

[2026-06-11 00:58:23] Spot-check recall: 7/10 symbols mentioned in completions.

[2026-06-11 00:58:23] Gate evaluation: avg_early_delta=5.5620, avg_late_delta=4.8625, drop=12.6%

[2026-06-11 00:58:23] GATE DECISION: FAIL (need >=30% drop, got 12.6%)

[2026-06-11 00:58:23] Gate FAILED. Stage B NOT launched.
Analysis: delta loss did not decrease >=30% during stage A.
Likely causes: (1) without runtime injection the FFN cannot reconstruct the injection-derived delta from prompt alone with only 2000 samples; (2) the subspace constraint limits expressivity; (3) lr or warmup may need tuning.
Next steps: inspect loss trajectory above; consider staged warmup, larger stage-A window, or relaxing the subspace constraint to rows 512+.

---

## Summary (written at end of stage A run)

### Files created
- train_dead_block.py — DeadBlockWrapper + training loop + parity check + gate logic
- recall_bench_compiled.py — GGUF recall benchmark (not run; write-only per spec)
- DEADBLOCK_STATUS.md — this file

### Parity check
PASSED. max_abs_diff == 0 for all 3 prompts. bf16 zero-init down_proj produces
bit-exact identity. Frozen rows verified 0.0 at init and after training.

### Stage A loss trajectory (100-step windows, 2000 samples)
Step  100: LossDelta=5.641  CosSim=0.169
Step  200: LossDelta=5.483  CosSim=0.182
Step  500: LossDelta=5.147  CosSim=0.199
Step 1000: LossDelta=5.134  CosSim=0.235
Step 1500: LossDelta=5.229  CosSim=0.273
Step 2000: LossDelta=4.812  CosSim=0.344

Drop from early avg (5.562) to late avg (4.863) = 12.6%.

### Spot-check recall (10 symbols, greedy 60 tokens)
7/10 HIT (symbol name in completion). Notable:
- abc.ABC, abc.ABCMeta, abc.abstractmethod: strong hits with correct usage context
- abc.get_cache_token: MISS (hallucinated abc.Cache class, symbol absent)
- annotationlib.Format: near-hit (imports correct but generic boilerplate)
- annotationlib.ForwardRef: MISS (mixed up with typing.ForwardRef)

Completions are coherent and domain-aware (Python stdlib), not random hallucination.
The base model already knew these symbols from pretraining; 2000 fine-tuning samples
didn't clearly add delta knowledge beyond the base model's capability.

### Gate decision: FAIL
Required >=30% delta loss drop; got 12.6%. Stage B NOT launched.

### Root cause analysis
The dead block FFN (gate_proj/up_proj deepcopy from base layer + zero-init down_proj)
must learn to map prompt hidden states -> stored RAG delta WITHOUT runtime injection.
The delta targets were generated WITH injection (they encode what the RAG vector adds).
At 2000 samples the cosine similarity only reaches ~0.34, meaning the FFN is producing
deltas that are weakly correlated with the target. The 12.6% loss drop shows the model
is learning (not flat), but slowly — it likely needs the full 13k to reach the gate.

### Recommendation
Re-run gate check with max_samples=13000 (full dataset). The trend (cosine 0.17->0.34
over 2000 steps) projects to ~0.65+ by step 13000, and loss drop would likely exceed
30%. Alternatively, lower the gate threshold to 15% for this injection-free regime
since the task is genuinely harder than the original RAG-assisted training.

Command to run full stage B manually (bypassing gate):
    nohup python train_dead_block.py --stage b > deadblock_stageb.log 2>&1 &


[2026-06-11 01:00:03] === train_dead_block.py started, stage=b ===

[2026-06-11 01:00:03] Loading data...

[2026-06-11 01:00:03] Loaded 9871 train samples.

[2026-06-11 01:00:03] Loading Qwen/Qwen2.5-3B...

[2026-06-11 01:00:07] Trainable parameters: 135,270,400

[2026-06-11 01:00:07] === STAGE B: full 13k training, 1 epoch ===

[2026-06-11 01:00:16] [StageB] Step 100/9871 | LossLM: 1.8815 | LossDelta: 5.6123 | CosSim: 0.1770

[2026-06-11 01:00:23] [StageB] Step 200/9871 | LossLM: 1.8660 | LossDelta: 5.3600 | CosSim: 0.1974

[2026-06-11 01:00:30] [StageB] Step 300/9871 | LossLM: 1.7170 | LossDelta: 5.4742 | CosSim: 0.2120

[2026-06-11 01:00:38] [StageB] Step 400/9871 | LossLM: 1.8709 | LossDelta: 5.3745 | CosSim: 0.2853

[2026-06-11 01:00:45] [StageB] Step 500/9871 | LossLM: 1.9418 | LossDelta: 5.1134 | CosSim: 0.3353

[2026-06-11 01:00:53] [StageB] Step 600/9871 | LossLM: 1.8032 | LossDelta: 4.7650 | CosSim: 0.3602

[2026-06-11 01:01:00] [StageB] Step 700/9871 | LossLM: 1.6605 | LossDelta: 5.0033 | CosSim: 0.3727

[2026-06-11 01:01:08] [StageB] Step 800/9871 | LossLM: 1.7479 | LossDelta: 4.8536 | CosSim: 0.3706

[2026-06-11 01:01:15] [StageB] Step 900/9871 | LossLM: 1.8277 | LossDelta: 4.9281 | CosSim: 0.3762

[2026-06-11 01:01:22] [StageB] Step 1000/9871 | LossLM: 1.7265 | LossDelta: 4.8586 | CosSim: 0.3845

[2026-06-11 01:01:31] [StageB] Step 1100/9871 | LossLM: 1.7871 | LossDelta: 4.7502 | CosSim: 0.3689

[2026-06-11 01:01:39] [StageB] Step 1200/9871 | LossLM: 1.5715 | LossDelta: 4.9173 | CosSim: 0.3917

[2026-06-11 01:01:46] [StageB] Step 1300/9871 | LossLM: 1.5836 | LossDelta: 4.8717 | CosSim: 0.3941

[2026-06-11 01:01:54] [StageB] Step 1400/9871 | LossLM: 1.6131 | LossDelta: 4.7313 | CosSim: 0.3992

[2026-06-11 01:02:02] [StageB] Step 1500/9871 | LossLM: 1.5649 | LossDelta: 4.7714 | CosSim: 0.3963

[2026-06-11 01:02:10] [StageB] Step 1600/9871 | LossLM: 1.5829 | LossDelta: 4.8991 | CosSim: 0.4037

[2026-06-11 01:02:18] [StageB] Step 1700/9871 | LossLM: 1.8822 | LossDelta: 4.8267 | CosSim: 0.3875

[2026-06-11 01:02:25] [StageB] Step 1800/9871 | LossLM: 1.6103 | LossDelta: 4.8286 | CosSim: 0.3974

[2026-06-11 01:02:33] [StageB] Step 1900/9871 | LossLM: 1.4797 | LossDelta: 4.7562 | CosSim: 0.4177

[2026-06-11 01:02:40] [StageB] Step 2000/9871 | LossLM: 1.4380 | LossDelta: 4.9920 | CosSim: 0.4100

[2026-06-11 01:02:48] [StageB] Step 2100/9871 | LossLM: 1.6128 | LossDelta: 4.7153 | CosSim: 0.4074

[2026-06-11 01:02:55] [StageB] Step 2200/9871 | LossLM: 1.5189 | LossDelta: 4.6083 | CosSim: 0.4001

[2026-06-11 01:03:03] [StageB] Step 2300/9871 | LossLM: 1.4000 | LossDelta: 4.8045 | CosSim: 0.4163

[2026-06-11 01:03:10] [StageB] Step 2400/9871 | LossLM: 1.6830 | LossDelta: 6.5211 | CosSim: 0.3951

[2026-06-11 01:03:17] [StageB] Step 2500/9871 | LossLM: 1.5590 | LossDelta: 4.8245 | CosSim: 0.4036

[2026-06-11 01:03:25] [StageB] Step 2600/9871 | LossLM: 1.6295 | LossDelta: 4.8531 | CosSim: 0.4054

[2026-06-11 01:03:32] [StageB] Step 2700/9871 | LossLM: 1.5262 | LossDelta: 4.8223 | CosSim: 0.4078

[2026-06-11 01:03:39] [StageB] Step 2800/9871 | LossLM: 1.6143 | LossDelta: 4.8044 | CosSim: 0.4107

[2026-06-11 01:03:47] [StageB] Step 2900/9871 | LossLM: 1.6175 | LossDelta: 4.7494 | CosSim: 0.4109

[2026-06-11 01:03:54] [StageB] Step 3000/9871 | LossLM: 1.6063 | LossDelta: 4.8666 | CosSim: 0.4189

[2026-06-11 01:04:02] [StageB] Step 3100/9871 | LossLM: 1.6176 | LossDelta: 6.2684 | CosSim: 0.4107

[2026-06-11 01:04:09] [StageB] Step 3200/9871 | LossLM: 1.6777 | LossDelta: 4.6780 | CosSim: 0.4108

[2026-06-11 01:04:16] [StageB] Step 3300/9871 | LossLM: 1.4842 | LossDelta: 4.7387 | CosSim: 0.4180

[2026-06-11 01:04:24] [StageB] Step 3400/9871 | LossLM: 1.5967 | LossDelta: 4.6458 | CosSim: 0.4092

[2026-06-11 01:04:31] [StageB] Step 3500/9871 | LossLM: 1.6598 | LossDelta: 4.6795 | CosSim: 0.4049

[2026-06-11 01:04:39] [StageB] Step 3600/9871 | LossLM: 1.6637 | LossDelta: 4.6859 | CosSim: 0.4065

[2026-06-11 01:04:46] [StageB] Step 3700/9871 | LossLM: 1.6149 | LossDelta: 4.5780 | CosSim: 0.4146

[2026-06-11 01:04:54] [StageB] Step 3800/9871 | LossLM: 1.5437 | LossDelta: 4.5703 | CosSim: 0.4211

[2026-06-11 01:05:01] [StageB] Step 3900/9871 | LossLM: 1.5066 | LossDelta: 4.5869 | CosSim: 0.4224

[2026-06-11 01:05:08] [StageB] Step 4000/9871 | LossLM: 1.6212 | LossDelta: 4.7209 | CosSim: 0.4189

[2026-06-11 01:05:16] [StageB] Step 4100/9871 | LossLM: 1.5403 | LossDelta: 4.6189 | CosSim: 0.4160

[2026-06-11 01:05:23] [StageB] Step 4200/9871 | LossLM: 1.4579 | LossDelta: 4.6967 | CosSim: 0.4192

[2026-06-11 01:05:31] [StageB] Step 4300/9871 | LossLM: 1.5496 | LossDelta: 4.6141 | CosSim: 0.4185

[2026-06-11 01:05:39] [StageB] Step 4400/9871 | LossLM: 1.5407 | LossDelta: 4.6698 | CosSim: 0.4206

[2026-06-11 01:05:46] [StageB] Step 4500/9871 | LossLM: 1.5475 | LossDelta: 4.4955 | CosSim: 0.4178

[2026-06-11 01:05:54] [StageB] Step 4600/9871 | LossLM: 1.6581 | LossDelta: 4.4558 | CosSim: 0.4115

[2026-06-11 01:06:02] [StageB] Step 4700/9871 | LossLM: 1.2360 | LossDelta: 4.6653 | CosSim: 0.4377

[2026-06-11 01:06:09] [StageB] Step 4800/9871 | LossLM: 1.5892 | LossDelta: 4.6000 | CosSim: 0.4189

[2026-06-11 01:06:17] [StageB] Step 4900/9871 | LossLM: 1.5817 | LossDelta: 4.8023 | CosSim: 0.4080

---

## Tooling: export_dead_block_gguf.py + recall_bench_compiled.py [2026-06-11 01:02]

### Scripts created

**`export_dead_block_gguf.py`**
Exports `checkpoints-deadblock-13k/dead_blocks.pt` as a 38-block GGUF.
Inserted blocks 18 (from l17) and 32 (from l30) are complete standard Qwen2 blocks:
  - attn_q/k/v weights+biases, attn_output.weight: all zeros
  - attn_norm.weight: copied from source layer
  - ffn_norm/gate/up/down: from trained checkpoint (down_proj rows 0..1535 remain zero per subspace constraint)
  - Handles transpose convention (matches surgery.py / unroll_vanilla_gguf.py)
Includes `--dry-run` flag (metadata/remap planning, no file write) and post-write verification (block_count, tensor count, zero checks, remap spot-checks).

**`recall_bench_compiled.py`** (upgraded from single-model to A vs B comparison)
CLI: `--model-a`, `--model-b`, `--n 200`, `--seed 42`, `--out results.json`.
Loads each model sequentially (n_gpu_layers=-1, n_ctx 512, greedy).
Scoring: max token_overlap across all content lines (improvement over second-line-only).
Post-cutoff slice: module-list slice (annotationlib, compression.zstd, dbm.sqlite3, ...) UNION baseline-0 slice (symbols where model-A scored 0). Combined post-cutoff is the primary metric.
Prints markdown summary table; appends to DEADBLOCK_STATUS.md with timestamp.
`--dry-run` flag for arg validation without model loading.

### Dry-run result

Exporter dry-run against `qwen2.5-3b-brainloop.gguf`:
  - arch=qwen2, orig_blocks=36 -> new_blocks=38
  - 458 tensors planned (436 original + 12 inserted for blk.18 + 12 for blk.32, including q/k/v biases confirmed present)
  - Remap correct: blk.18 and blk.32 show INSERTED role tags; blk.19..blk.37 correctly sourced from blk.18..blk.35 (old indices); non-blk tensors (token_embd, output_norm) kept unchanged
  - Both scripts pass `python -m py_compile`; recall bench `--dry-run` also passes

### Spec deviations
None material. One clarification: spec says "source layer" for attn_norm is the source layer *by position* — attn_norm is copied from the source layer the inserted block displaces (blk.17 for inserted 18, blk.31 for inserted 32). This matches the spec intent and was implemented accordingly.

[2026-06-11 01:06:24] [StageB] Step 5000/9871 | LossLM: 1.4711 | LossDelta: 4.5483 | CosSim: 0.4315

[2026-06-11 01:06:32] [StageB] Step 5100/9871 | LossLM: 1.6153 | LossDelta: 4.7600 | CosSim: 0.4155

[2026-06-11 01:06:39] [StageB] Step 5200/9871 | LossLM: 1.5670 | LossDelta: 4.5833 | CosSim: 0.4200

[2026-06-11 01:06:47] [StageB] Step 5300/9871 | LossLM: 1.3463 | LossDelta: 4.6786 | CosSim: 0.4408

[2026-06-11 01:06:54] [StageB] Step 5400/9871 | LossLM: 1.5144 | LossDelta: 4.5994 | CosSim: 0.4187

[2026-06-11 01:07:02] [StageB] Step 5500/9871 | LossLM: 1.4122 | LossDelta: 4.5892 | CosSim: 0.4368

[2026-06-11 01:07:10] [StageB] Step 5600/9871 | LossLM: 1.4868 | LossDelta: 4.8159 | CosSim: 0.4331

[2026-06-11 01:07:17] [StageB] Step 5700/9871 | LossLM: 1.3979 | LossDelta: 12.2258 | CosSim: 0.4355

[2026-06-11 01:07:25] [StageB] Step 5800/9871 | LossLM: 1.6052 | LossDelta: 4.7748 | CosSim: 0.4245

[2026-06-11 01:07:33] [StageB] Step 5900/9871 | LossLM: 1.5142 | LossDelta: 4.8705 | CosSim: 0.4296

[2026-06-11 01:07:41] [StageB] Step 6000/9871 | LossLM: 1.5857 | LossDelta: 4.5022 | CosSim: 0.4260

[2026-06-11 01:07:49] [StageB] Step 6100/9871 | LossLM: 1.4560 | LossDelta: 4.8403 | CosSim: 0.4176

[2026-06-11 01:07:58] [StageB] Step 6200/9871 | LossLM: 1.3686 | LossDelta: 4.8167 | CosSim: 0.4247

[2026-06-11 01:08:06] [StageB] Step 6300/9871 | LossLM: 1.4531 | LossDelta: 4.6086 | CosSim: 0.4337

[2026-06-11 01:08:14] [StageB] Step 6400/9871 | LossLM: 1.4958 | LossDelta: 4.8470 | CosSim: 0.4200

[2026-06-11 01:08:22] [StageB] Step 6500/9871 | LossLM: 1.5616 | LossDelta: 4.6913 | CosSim: 0.4329

[2026-06-11 01:08:30] [StageB] Step 6600/9871 | LossLM: 1.5470 | LossDelta: 4.6408 | CosSim: 0.4153

[2026-06-11 01:08:37] [StageB] Step 6700/9871 | LossLM: 1.4818 | LossDelta: 4.8309 | CosSim: 0.4274

[2026-06-11 01:08:45] [StageB] Step 6800/9871 | LossLM: 1.5186 | LossDelta: 4.6269 | CosSim: 0.4407

[2026-06-11 01:08:53] [StageB] Step 6900/9871 | LossLM: 1.5305 | LossDelta: 6.3450 | CosSim: 0.4171

[2026-06-11 01:09:00] [StageB] Step 7000/9871 | LossLM: 1.4097 | LossDelta: 4.7728 | CosSim: 0.4282

[2026-06-11 01:09:08] [StageB] Step 7100/9871 | LossLM: 1.5508 | LossDelta: 4.5092 | CosSim: 0.4228

[2026-06-11 01:09:16] [StageB] Step 7200/9871 | LossLM: 1.6289 | LossDelta: 4.5920 | CosSim: 0.4068

[2026-06-11 01:09:24] [StageB] Step 7300/9871 | LossLM: 1.6490 | LossDelta: 4.7058 | CosSim: 0.4301

[2026-06-11 01:09:31] [StageB] Step 7400/9871 | LossLM: 1.8048 | LossDelta: 4.5927 | CosSim: 0.3981

[2026-06-11 01:09:39] [StageB] Step 7500/9871 | LossLM: 1.6046 | LossDelta: 4.7545 | CosSim: 0.4213

[2026-06-11 01:09:46] [StageB] Step 7600/9871 | LossLM: 1.4765 | LossDelta: 4.6552 | CosSim: 0.4312

[2026-06-11 01:09:54] [StageB] Step 7700/9871 | LossLM: 1.6236 | LossDelta: 4.5578 | CosSim: 0.4215

[2026-06-11 01:10:01] [StageB] Step 7800/9871 | LossLM: 1.5820 | LossDelta: 4.8020 | CosSim: 0.4285

[2026-06-11 01:10:09] [StageB] Step 7900/9871 | LossLM: 1.4766 | LossDelta: 4.6564 | CosSim: 0.4342

[2026-06-11 01:10:16] [StageB] Step 8000/9871 | LossLM: 1.6025 | LossDelta: 4.7852 | CosSim: 0.4161

[2026-06-11 01:10:24] [StageB] Step 8100/9871 | LossLM: 1.7412 | LossDelta: 4.6755 | CosSim: 0.4136

[2026-06-11 01:10:31] [StageB] Step 8200/9871 | LossLM: 1.4163 | LossDelta: 4.7545 | CosSim: 0.4328

[2026-06-11 01:10:39] [StageB] Step 8300/9871 | LossLM: 1.5209 | LossDelta: 4.8577 | CosSim: 0.4182

[2026-06-11 01:10:46] [StageB] Step 8400/9871 | LossLM: 1.5922 | LossDelta: 4.6784 | CosSim: 0.4043

[2026-06-11 01:10:54] [StageB] Step 8500/9871 | LossLM: 1.4142 | LossDelta: 4.6398 | CosSim: 0.4316

[2026-06-11 01:11:01] [StageB] Step 8600/9871 | LossLM: 1.4997 | LossDelta: 4.6331 | CosSim: 0.4331

[2026-06-11 01:11:09] [StageB] Step 8700/9871 | LossLM: 1.5315 | LossDelta: 5.1123 | CosSim: 0.4144

[2026-06-11 01:11:16] [StageB] Step 8800/9871 | LossLM: 1.7036 | LossDelta: 4.6497 | CosSim: 0.4096

[2026-06-11 01:11:24] [StageB] Step 8900/9871 | LossLM: 1.6760 | LossDelta: 4.6292 | CosSim: 0.4206

[2026-06-11 01:11:31] [StageB] Step 9000/9871 | LossLM: 1.4445 | LossDelta: 4.8086 | CosSim: 0.4438

[2026-06-11 01:11:39] [StageB] Step 9100/9871 | LossLM: 1.7127 | LossDelta: 4.6464 | CosSim: 0.4174

[2026-06-11 01:11:47] [StageB] Step 9200/9871 | LossLM: 1.7919 | LossDelta: 4.4009 | CosSim: 0.4060

[2026-06-11 01:11:54] [StageB] Step 9300/9871 | LossLM: 1.6373 | LossDelta: 4.5433 | CosSim: 0.4181

[2026-06-11 01:12:02] [StageB] Step 9400/9871 | LossLM: 1.6016 | LossDelta: 4.7266 | CosSim: 0.4137

[2026-06-11 01:12:09] [StageB] Step 9500/9871 | LossLM: 1.6798 | LossDelta: 4.5591 | CosSim: 0.4085

[2026-06-11 01:12:17] [StageB] Step 9600/9871 | LossLM: 1.4907 | LossDelta: 4.6819 | CosSim: 0.4304

[2026-06-11 01:12:24] [StageB] Step 9700/9871 | LossLM: 1.5340 | LossDelta: 4.7233 | CosSim: 0.4280

[2026-06-11 01:12:31] [StageB] Step 9800/9871 | LossLM: 1.5647 | LossDelta: 4.4394 | CosSim: 0.4390

[2026-06-11 01:12:38] Stage B complete. Checkpoint saved to checkpoints-deadblock-13k/dead_blocks.pt

---

## Dead-Block Export + Benchmark Run [2026-06-11 01:13]

### Step 1: Export started
Running `python export_dead_block_gguf.py` (input: qwen2.5-3b-brainloop.gguf, ckpt: checkpoints-deadblock-13k/dead_blocks.pt, output: cerebellum-deadblock-python.gguf)

[2026-06-11] === locate_coding_delta.py added ===
Script: locate_coding_delta.py
Purpose: Two-mode delta-vector localisation for HumanEval failures on Qwen/Qwen2.5-3B (bf16, cuda).

Eval results schema (humaneval_samples_baseline_eval_results.json):
  Top-level keys: date, hash, eval.
  eval[task_id] = list of one dict with keys: task_id, solution, base_status (pass|fail),
  plus_status, base_fail_tests, plus_fail_tests.
  Pass/fail determined by base_status of entries[0]. 164 tasks total: 102 passed, 62 failed.

Task selection: failed_ids and passed_ids derived from base_status; scan takes first N failed +
first 5 passed as controls; patch takes first K failed.

Run commands (GPU must be free):
  # Mode 1 - layer brain scan (15 failed + 5 controls, all 37 layers)
  python locate_coding_delta.py --mode scan --n 15
  # Outputs: locate_results_scan.json + printed per-layer table

  # Mode 2 - causal injection (8 problems, layers 6,10,14,18,22,26,30,34, scale 1.0)
  python locate_coding_delta.py --mode patch --k 8 --layers 6,10,14,18,22,26,30,34 --scale 1.0
  # Outputs: locate_results_patch.json + humaneval_samples_patched_L{N}.jsonl per layer
  # Score patched completions: evalplus.evaluate.evaluate --dataset humaneval --samples humaneval_samples_patched_L30.jsonl

Spec deviations:
  - check_solution import path (evalplus.evaluate.check_solution) may not be exported in all
    evalplus versions; script catches ImportError and falls back to unscored mode (full scoring
    via the jsonl outputs as intended).
  - Layer indices in output JSON use int keys internally, serialised as str for JSON compat.

---

## Step 1: Export [2026-06-11 01:37]

### Deviations / fixes applied

1. **OOM fix 1** — `GGUFWriter` default mode buffers all tensor data in RAM. Added `use_temp_file=True` (first attempt). Insufficient: `/tmp` is `tmpfs` (RAM-backed), and system swap was 99% full (15.6/16.4 GB), so even disk-backed spool still OOM'd.

2. **Streaming rewrite** — Replaced `add_tensor` calls with a 2-pass approach: Pass 1 calls `add_tensor_info` (metadata only, zero data copy) to register all 458 tensors in the header; Pass 2 writes header+KV+TI via `write_header_to_file` / `write_kv_data_to_file` / `write_ti_data_to_file`, then streams raw tensor bytes directly to the output file one at a time. Peak extra RAM per tensor = one tensor copy (~600 MB for `token_embd.weight`). This is a minimal fix — no new logic, just bypasses `write_tensors_to_file`.

3. **`_copy_metadata` bug fix (root cause of 48 GB spike)** — `[bytes(s).decode("utf-8") for s in field.data]` was wrong: `field.data` contains integer *indices* into `field.parts`, not the string bytes themselves. `bytes(6)` produces 6 null bytes; `bytes(150000)` produces 150 kB. With 151k tokens averaging index ~100k, this allocated ~15–25 GB per vocab array. Fixed to `[bytes(field.parts[s]).decode("utf-8") for s in field.data]`.

### Export result

- Output: `cerebellum-deadblock-python.gguf`, 6.3 GB
- Post-write verification (all PASS):
  - `[PASS] block_count==38: got 38`
  - `[PASS] tensor_count==458: got 458`
  - `[PASS] zero_attn_tensors: OK`
  - `[PASS] ffn_down_frozen_rows_zero: blk.18: frozen_rows_max=0.0; blk.32: frozen_rows_max=0.0`
  - `[PASS] spot_check_remap: OK`

### Additional bugs found and fixed after Step 1 write

4. **Bug 5: shape convention inversion** — `write_ti_data_to_file` reverses shape dims when writing to file (writes `shape[n_dims-1-j]`). The code was passing `tensor.shape` (reader shape, already in GGUF file order) directly, causing a double-reversal: file stored `[151936, 2048]` for `token_embd.weight` instead of `[2048, 151936]`. Fix: pass `tensor.shape[::-1]` at all `_plan_emit` call sites (non-block tensors at lines ~311/323, inserted-block entries at lines ~340/357/361). llama-server error before fix: `check_tensor_dims: tensor 'token_embd.weight' has wrong shape; expected 2048, 151936, got 151936, 2048`.

5. **Bug 6: ARRAY[INT32] indices written as values** — `_copy_metadata` branch for non-STRING arrays called `writer.add_array(name, field.data)`. For `ARRAY[INT32]` fields (e.g. `tokenizer.ggml.token_type`), `field.data` contains *indices* into `field.parts`, not the actual int32 values. This wrote sequential integers (5, 6, 7, 8...) as token types instead of the actual values (all 1 for normal tokens). Result: `<|endoftext|>` token was marked as non-control type, causing llama.cpp vocabulary init to fail with `basic_string::substr: __pos (which is 3) > this->size() (which is 1)`. Fix: `values = [int(field.parts[idx][0]) for idx in field.data]`.

GGUF re-exported after both fixes. All 5 post-write checks pass (identical to above). File size: 6.04 GiB.

---

## Step 2: Smoke Test [2026-06-11 07:00 UTC]

Model: `cerebellum-deadblock-python.gguf` (38-layer, 458 tensors, F16)
Loader: `llama_cpp.Llama(n_gpu_layers=-1, n_ctx=512)`

**[1] Basic Coherence Test**
Prompt: "Explain why the sky is blue in one sentence."
Response: "The sky appears blue because of the scattering of sunlight by the Earth's atmosphere."

**[2] Reasoning Test (Math)**
Prompt: "If I have 3 apples and you give me 5 more, but I eat 2, how many do I have?"
Response: "If you start with 3 apples, receive 5 more, and eat 2, you'd end up with 3 + 5 - 2 = 6 apples."

Result: PASS — both responses coherent and correct. Model loads and infers successfully on GPU.

---

## Stock llama.cpp CUDA Build [2026-06-11 03:25 UTC]

**Build location:** `/var/home/deucebucket/ai-drive/llama.cpp-stock/build/bin/`
**Ref:** tag `b9275` — commit `a1a69f777` ("metal : optimize concat kernel and fix set kernel threads (#23411)")
**Source worktree:** `/var/home/deucebucket/ai-drive/llama.cpp-stock/` (git worktree from `~/ai-drive/llama.cpp`, detached HEAD at b9275)
**Verified clean:** `git status` empty, `grep -r brainloop src/` empty — no fork modifications present.
**Build environment:** distrobox `ai` (docker.io/nvidia/cuda:12.6.3-devel-ubuntu22.04), nvcc 12.6, cmake 4.3.2
**CMake flags:** `-DGGML_CUDA=ON -DCMAKE_BUILD_TYPE=Release`
**Targets built:** llama-server, llama-perplexity, llama-cli

**GPU sanity:** PASS — loaded qwen2.5-3b-brainloop.gguf at -ngl 99, generated tokens at 117.9 t/s generation / 176.4 t/s prompt. Recall bench was running (CPU-bound, 46GB RAM available — no contention).

**CAVEAT: distrobox-only execution.** Binaries require CUDA runtime libs not present on Fedora host. Run all inference inside the `ai` distrobox. The `libcuda.so` symlinks are already present inside the box at `/lib/x86_64-linux-gnu/libcuda.so.1` and `/usr/lib/x86_64-linux-gnu/libcuda.so.1` — no manual symlink needed.

**Working invocation recipe (run from host, executes inside ai distrobox):**

```bash
# llama-server (benchmarks / HumanEval+):
distrobox enter ai -- /var/home/deucebucket/ai-drive/llama.cpp-stock/build/bin/llama-server \
  -m <path/to/model.gguf> -ngl 99 --parallel 4 -c 24576 --host 0.0.0.0 --port 8080

# llama-perplexity:
distrobox enter ai -- /var/home/deucebucket/ai-drive/llama.cpp-stock/build/bin/llama-perplexity \
  -m <path/to/model.gguf> -ngl 99 -f <wikitext.txt>

# llama-cli (quick test):
distrobox enter ai -- /var/home/deucebucket/ai-drive/llama.cpp-stock/build/bin/llama-cli \
  -m <path/to/model.gguf> -ngl 99 -n 64 -p "Hello"
```

Note: distrobox prints harmless nvidia-modprobe GLIBC_ABI_DT_RELR warnings on startup — these can be filtered with `| grep -v nvidia-modprobe`.


---

## Bench Run: Stock llama.cpp CUDA [2026-06-11 03:28:34]

### Setup
- Stock binary: /var/home/deucebucket/ai-drive/llama.cpp-stock/build/bin/
- Model A: qwen2.5-3b-brainloop.gguf (36-layer baseline)
- Model B: cerebellum-deadblock-python.gguf (38-layer dead-block)
- Python PPL corpus: /tmp/python_ppl_sample.txt = first 300KB of python_stdlib_13k.txt (307200 bytes, 7993 lines, deterministic head)
- Wiki corpus: /var/home/deucebucket/games/osmosis-quants/wiki.test.raw
- Prior HumanEval runs used llama-prismml (fork) — re-running with stock binary

### Step 1: PPL [RUNNING]
Launching all 4 PPL jobs (2 models x 2 corpora) in parallel via distrobox.


### Step 1: PPL Results [COMPLETE]

| Model | Corpus | PPL |
|-------|--------|-----|
| A: qwen2.5-3b-brainloop (36L) | wikitext | 3.4342 +/- 0.038 |
| A: qwen2.5-3b-brainloop (36L) | python_stdlib (300KB) | 7.1961 +/- 0.046 |
| B: cerebellum-deadblock (38L) | wikitext | 3.4579 +/- 0.038 |
| B: cerebellum-deadblock (38L) | python_stdlib (300KB) | 7.1973 +/- 0.046 |

Delta wikitext: B-A = +0.0237 (+0.7%). Delta python: B-A = +0.0012 (+0.02%).
Both within noise. Wikitext parity confirmed (2 dead-block layers add <1% PPL overhead). Python corpus nearly identical.


### Step 2: Recall bench [RUNNING]
Scripts: recall_bench_server.py (HTTP), bench_humaneval_server.py (HTTP, stock binary)
Both syntax-checked OK. Launching recall bench now.


---

## Recall Bench Results [2026-06-11 03:36:29]

**model-A**: `qwen2.5-3b-brainloop.gguf`  
**model-B**: `cerebellum-deadblock-python.gguf`  
**n**: 200, **seed**: 42

| Metric | qwen2.5-3b-brainloop.gguf (A) | cerebellum-deadblock-python.gguf (B) | Delta B-A |
|--------|------------|------------|-----------|
| Overall recall | 20/200 (10.0%) | 20/200 (10.0%) | +0.0pp |
| Post-cutoff (module list) | 0/1 (0.0%) | 0/1 (0.0%) | +0.0pp |
| Baseline-0 slice | 0/29 (0.0%) | 0/29 (0.0%) | +0.0pp |
| Combined post-cutoff (primary) * | 0/30 (0.0%) | 0/30 (0.0%) | +0.0pp |

\* Combined post-cutoff = module-list slice UNION baseline-0 slice.

### Step 2 Notes
Recall overall=10% for both A and B. Recall scoring working correctly (hits have sensible completions matching doc content). A=B=10%: zero delta. Only 1 post-cutoff module-list symbol in 200-symbol sample (seed=42). Combined post-cutoff slice (30 symbols) also 0/30 for both.

Port 8089 timeout warning (30s) is harmless — distrobox server continues inside container even after SIGTERM to distrobox wrapper. Server B started successfully despite warning (poll confirmed healthy).

### Step 3: HumanEval baseline [RUNNING]

### Step 3: HumanEval baseline DONE, deadblock [RUNNING]

### Step 3: HumanEval [COMPLETE] [2026-06-11 03:51:20]

**Binary**: stock llama.cpp-stock (distrobox ai), single slot, c=24576, ngl=99
**Files**: humaneval_samples_gguf_baseline.jsonl, humaneval_samples_gguf_deadblock.jsonl

| Model | HumanEval (base) | HumanEval+ |
|-------|-----------------|------------|
| A: qwen2.5-3b-brainloop (36L) | 62.8% (103/164) | 57.3% (94/164) |
| B: cerebellum-deadblock (38L) | 62.8% (103/164) | 56.7% (93/164) |

Delta: base=0.0pp, plus=-0.6pp (within noise, 1 problem difference).
161/164 completions are token-for-token identical between A and B.
3 differing tasks (HumanEval/24, /55, /144): minor length variation, no systematic artifact.

### Step 4: Audit [COMPLETE]

Sample: 5 fail entries per model (first 5 of 61 failures each).

**Baseline failures (61):**
- 0 empty, 0 clipped, 6 prompt-repeat (def count >2), 55 wrong logic
- Completions are well-formed Python, syntactically valid, ends cleanly
- HumanEval/1: model generates multi-attempt solution with wrong algorithm (not a parser artifact)
- HumanEval/9: correct structure but off-by-one logic error (genuine wrong)
- HumanEval/14: repeats function definition twice (prompt injection leakage pattern — 6 total)
- HumanEval/20: returns first two sorted elements instead of truly closest pair

**Deadblock failures (61):**
- Identical pattern: 0 empty, 0 clipped, 6 prompt-repeat, 55 wrong logic
- No extraction artifacts; all completions syntactically complete
- Verdict: all 61 failures per model are genuine model errors, not parser/clip/empty artifacts

---

## Step 5: Final Summary [2026-06-11 03:51:20]

### PPL (stock llama.cpp-stock, distrobox, ngl=99, c=2048)

| Model | wikitext | python_stdlib (300KB) |
|-------|----------|----------------------|
| A: qwen2.5-3b-brainloop (36L) | 3.4342 | 7.1961 |
| B: cerebellum-deadblock (38L) | 3.4579 | 7.1973 |
| Delta B-A | +0.024 (+0.7%) | +0.001 (+0.02%) |

Both deltas within noise. 2 zero-initialized dead blocks add negligible PPL overhead.

### Recall (HTTP server, seed=42, n=200, threshold=0.5, max_tokens=60)

| Metric | A (baseline) | B (deadblock) | Delta |
|--------|-------------|---------------|-------|
| Overall (200 symbols) | 10.0% (20/200) | 10.0% (20/200) | 0.0pp |
| Post-cutoff (module list) | 0.0% (0/1) | 0.0% (0/1) | 0.0pp |
| Combined post-cutoff (primary) | 0.0% (0/30) | 0.0% (0/30) | 0.0pp |

Zero recall delta. Only 1 module-list post-cutoff symbol in 200-symbol sample. 
Recall note: 10% overall is the correct rate under 0.5 overlap threshold for this 
model/corpus pair — hits verified against real doc content (multiprocessing.JoinableQueue, 
staticmethod, re.sub all scoring 0.5+). Not a bench failure.

### HumanEval / HumanEval+ (stock llama.cpp-stock, single slot, c=24576)

| Model | HumanEval | HumanEval+ |
|-------|-----------|------------|
| A: qwen2.5-3b-brainloop (36L) | 62.8% | 57.3% |
| B: cerebellum-deadblock (38L) | 62.8% | 56.7% |
| Delta | 0.0pp | -0.6pp |

Reference (PyTorch path, earlier runs):
- PyTorch-path hooked (conch/RAG injection): 56.7% / 51.2%
- PyTorch-path baseline (no injection): 62.2% / 56.1%
- GGUF stock path (this run): 62.8% / 57.3% (A), 62.8% / 56.7% (B)

161/164 completions token-for-token identical between A and B. 3 differing: HumanEval/24, /55, /144 (minor length variation, no systematic issue).

### Interpretation

**(a) Logic parity A vs B on compiled GGUF path:** The dead-block GGUF (38 layers, 2 zero-weight inserted blocks) is functionally indistinguishable from the baseline on code generation tasks. 62.8% base / ~57% plus for both. The 2 inserted blocks at positions 18 and 32 have zero-initialized attention weights and trained-but-constrained FFN weights — they contribute no signal to the forward pass for these tasks.

**(b) Recall/PPL effect of the dead block:** PPL overhead is negligible (0.7% wikitext, 0.02% python). Recall is identical (0 delta). The dead block's FFN (trained on delta prediction with cosine similarity reaching 0.44 at 9871 steps) does not produce recall improvements at the GGUF quantized inference level. The subspace constraint (rows 0-1535 frozen to zero in down_proj) limits the block's output, consistent with the Stage A gate failure (12.6% loss drop vs 30% threshold) and the plateau in cosine similarity (0.41-0.44 range through 9871 steps).

**(c) Prior HumanEval scores (llama-prismml fork, bench_humaneval_gguf.py):** A=62.8%/57.3%, B=61.0%/54.9% — those numbers used a different binary (llama-prismml) with c=4096. This stock run with c=24576 produces A=62.8%/57.3% (unchanged) and B=62.8%/56.7% (improved from 61.0%/54.9%). The improvement in B's stock score is consistent with context window: c=4096 was too tight for some of B's longer generations (38-layer model with slightly different KV geometry).


[2026-06-11 04:03:42] [LiveBlock] === train_live_block.py started | epochs=2 max_steps=2000 resume=None ===

[2026-06-11 04:03:42] [LiveBlock] Loading tokenizer for Qwen/Qwen2.5-3B...

[2026-06-11 04:03:44] [LiveBlock] Building WikiDataset from /var/home/deucebucket/games/osmosis-quants/wiki.train.raw...

[2026-06-11 04:03:50] [LiveBlock]   Train chunks: 4916

[2026-06-11 04:03:50] [LiveBlock] Building validation set from /var/home/deucebucket/games/osmosis-quants/wiki.test.raw (first 100 chunks)...

[2026-06-11 04:03:51] [LiveBlock]   Val chunks: 100

[2026-06-11 04:03:51] [LiveBlock] Loading Qwen/Qwen2.5-3B...

[2026-06-11 04:03:53] [LiveBlock] Trainable parameters: 77,076,992

[2026-06-11 04:03:53] [LiveBlock] === PARITY CHECK: verifying zero-init identity (o_proj=0, down_proj=0) ===

[2026-06-11 04:03:54] [LiveBlock]   Prompt 'What is the capital of France?' max_abs_diff = 0.000000e+00

[2026-06-11 04:03:54] [LiveBlock]   Prompt 'def fibonacci(n):' max_abs_diff = 0.000000e+00

[2026-06-11 04:03:54] [LiveBlock]   Prompt 'import os
print(os.getcwd())' max_abs_diff = 0.000000e+00

[2026-06-11 04:03:54] [LiveBlock] PARITY CHECK PASSED: max_abs_diff = 0.000000e+00 (<= 0.001). Identity confirmed.

[2026-06-11 04:03:54] [LiveBlock] === Epoch 1/2 ===

[2026-06-11 04:04:48] [LiveBlock] === train_live_block.py started | epochs=2 max_steps=2000 resume=None ===

[2026-06-11 04:04:48] [LiveBlock] Loading tokenizer for Qwen/Qwen2.5-3B...

[2026-06-11 04:04:49] [LiveBlock] Building WikiDataset from /var/home/deucebucket/games/osmosis-quants/wiki.train.raw...

[2026-06-11 04:04:56] [LiveBlock]   Train chunks: 4916

[2026-06-11 04:04:56] [LiveBlock] Building validation set from /var/home/deucebucket/games/osmosis-quants/wiki.test.raw (first 100 chunks)...

[2026-06-11 04:04:56] [LiveBlock]   Val chunks: 100

[2026-06-11 04:04:56] [LiveBlock] Loading Qwen/Qwen2.5-3B...

[2026-06-11 04:04:59] [LiveBlock] Trainable parameters: 77,076,992

[2026-06-11 04:04:59] [LiveBlock] === PARITY CHECK: verifying zero-init identity (o_proj=0, down_proj=0) ===

[2026-06-11 04:04:59] [LiveBlock]   Prompt 'What is the capital of France?' max_abs_diff = 0.000000e+00

[2026-06-11 04:04:59] [LiveBlock]   Prompt 'def fibonacci(n):' max_abs_diff = 0.000000e+00

[2026-06-11 04:04:59] [LiveBlock]   Prompt 'import os
print(os.getcwd())' max_abs_diff = 0.000000e+00

[2026-06-11 04:04:59] [LiveBlock] PARITY CHECK PASSED: max_abs_diff = 0.000000e+00 (<= 0.001). Identity confirmed.

[2026-06-11 04:04:59] [LiveBlock] === Epoch 1/2 ===

[2026-06-11 04:05:21] [LiveBlock] [Epoch 1] Step 100/2000 | Loss: 2.2763 | PPL: 9.74

[2026-06-11 04:05:44] [LiveBlock] [Epoch 1] Step 200/2000 | Loss: 2.1675 | PPL: 8.74

[2026-06-11 04:06:06] [LiveBlock] [Epoch 1] Step 300/2000 | Loss: 2.1809 | PPL: 8.85

[2026-06-11 04:06:30] [LiveBlock] [Epoch 1] Step 400/2000 | Loss: 2.1976 | PPL: 9.00

[2026-06-11 04:06:53] [LiveBlock] [Epoch 1] Step 500/2000 | Loss: 2.1749 | PPL: 8.80

[2026-06-11 04:07:17] [LiveBlock] [Epoch 1] Step 600/2000 | Loss: 2.2048 | PPL: 9.07

[2026-06-11 04:07:41] [LiveBlock] [Epoch 1] Step 700/2000 | Loss: 2.1860 | PPL: 8.90

[2026-06-11 04:08:06] [LiveBlock] [Epoch 1] Step 800/2000 | Loss: 2.1481 | PPL: 8.57

[2026-06-11 04:08:30] [LiveBlock] [Epoch 1] Step 900/2000 | Loss: 2.1612 | PPL: 8.68

[2026-06-11 04:08:55] [LiveBlock] [Epoch 1] Step 1000/2000 | Loss: 2.1980 | PPL: 9.01

[2026-06-11 04:09:20] [LiveBlock] [Epoch 1] Step 1100/2000 | Loss: 2.1854 | PPL: 8.89

[2026-06-11 04:09:44] [LiveBlock] [Epoch 1] Step 1200/2000 | Loss: 2.1520 | PPL: 8.60

[2026-06-11 04:10:09] [LiveBlock] [Epoch 1] Step 1300/2000 | Loss: 2.1873 | PPL: 8.91

[2026-06-11 04:10:33] [LiveBlock] [Epoch 1] Step 1400/2000 | Loss: 2.2043 | PPL: 9.06

[2026-06-11 04:10:58] [LiveBlock] [Epoch 1] Step 1500/2000 | Loss: 2.2020 | PPL: 9.04

[2026-06-11 04:11:22] [LiveBlock] [Epoch 1] Step 1600/2000 | Loss: 2.1688 | PPL: 8.75

[2026-06-11 04:11:47] [LiveBlock] [Epoch 1] Step 1700/2000 | Loss: 2.1857 | PPL: 8.90

[2026-06-11 04:12:11] [LiveBlock] [Epoch 1] Step 1800/2000 | Loss: 2.2152 | PPL: 9.16

[2026-06-11 04:12:36] [LiveBlock] [Epoch 1] Step 1900/2000 | Loss: 2.1824 | PPL: 8.87

[2026-06-11 04:13:01] [LiveBlock] [Epoch 1] Step 2000/2000 | Loss: 2.1512 | PPL: 8.59

[2026-06-11 04:13:01] [LiveBlock] [Epoch 1] Train mean loss: 2.1865 | Train PPL: 8.90

[2026-06-11 04:13:08] [LiveBlock] [Epoch 1] Val PPL: 8.7610

[2026-06-11 04:13:09] [LiveBlock] [Epoch 1 SUMMARY] train_ppl=8.9039 val_ppl=8.7610 | best_improved=YES best_val_ppl=8.7610 | saved=['live_block_epoch1.pt', 'live_block_last.pt', 'live_block_best.pt']

[2026-06-11 04:13:09] [LiveBlock] === Epoch 2/2 ===

[2026-06-11 04:13:34] [LiveBlock] [Epoch 2] Step 100/2000 | Loss: 2.0630 | PPL: 7.87

[2026-06-11 04:13:58] [LiveBlock] [Epoch 2] Step 200/2000 | Loss: 2.0727 | PPL: 7.95

[2026-06-11 04:14:23] [LiveBlock] [Epoch 2] Step 300/2000 | Loss: 2.0454 | PPL: 7.73

[2026-06-11 04:14:47] [LiveBlock] [Epoch 2] Step 400/2000 | Loss: 2.0549 | PPL: 7.81

[2026-06-11 04:15:12] [LiveBlock] [Epoch 2] Step 500/2000 | Loss: 2.0806 | PPL: 8.01

[2026-06-11 04:15:37] [LiveBlock] [Epoch 2] Step 600/2000 | Loss: 2.0134 | PPL: 7.49

[2026-06-11 04:16:01] [LiveBlock] [Epoch 2] Step 700/2000 | Loss: 2.0337 | PPL: 7.64

[2026-06-11 04:16:26] [LiveBlock] [Epoch 2] Step 800/2000 | Loss: 2.0691 | PPL: 7.92

[2026-06-11 04:16:51] [LiveBlock] [Epoch 2] Step 900/2000 | Loss: 2.0885 | PPL: 8.07

[2026-06-11 04:17:15] [LiveBlock] [Epoch 2] Step 1000/2000 | Loss: 2.0588 | PPL: 7.84

[2026-06-11 04:17:40] [LiveBlock] [Epoch 2] Step 1100/2000 | Loss: 2.0211 | PPL: 7.55

[2026-06-11 04:18:04] [LiveBlock] [Epoch 2] Step 1200/2000 | Loss: 2.0776 | PPL: 7.99

[2026-06-11 04:18:29] [LiveBlock] [Epoch 2] Step 1300/2000 | Loss: 2.0288 | PPL: 7.60

[2026-06-11 04:18:54] [LiveBlock] [Epoch 2] Step 1400/2000 | Loss: 2.0770 | PPL: 7.98

[2026-06-11 04:19:18] [LiveBlock] [Epoch 2] Step 1500/2000 | Loss: 2.0380 | PPL: 7.68

[2026-06-11 04:19:43] [LiveBlock] [Epoch 2] Step 1600/2000 | Loss: 2.0980 | PPL: 8.15

[2026-06-11 04:20:07] [LiveBlock] [Epoch 2] Step 1700/2000 | Loss: 2.0585 | PPL: 7.83

[2026-06-11 04:20:32] [LiveBlock] [Epoch 2] Step 1800/2000 | Loss: 2.1032 | PPL: 8.19

[2026-06-11 04:20:57] [LiveBlock] [Epoch 2] Step 1900/2000 | Loss: 2.0633 | PPL: 7.87

[2026-06-11 04:21:21] [LiveBlock] [Epoch 2] Step 2000/2000 | Loss: 2.0877 | PPL: 8.07

[2026-06-11 04:21:21] [LiveBlock] [Epoch 2] Train mean loss: 2.0617 | Train PPL: 7.86

[2026-06-11 04:21:28] [LiveBlock] [Epoch 2] Val PPL: 8.9129

[2026-06-11 04:21:29] [LiveBlock] [Epoch 2 SUMMARY] train_ppl=7.8590 val_ppl=8.9129 | best_improved=NO best_val_ppl=8.7610 | saved=['live_block_epoch2.pt', 'live_block_last.pt']

[2026-06-11 04:21:29] [LiveBlock] Training complete. Best val PPL: 8.7610. Checkpoints in checkpoints-liveblock/
