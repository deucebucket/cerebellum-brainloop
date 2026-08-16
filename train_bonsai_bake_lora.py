"""Train a conservative PEFT LoRA for Bonsai baked-knowledge SFT.

This uses the unpacked F16 Bonsai HF model for correct training semantics and
saves a standard PEFT adapter that llama.cpp's convert_lora_to_gguf.py can
convert for stock llama.cpp serving.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments


ALL_LINEAR = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]


def format_prompt(tokenizer: AutoTokenizer, messages: list[dict[str, str]], prompt_format: str) -> str:
    question = messages[0]["content"].strip()
    if prompt_format == "chat":
        return tokenizer.apply_chat_template(
            messages[:-1],
            tokenize=False,
            add_generation_prompt=True,
        )
    if prompt_format == "raw":
        return question
    if prompt_format == "qa":
        return f"Question: {question}\nAnswer:"
    raise ValueError(f"unknown prompt format: {prompt_format}")


def parse_layers(spec: str | None) -> list[int] | None:
    if spec is None or spec.lower() in {"", "all", "none"}:
        return None
    layers: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            layers.extend(range(int(start), int(end) + 1))
        else:
            layers.append(int(part))
    return sorted(set(layers))


def load_rows(
    path: str,
    limit: int | None,
    tokenizer: AutoTokenizer,
    max_len: int,
    assistant_only_loss: bool,
    prompt_format: str,
) -> Dataset:
    rows = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            messages = row.get("messages")
            if messages and len(messages) >= 2:
                answer = messages[-1]["content"].strip()
                if assistant_only_loss:
                    prompt = format_prompt(tokenizer, messages, prompt_format)
                    text = prompt + answer + (tokenizer.eos_token or "")
                    prompt_ids = tokenizer(prompt, add_special_tokens=False)["input_ids"]
                    encoded = tokenizer(text, add_special_tokens=False, max_length=max_len, truncation=True)
                    input_ids = encoded["input_ids"]
                    labels = [-100] * min(len(prompt_ids), len(input_ids))
                    labels.extend(input_ids[len(labels) :])
                    rows.append(
                        {
                            "input_ids": input_ids,
                            "attention_mask": encoded["attention_mask"],
                            "labels": labels,
                        }
                    )
                else:
                    if prompt_format == "chat":
                        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
                    else:
                        prompt = format_prompt(tokenizer, messages, prompt_format)
                        text = prompt + answer + (tokenizer.eos_token or "")
                    encoded = tokenizer(text, add_special_tokens=False, max_length=max_len, truncation=True)
                    rows.append(
                        {
                            "input_ids": encoded["input_ids"],
                            "attention_mask": encoded["attention_mask"],
                            "labels": encoded["input_ids"].copy(),
                        }
                    )
            if limit is not None and len(rows) >= limit:
                break
    return Dataset.from_list(rows)


class CausalCollator:
    def __init__(self, tokenizer: AutoTokenizer) -> None:
        self.tokenizer = tokenizer

    def __call__(self, features: list[dict[str, list[int]]]) -> dict[str, torch.Tensor]:
        max_len = max(len(feature["input_ids"]) for feature in features)
        pad_id = self.tokenizer.pad_token_id
        batch = {"input_ids": [], "attention_mask": [], "labels": []}
        for feature in features:
            pad = max_len - len(feature["input_ids"])
            batch["input_ids"].append(feature["input_ids"] + [pad_id] * pad)
            batch["attention_mask"].append(feature["attention_mask"] + [0] * pad)
            batch["labels"].append(feature["labels"] + [-100] * pad)
        return {key: torch.tensor(value, dtype=torch.long) for key, value in batch.items()}


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="/var/home/deucebucket/games/models/Ternary-Bonsai-8B-unpacked")
    parser.add_argument("--data", default="bake_splits/bake_train.jsonl")
    parser.add_argument("--output-dir", default="adapters/bonsai-bake-late-r8")
    parser.add_argument("--num-examples", type=int)
    parser.add_argument("--rank", type=int, default=8)
    parser.add_argument("--alpha", type=int, default=8)
    parser.add_argument("--lr", type=float, default=5e-5)
    parser.add_argument("--epochs", type=float, default=2.0)
    parser.add_argument("--max-steps", type=int, default=-1)
    parser.add_argument("--max-len", type=int, default=1024)
    parser.add_argument("--grad-accum", type=int, default=4)
    parser.add_argument("--layers", default="28-35")
    parser.add_argument("--modules", nargs="+", default=ALL_LINEAR)
    parser.add_argument("--save-steps", type=int, default=0)
    parser.add_argument("--full-text-loss", action="store_true")
    parser.add_argument("--prompt-format", choices=["chat", "raw", "qa"], default="chat")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    layers = parse_layers(args.layers)

    tokenizer = AutoTokenizer.from_pretrained(args.base, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    assistant_only_loss = not args.full_text_loss
    dataset = load_rows(args.data, args.num_examples, tokenizer, args.max_len, assistant_only_loss, args.prompt_format)
    print(f"dataset: {len(dataset)} conversations")
    print(f"assistant-only loss: {assistant_only_loss}")
    print(f"prompt format: {args.prompt_format}")
    print(f"target modules: {args.modules}")
    print(f"target layers: {'all' if layers is None else layers}")

    model = AutoModelForCausalLM.from_pretrained(
        args.base,
        torch_dtype=torch.bfloat16,
        device_map="cuda",
        attn_implementation="sdpa",
        trust_remote_code=True,
    )
    model.config.use_cache = False

    peft_kwargs = {
        "r": args.rank,
        "lora_alpha": args.alpha,
        "lora_dropout": 0.0,
        "target_modules": args.modules,
        "task_type": "CAUSAL_LM",
        "bias": "none",
    }
    if layers is not None:
        peft_kwargs["layers_to_transform"] = layers
        peft_kwargs["layers_pattern"] = "layers"
    peft_config = LoraConfig(**peft_kwargs)
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    cfg_kwargs = {
        "output_dir": str(out_dir),
        "per_device_train_batch_size": 1,
        "gradient_accumulation_steps": args.grad_accum,
        "num_train_epochs": args.epochs,
        "max_steps": args.max_steps,
        "learning_rate": args.lr,
        "lr_scheduler_type": "cosine",
        "warmup_ratio": 0.05,
        "bf16": True,
        "gradient_checkpointing": True,
        "gradient_checkpointing_kwargs": {"use_reentrant": False},
        "logging_steps": 5,
        "save_strategy": "steps" if args.save_steps > 0 else "no",
        "save_steps": args.save_steps if args.save_steps > 0 else 500,
        "report_to": "none",
        "seed": 42,
        "remove_unused_columns": False,
        "save_total_limit": 2,
    }
    training_args = TrainingArguments(**cfg_kwargs)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=CausalCollator(tokenizer),
    )
    # Resume from the last checkpoint in out_dir if one exists (survives crashes).
    from transformers.trainer_utils import get_last_checkpoint
    _ckpt = get_last_checkpoint(str(out_dir)) if out_dir.is_dir() else None
    if _ckpt:
        print(f"[resume] continuing from {_ckpt}", flush=True)
    trainer.train(resume_from_checkpoint=_ckpt)
    trainer.save_model(str(out_dir))
    tokenizer.save_pretrained(str(out_dir))

    manifest = {
        "base": args.base,
        "data": args.data,
        "output_dir": str(out_dir),
        "git_head": git_head(),
        "rank": args.rank,
        "alpha": args.alpha,
        "lr": args.lr,
        "epochs": args.epochs,
        "max_steps": args.max_steps,
        "max_len": args.max_len,
        "grad_accum": args.grad_accum,
        "layers": "all" if layers is None else layers,
        "modules": args.modules,
        "assistant_only_loss": assistant_only_loss,
        "prompt_format": args.prompt_format,
        "prompt_uses_generation_template": assistant_only_loss and args.prompt_format == "chat",
        "torch": torch.__version__,
    }
    (out_dir / "brainloop_train_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"saved adapter -> {out_dir}")


if __name__ == "__main__":
    main()
