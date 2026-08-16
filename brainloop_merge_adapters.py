"""N-way additive pack composition: sum K independently-trained adapter deltas.

Loads K LoRA packs trained separately from the same frozen base, sums their
deltas (task arithmetic, combination_type='linear'), exports one merged HF model.
No retraining over the union. Usage:
  brainloop_merge_adapters.py --output-dir <hf_out> --adapters A B C ...
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
    ap.add_argument("--adapters", nargs="+", required=True)
    ap.add_argument("--weights", nargs="+", type=float)
    ap.add_argument("--combo", default="linear",
                    choices=["linear", "ties", "dare_linear", "dare_ties"])
    ap.add_argument("--density", type=float, default=0.5)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    weights = args.weights or [1.0] * len(args.adapters)
    assert len(weights) == len(args.adapters)

    tok = AutoTokenizer.from_pretrained(args.base, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    base = AutoModelForCausalLM.from_pretrained(
        args.base, torch_dtype=torch.bfloat16, device_map="cuda",
        attn_implementation="sdpa", trust_remote_code=True)

    names = [f"P{i}" for i in range(len(args.adapters))]
    m = PeftModel.from_pretrained(base, args.adapters[0], adapter_name=names[0])
    for nm, path in zip(names[1:], args.adapters[1:]):
        m.load_adapter(path, adapter_name=nm)
    kw = {"combination_type": args.combo}
    if args.combo != "linear":
        kw["density"] = args.density
    m.add_weighted_adapter(names, weights, adapter_name="SUM", **kw)
    m.set_adapter("SUM")
    merged = m.merge_and_unload()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    merged.save_pretrained(out, safe_serialization=True, max_shard_size="4GB")
    tok.save_pretrained(out)
    print(f"summed {len(args.adapters)} packs -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
