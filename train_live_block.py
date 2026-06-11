"""
train_live_block.py -- Live Block experiment

Architecture: a full Qwen2DecoderLayer (attention + FFN) inserted between
layers 17 and 18, trained with pure LM loss. No gate, no subspace mask,
no revolution loop. o_proj.weight and down_proj.weight zero-initialized so
the block starts as an exact identity. Trained exactly as vanilla llama.cpp
will execute it: h_out = block(h) with standard internal residuals.

This is the fix for the historical STE-gate train/deploy mismatch that caused
looping catastrophe in the old looped-refiner experiments.

Usage:
    python train_live_block.py
    python train_live_block.py --epochs 3 --max-steps-per-epoch 2000
    python train_live_block.py --resume checkpoints-liveblock/live_block_epoch1.pt
"""

import argparse
import copy
import datetime
import os
import sys

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MODEL_NAME = "Qwen/Qwen2.5-3B"
DEVICE = torch.device("cuda")
STATUS_FILE = "DEADBLOCK_STATUS.md"
CHECKPOINT_DIR = "checkpoints-liveblock"

WIKI_TRAIN = "/var/home/deucebucket/games/osmosis-quants/wiki.train.raw"
WIKI_TEST  = "/var/home/deucebucket/games/osmosis-quants/wiki.test.raw"
BLOCK_SIZE  = 512
BATCH_SIZE  = 2


# ---------------------------------------------------------------------------
# Status logging (shared file with dead-block; tagged [LiveBlock])
# ---------------------------------------------------------------------------
def log_status(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"\n[{ts}] [LiveBlock] {msg}"
    print(line, flush=True)
    with open(STATUS_FILE, "a") as fh:
        fh.write(line + "\n")


# ---------------------------------------------------------------------------
# Dataset (WikiDataset pattern from train_python_dual.py)
# ---------------------------------------------------------------------------
class WikiDataset(Dataset):
    def __init__(self, tokenizer, file_path: str, block_size: int = BLOCK_SIZE,
                 max_chunks=None):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        tokens = tokenizer.encode(text)
        self.examples = [
            torch.tensor(tokens[i : i + block_size], dtype=torch.long)
            for i in range(0, len(tokens) - block_size, block_size)
        ]
        if max_chunks is not None:
            self.examples = self.examples[:max_chunks]

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        return self.examples[idx]


def wiki_collate(batch):
    max_len = max(x.size(0) for x in batch)
    padded = torch.zeros(len(batch), max_len, dtype=torch.long)
    for i, x in enumerate(batch):
        padded[i, : x.size(0)] = x
    return padded


# ---------------------------------------------------------------------------
# Live Block Wrapper
# ---------------------------------------------------------------------------
class LiveBlockWrapper(nn.Module):
    """
    Wraps model.model.layers[17].

    Forward math:
        base_out = base_layer(hidden_states, *args, **kwargs)   [frozen]
        h        = base_out[0] if tuple else base_out
        block_out = self.block(h, *args, **kwargs)              [trainable]
        h_out    = block_out[0] if tuple else block_out
        return (h_out,) + base_out[1:]  if tuple else h_out

    Zero-init invariant at construction time:
        block.self_attn.o_proj.weight  = 0  (no bias on o_proj in Qwen2.5)
        block.mlp.down_proj.weight     = 0
    => attention output contribution == 0, FFN output contribution == 0
    => block output == its own input h (via internal residuals) == base_layer output
    => parity check must pass before training starts.

    No gate. No subspace mask. No bypass flag.
    """

    def __init__(self, base_layer):
        super().__init__()
        self.base_layer = base_layer

        # Freeze base layer entirely
        for p in self.base_layer.parameters():
            p.requires_grad = False

        # Full decoder block deepcopy: preserves architecture, causal mask handling,
        # position embeddings, SwiGLU, RMSNorms -- same args/kwargs pass-through
        # as RefinerWrapper in refiner_vanilla.py.
        self.block = copy.deepcopy(base_layer)

        # Zero-init so block starts as identity.
        # Confirmed: o_proj is nn.Linear(..., bias=False) in Qwen2.5; weight only.
        nn.init.zeros_(self.block.self_attn.o_proj.weight)
        nn.init.zeros_(self.block.mlp.down_proj.weight)

        # All block params are trainable
        for p in self.block.parameters():
            p.requires_grad = True

    def forward(self, hidden_states, *args, **kwargs):
        base_out = self.base_layer(hidden_states, *args, **kwargs)

        h = base_out[0] if isinstance(base_out, tuple) else base_out

        block_out = self.block(h, *args, **kwargs)
        h_out = block_out[0] if isinstance(block_out, tuple) else block_out

        if isinstance(base_out, tuple):
            return (h_out,) + base_out[1:]
        return h_out


# ---------------------------------------------------------------------------
# Model patching
# ---------------------------------------------------------------------------
def patch_model(model):
    """Replace layers[17] with LiveBlockWrapper; freeze everything else."""
    wrapper = LiveBlockWrapper(model.model.layers[17]).to(DEVICE, dtype=torch.bfloat16)
    model.model.layers[17] = wrapper

    # Freeze all parameters outside the wrapper's trainable block
    for name, param in model.named_parameters():
        in_wrapper_block = (
            "model.layers.17" in name and ".base_layer." not in name
        )
        param.requires_grad = in_wrapper_block

    return model, wrapper


# ---------------------------------------------------------------------------
# Resume helper
# ---------------------------------------------------------------------------
def load_resume(path: str, wrapper: LiveBlockWrapper):
    ckpt = torch.load(path, map_location=DEVICE, weights_only=False)
    wrapper.block.load_state_dict(ckpt["l17_block"])
    log_status(f"Resumed from {path}.")


# ---------------------------------------------------------------------------
# Parity check (REQUIRED before training)
# ---------------------------------------------------------------------------
def run_parity_check(model, tokenizer, wrapper: LiveBlockWrapper):
    log_status("=== PARITY CHECK: verifying zero-init identity (o_proj=0, down_proj=0) ===")

    prompts = [
        "What is the capital of France?",
        "def fibonacci(n):",
        "import os\nprint(os.getcwd())",
    ]

    model.eval()
    max_diffs = []

    for prompt in prompts:
        inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)

        # Wrapper active: block has zero o_proj/down_proj, so h passes through
        with torch.no_grad():
            logits_with = model(**inputs).logits

        # Bypass: temporarily swap wrapper for raw base_layer
        model.model.layers[17] = wrapper.base_layer
        with torch.no_grad():
            logits_without = model(**inputs).logits
        model.model.layers[17] = wrapper  # restore

        diff = (logits_with - logits_without).abs().max().item()
        max_diffs.append(diff)
        log_status(f"  Prompt '{prompt[:40]}' max_abs_diff = {diff:.6e}")

    overall_max = max(max_diffs)
    # bf16 rounding is ~1e-3; true zeros produce exact 0 in down_proj/o_proj path
    threshold = 1e-3
    if overall_max <= threshold:
        log_status(
            f"PARITY CHECK PASSED: max_abs_diff = {overall_max:.6e} "
            f"(<= {threshold}). Identity confirmed."
        )
    else:
        log_status(
            f"PARITY CHECK FAILED: max_abs_diff = {overall_max:.6e} "
            f"(> {threshold}). Zero-init did not produce identity. Aborting."
        )
        sys.exit(1)

    return overall_max


# ---------------------------------------------------------------------------
# Validation: held-out PPL on first 100 chunks of wiki.test.raw
# ---------------------------------------------------------------------------
def run_validation(model, val_loader) -> float:
    """Compute PPL on held-out chunks (no_grad, exp of mean cross-entropy)."""
    model.eval()
    total_loss = 0.0
    n_batches = 0

    with torch.no_grad():
        for input_ids in val_loader:
            input_ids = input_ids.to(DEVICE)
            outputs = model(input_ids)
            logits = outputs.logits
            shift_logits = logits[:, :-1, :].contiguous()
            shift_labels = input_ids[:, 1:].contiguous()
            loss = F.cross_entropy(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.view(-1),
            )
            total_loss += loss.item()
            n_batches += 1

    mean_loss = total_loss / max(n_batches, 1)
    import math
    return math.exp(mean_loss)


# ---------------------------------------------------------------------------
# Checkpoint save
# ---------------------------------------------------------------------------
def save_checkpoint(wrapper: LiveBlockWrapper, epoch: int, val_ppl: float, path: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    torch.save(
        {
            "l17_block": wrapper.block.state_dict(),
            "meta": {
                "epoch": epoch,
                "val_ppl": val_ppl,
                "timestamp": ts,
            },
        },
        path,
    )


# ---------------------------------------------------------------------------
# Training loop (one epoch, capped at max_steps)
# ---------------------------------------------------------------------------
def train_epoch(
    model,
    wrapper: LiveBlockWrapper,
    loader,
    optimizer,
    epoch: int,
    max_steps: int,
) -> float:
    """Run one epoch up to max_steps. Returns mean train loss for the epoch."""
    model.train()

    running_loss = 0.0
    epoch_loss = 0.0
    step = 0

    for input_ids in loader:
        if step >= max_steps:
            break

        input_ids = input_ids.to(DEVICE)

        outputs = model(input_ids)
        logits = outputs.logits

        # Pure LM loss: standard causal shift, no masking
        shift_logits = logits[:, :-1, :].contiguous()
        shift_labels = input_ids[:, 1:].contiguous()
        loss = F.cross_entropy(
            shift_logits.view(-1, shift_logits.size(-1)),
            shift_labels.view(-1),
        )

        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        running_loss += loss.item()
        epoch_loss += loss.item()
        step += 1

        if step % 100 == 0:
            import math
            avg_loss = running_loss / 100
            running_ppl = math.exp(avg_loss)
            log_status(
                f"[Epoch {epoch}] Step {step}/{max_steps} | "
                f"Loss: {avg_loss:.4f} | PPL: {running_ppl:.2f}"
            )
            running_loss = 0.0

    return epoch_loss / max(step, 1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description=(
            "Train a live block (full Qwen2 decoder) inserted between "
            "layers 17 and 18 with pure LM loss."
        )
    )
    parser.add_argument("--epochs", type=int, default=2,
                        help="Number of training epochs (default: 2)")
    parser.add_argument("--max-steps-per-epoch", type=int, default=2000,
                        help="Max optimizer steps per epoch (default: 2000)")
    parser.add_argument("--resume", type=str, default=None,
                        help="Path to checkpoint {'l17_block', 'meta'} to resume from")
    args = parser.parse_args()

    log_status(
        f"=== train_live_block.py started | "
        f"epochs={args.epochs} max_steps={args.max_steps_per_epoch} "
        f"resume={args.resume} ==="
    )

    # Load tokenizer
    log_status(f"Loading tokenizer for {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    # Build datasets before model load to fail fast on missing files
    log_status(f"Building WikiDataset from {WIKI_TRAIN}...")
    train_dataset = WikiDataset(tokenizer, WIKI_TRAIN, block_size=BLOCK_SIZE)
    log_status(f"  Train chunks: {len(train_dataset)}")

    log_status(f"Building validation set from {WIKI_TEST} (first 100 chunks)...")
    val_dataset = WikiDataset(tokenizer, WIKI_TEST, block_size=BLOCK_SIZE, max_chunks=100)
    log_status(f"  Val chunks: {len(val_dataset)}")

    train_loader = DataLoader(
        train_dataset, batch_size=BATCH_SIZE, shuffle=True, collate_fn=wiki_collate
    )
    val_loader = DataLoader(
        val_dataset, batch_size=BATCH_SIZE, shuffle=False, collate_fn=wiki_collate
    )

    # Load model and patch
    log_status(f"Loading {MODEL_NAME}...")
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.bfloat16)
    model, wrapper = patch_model(model)
    model = model.to(DEVICE)

    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    log_status(f"Trainable parameters: {trainable:,}")

    # Resume before parity check (resumed weights may not be identity, that's fine --
    # parity is only meaningful at init; skip if resuming)
    if args.resume is not None:
        load_resume(args.resume, wrapper)
        log_status("Skipping parity check (resuming from checkpoint; block is no longer at zero-init).")
    else:
        run_parity_check(model, tokenizer, wrapper)

    # Optimizer: golden config -- lr=1e-4, wd=0.1
    optimizer = AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=1e-4,
        weight_decay=0.1,
    )

    os.makedirs(CHECKPOINT_DIR, exist_ok=True)

    best_val_ppl = float("inf")
    import math

    for epoch in range(1, args.epochs + 1):
        log_status(f"=== Epoch {epoch}/{args.epochs} ===")

        mean_train_loss = train_epoch(
            model, wrapper, train_loader, optimizer, epoch, args.max_steps_per_epoch
        )
        train_ppl = math.exp(mean_train_loss)
        log_status(
            f"[Epoch {epoch}] Train mean loss: {mean_train_loss:.4f} | "
            f"Train PPL: {train_ppl:.2f}"
        )

        val_ppl = run_validation(model, val_loader)
        log_status(f"[Epoch {epoch}] Val PPL: {val_ppl:.4f}")

        # Per-epoch checkpoint
        epoch_path = os.path.join(CHECKPOINT_DIR, f"live_block_epoch{epoch}.pt")
        save_checkpoint(wrapper, epoch, val_ppl, epoch_path)

        # Best checkpoint (lowest val PPL)
        is_best = val_ppl < best_val_ppl
        if is_best:
            best_val_ppl = val_ppl
            best_path = os.path.join(CHECKPOINT_DIR, "live_block_best.pt")
            save_checkpoint(wrapper, epoch, val_ppl, best_path)

        # Always write last
        last_path = os.path.join(CHECKPOINT_DIR, "live_block_last.pt")
        save_checkpoint(wrapper, epoch, val_ppl, last_path)

        written = [epoch_path, last_path]
        if is_best:
            written.append(best_path)

        log_status(
            f"[Epoch {epoch} SUMMARY] "
            f"train_ppl={train_ppl:.4f} val_ppl={val_ppl:.4f} | "
            f"best_improved={'YES' if is_best else 'NO'} "
            f"best_val_ppl={best_val_ppl:.4f} | "
            f"saved={[os.path.basename(p) for p in written]}"
        )

    log_status(
        f"Training complete. Best val PPL: {best_val_ppl:.4f}. "
        f"Checkpoints in {CHECKPOINT_DIR}/"
    )


if __name__ == "__main__":
    main()
