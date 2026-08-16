# Evidence

Per-item compiled-path dumps that back the numbers in `README.md` and
`RESULTS.md`. Each score below was recounted from the listed file at publish
time (2026-08-16). Weights and GGUFs are **not** in this repo.

The lab notebook those tables were copied from is `DEADBLOCK_STATUS.md`.
This directory is the map from a claim to the file a third party can inspect.

How to read a dump: one JSON object per line, `hit: true/false`, plus the
question, gold answer, and the model's raw `out`. Summaries are small JSON
score files next to the per-item traces.

## Headline claims

| Claim | Recounted from the dump | File |
|---|---|---|
| AST usable memory (enum 42/53, count 53/53, presence 103/106, reasoning 156/159) | trained enum 42/53, count 53/53, presence_yes 50/53, presence_no 53/53 | `../brainloop_runs/e1051_battery_v4_eval/baked_q8.jsonl` + `milestone_summary.json` |
| Fictional entities (trained reasoning 177/180; control enum 0/20) | trained count 60/60 + presence 58/60 + 59/60 = 177/180; control enum 0/20 | `../brainloop_runs/e1052_fiction_eval/baked_q8.jsonl` |
| 2-pack task-arithmetic compose (~95% retained) | `e1053_combined_eval/{ast,fiction}.jsonl` | `../brainloop_runs/e1053_combined_eval/` |
| 3-pack naive merge interferes | `e1054_3pack_eval/{ast,fic1,fic2}.jsonl` | `../brainloop_runs/e1054_3pack_eval/` |
| TIES does not rescue 3-pack | `e1055_ties_eval/{ast,fic1,fic2}.jsonl` | `../brainloop_runs/e1055_ties_eval/` |
| Stdlib signatures 61.3% vs 26.7% | baked 184/300, base 80/300 | `../brainloop_runs/e1056_stdlib_eval/{baked,base}.jsonl` |
| Router 93.7% over 4 packs | `overall_accuracy` 0.9367 (1213/1295) | `../brainloop_runs/e1057_router/summary.json` |
| Routed system 76.7% vs base 23.3% | 138/180 vs 42/180 | `../brainloop_runs/e1058_routed_system/{report.json,results.jsonl}` |
| Paged controller 96.7% on 26 GB cold tier | 29/30, page-ins 30, hot 8.7 GB, cold 26.1 GB | `../brainloop_runs/e1059_paged_endpoint/results.json` |
| 5-pack / 43.5 GB cold tier; K=2 LRU halves page-ins | K=2 skew: acc 0.875, page-ins 7, hit 0.825 | `../brainloop_runs/e1063_memctl_k{1,2}_{blocks,skew}/results.json` |
| Hardened router 97.1% over 7 packs | `overall` 0.9714; fic3/fic4/ast/stdlib 100% | `../brainloop_runs/e1064_router_hardened/summary.json` |
| PopQA 58.0% vs 31.2% (1000 obscure, closed-book) | baked 580/1000, base 312/1000 | `../brainloop_runs/e1065_popqa_eval/{baked,base}.jsonl` |
| Q2 200-sample PopQA check | `baked_q2_200.jsonl` | `../brainloop_runs/e1065_popqa_eval/baked_q2_200.jsonl` |
| Full-14k PopQA @ Q2: 23.7% vs 17.0%; obscure tail 38.7% vs 31.2% | 3377/14267 vs 2422/14267; 387/1000 vs 312/1000 | `../brainloop_runs/e1068_eval_{baked,base}_{q2,full14k}.json` (JSONL despite `.json`) |

## Held-out probes used to produce those dumps

Training rows plus the held-out eval questions. Re-run the eval scripts against
a served GGUF to regenerate the dumps.

| Experiment | Probe set |
|---|---|
| E1051 AST battery | `../bake_splits/e1051_ast_battery_v4/` |
| E1052 fiction | `../bake_splits/e1052_fiction/` |
| E1054 fiction set 2 | `../bake_splits/e1054_fiction2/` |
| E1056 stdlib signatures | `../bake_splits/e1056_stdlib_recall/` |
| E1060 stdlib set 2 | `../bake_splits/e1060_stdlib2/` |
| E1061 / E1062 fiction 3–4 | `../bake_splits/e1061_fic3/`, `../bake_splits/e1062_fic4/` |
| E1065 PopQA 1k obscure | `../bake_splits/e1065_popqa/` |
| E1066 / E1068 PopQA full 14,267 | `../bake_splits/e1066_popqa_full/` |

## Scripts that produced the numbers

These were previously gitignored ("oven rule"). They are the README Reproduce
entry points:

- Bake / train / merge: `../run_bake_export.sh`, `../train_bonsai_bake_lora.py`, `../brainloop_merge_lora_model.py`, `../brainloop_merge_adapters.py`, `../brainloop_merge_two_adapters.py`
- Data: `../make_popqa_bake.py`, `../make_stdlib_recall_bake.py`, `../make_ast_battery_v4.py`, `../make_fiction_bake.py`, `../make_bake_data.py`
- Eval: `../brainloop_eval_popqa.py`, `../brainloop_eval_server.py`, `../brainloop_eval_usable_bake.py`
- Route / page: `../brainloop_router.py`, `../brainloop_router_v2.py`, `../brainloop_routed_system.py`, `../brainloop_paged_endpoint.py`, `../brainloop_memctl.py`

Several still default to machine-local model and `llama.cpp` paths. Override
with flags / env vars (`--base`, `LLAMA_CPP`, `BRAINLOOP_MODELS`).

## Not in this pack (and why)

- **GGUFs, adapters, merged HF dirs.** Too large; sha256 of the E1051 Q8 GGUF is in `milestone_summary.json` if you have the artifact locally.
- **E1067 static injection (14/40 vs 13/40).** Recorded in `RESULTS.md` / `DEADBLOCK_STATUS.md` only. No per-item dump was saved. The control-vector build log is local (`e1067_cvec.log`); the vectors themselves are GGUFs and stay out.
- **E1069 rank-256 collapse.** Lab-notebook result in `DEADBLOCK_STATUS.md` (16.9% vs base 17.0%). The eval files lived on an external experiments volume and are not in this tree.
- **Older Qwen2.5-3B HumanEval dumps** under `bench_results/`. That line is superseded. `test_wiring_audit.md` (already public) documents which of those files were miswired copies. Score-only `*_evalplus_results.json` files are included; the large sample traces stay local.
- **The rest of `brainloop_runs/`** (1,500+ earlier proxy / router / signature experiments). Iteration, not the compiled-path headline.

## Integrity

`SHA256SUMS` covers every file listed above. Recount a score with:

```bash
python3 - <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
print(sum(bool(r.get("hit")) for r in rows), "/", len(rows))
PY
brainloop_runs/e1065_popqa_eval/baked.jsonl
```
