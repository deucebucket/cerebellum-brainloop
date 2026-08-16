"""Merge a PEFT LoRA adapter into a standalone Hugging Face model checkpoint.

This supports the Brainloop baked-memory diagnostic: if HF base+adapter recall
works but llama.cpp runtime --lora recall fails, export a fully merged HF model
and convert that model to GGUF to test whether the memory survives as weights.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from brainloop_memory_product import file_sha256


SCHEMA = "brainloop-merge-lora-model-v1"
DEFAULT_BASE = "/var/home/deucebucket/games/models/Ternary-Bonsai-8B-unpacked"
DEFAULT_ADAPTER = "adapters/bonsai-bake-e1031-tiny-qa-r32-a32-lr5e4-s300"
DEFAULT_OUTPUT_DIR = "merged_models/e1037_bonsai_tiny_qa_overfit_merged"
DEFAULT_RUN_ID = "e1037_bonsai_tiny_qa_overfit_merged"
DEFAULT_OUT_DIR = "brainloop_runs/e1037_bonsai_tiny_qa_overfit_merged"


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).isoformat()


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def list_artifacts(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for child in sorted(path.iterdir()):
        if not child.is_file():
            continue
        records.append(
            {
                "path": str(child),
                "size_bytes": child.stat().st_size,
                "sha256": file_sha256(child),
            }
        )
    return records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge a PEFT LoRA adapter into a standalone HF model.")
    parser.add_argument("--base", default=DEFAULT_BASE)
    parser.add_argument("--adapter", default=DEFAULT_ADAPTER)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--max-shard-size", default="4GB")
    parser.add_argument("--dtype", choices=["bf16", "fp16"], default="bf16")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    out_dir = Path(args.out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    dtype = torch.bfloat16 if args.dtype == "bf16" else torch.float16

    tokenizer = AutoTokenizer.from_pretrained(args.base, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    base_model = AutoModelForCausalLM.from_pretrained(
        args.base,
        torch_dtype=dtype,
        device_map="cuda",
        attn_implementation="sdpa",
        trust_remote_code=True,
    )
    peft_model = PeftModel.from_pretrained(base_model, args.adapter)
    merged_model = peft_model.merge_and_unload()
    merged_model.save_pretrained(
        output_dir,
        safe_serialization=True,
        max_shard_size=args.max_shard_size,
    )
    tokenizer.save_pretrained(output_dir)

    summary = {
        "schema": SCHEMA,
        "run_id": args.run_id,
        "created_at": utc_now(),
        "ok": True,
        "production_ready": False,
        "root_or_systemd_work_used": False,
        "base": args.base,
        "adapter": args.adapter,
        "output_dir": str(output_dir),
        "dtype": args.dtype,
        "max_shard_size": args.max_shard_size,
        "git_head": git_head(),
        "adapter_model_sha256": file_sha256(Path(args.adapter) / "adapter_model.safetensors"),
        "artifact_records": list_artifacts(output_dir),
        "notes": [
            "Merged HF model checkpoint for baked-memory GGUF diagnostic.",
            "This is not a product claim; it tests whether memory survives full-weight export better than runtime --lora.",
        ],
    }
    write_json(output_dir / "brainloop_merge_manifest.json", summary)
    write_json(out_dir / "summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
