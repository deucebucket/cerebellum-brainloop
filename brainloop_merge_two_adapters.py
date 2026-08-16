"""E1053 — additive knowledge packs: combine two INDEPENDENTLY-trained adapters.

Tests the core "add knowledge without retraining over the union" claim. Loads
two LoRA packs trained separately from the same frozen base, sums their deltas
(task arithmetic, combination_type='linear'), and exports one merged HF model.
No retraining over A+B happens here -- the packs were baked in isolation.

Usage: brainloop_merge_two_adapters.py --a <adapterA> --b <adapterB> \
         --output-dir <hf_out> --weight-a 1.0 --weight-b 1.0
"""

from __future__ import annotations

import argparse
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE = "/var/home/deucebucket/games/models/Ternary-Bonsai-8B-unpacked"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=BASE)
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--weight-a", type=float, default=1.0)
    ap.add_argument("--weight-b", type=float, default=1.0)
    args = ap.parse_args()

    tok = AutoTokenizer.from_pretrained(args.base, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    base = AutoModelForCausalLM.from_pretrained(
        args.base, torch_dtype=torch.bfloat16, device_map="cuda",
        attn_implementation="sdpa", trust_remote_code=True)

    m = PeftModel.from_pretrained(base, args.a, adapter_name="A")
    m.load_adapter(args.b, adapter_name="B")
    m.add_weighted_adapter(["A", "B"], [args.weight_a, args.weight_b],
                           adapter_name="AB", combination_type="linear")
    m.set_adapter("AB")
    merged = m.merge_and_unload()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    merged.save_pretrained(out, safe_serialization=True, max_shard_size="4GB")
    tok.save_pretrained(out)
    print(f"merged A+B -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
