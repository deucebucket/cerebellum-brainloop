# Repository Guidelines

## Project Structure & Module Organization

This is a Python research prototype for Cerebellum/Brainloop experiments. Core model and training code lives at the repository root: `model.py`, `train.py`, `evaluate.py`, refiner variants such as `refiner_vanilla.py`, and GGUF/export utilities such as `unroll_vanilla_gguf.py` and `export_*_gguf.py`. Benchmark and audit scripts use prefixes like `bench_`, `smoke_test_`, `recall_`, and `test_`. Active Ternary-Bonsai work uses `bonsai_*.py`. RAG-specific code lives in `rag-experiment/`.

Keep large models, checkpoints, and datasets outside the repo when possible; the README references external paths under `/var/home/deucebucket/games/...`.

## Build, Test, and Development Commands

Use `python3` directly; there is no packaged build step.

- `python3 model.py` verifies the base Conch model wiring.
- `./run_poc.sh` runs the original full proof-of-concept training and evaluation pipeline.
- `python3 train.py --phase 1 --data /path/to/wiki.test.raw --output checkpoints` starts a training phase.
- `python3 evaluate.py --checkpoint checkpoints/phase2/best_checkpoint.pt --data /path/to/wiki.test.raw` evaluates a trained checkpoint.
- `cd rag-experiment && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python rag_experiment.py` runs the RAG smoke test.

Most scripts assume CUDA and Hugging Face model access; record hardware, model path, and dataset path in result notes.

## Coding Style & Naming Conventions

Use 4-space indentation, `snake_case` for functions and files, `CamelCase` for classes, and uppercase constants for fixed paths or model names. Prefer `argparse` for new runnable experiments. Group imports as standard library, third-party, then local modules. Avoid hidden global state; print or save parameters needed to reproduce a run.

## Testing Guidelines

There is no centralized test framework. Treat smoke and benchmark scripts as executable tests: `python3 test_force_loop.py`, `python3 smoke_test_gguf.py`, and relevant `bench_*.py` scripts. For new mechanisms, add a small script or mode that verifies baseline parity, intervention effect, and failure cases. Name audits with `test_`, `smoke_`, `bench_`, or `*_audit`.

## Commit & Pull Request Guidelines

Recent commits use prefixes such as `results:`, `fix:`, and `chore:` followed by a specific finding or change. Examples: `results: layer sweep validates L33 injection window` or `fix: correct crossed perplexity labels`.

Pull requests should include the experiment purpose, exact commands run, model/data paths, key metrics before and after, and known regressions. For model work, prefer logs, tables, and linked result files.

## Security & Configuration Tips

Do not commit API tokens, private model credentials, large checkpoints, or new machine-local absolute paths. Prefer configurable paths and keep generated artifacts out of git unless they are intentional evidence files.
