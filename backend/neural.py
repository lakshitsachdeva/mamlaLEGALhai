"""Optional InLegalBERT evidence-pair signal for reviewer-guided rule checks.

The checkpoint is pretrained for masked language modeling, not calibrated for
similarity or contradiction. Cosine similarity is a triage signal only.
"""

from __future__ import annotations

import os
from functools import lru_cache

MODEL_ID = "law-ai/InLegalBERT"
MODEL_REVISION = "b5ecfed8ed6cf9d25a3cb8225a8c52f161f7401a"
MAX_TOKENS = 256


class NeuralUnavailable(RuntimeError):
    """The optional neural dependencies or checkpoint could not be loaded."""


@lru_cache(maxsize=1)
def _load_model():
    # The standard Hub download works on classroom networks where Xet may stall.
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    try:
        import torch
        from transformers import AutoModel, AutoTokenizer
    except ImportError as exc:
        raise NeuralUnavailable(
            "InLegalBERT is optional. Install it with '.venv/bin/python -m pip install -r requirements-neural.txt' and restart the API."
        ) from exc
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION)
        model = AutoModel.from_pretrained(MODEL_ID, revision=MODEL_REVISION, use_safetensors=False)
        model.eval()
    except (OSError, ValueError) as exc:
        raise NeuralUnavailable(
            "InLegalBERT could not be loaded. Check model access and the local Hugging Face cache, then retry."
        ) from exc
    return torch, tokenizer, model


def score_evidence_pair(left: str, right: str) -> dict:
    """Return a raw mean-pooled encoder cosine; never a contradiction verdict."""
    torch, tokenizer, model = _load_model()
    texts = [left, right]
    lengths = [len(tokenizer(text, add_special_tokens=True)["input_ids"]) for text in texts]
    encoded = tokenizer(texts, padding=True, truncation=True, max_length=MAX_TOKENS, return_tensors="pt")
    with torch.inference_mode():
        hidden = model(**encoded).last_hidden_state
        mask = encoded["attention_mask"].unsqueeze(-1)
        pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
        cosine = torch.nn.functional.cosine_similarity(pooled[0:1], pooled[1:2]).item()
    return {
        "modelId": MODEL_ID,
        "modelRevision": MODEL_REVISION,
        "cosineSimilarity": round(float(cosine), 4),
        "method": "mean-pooled last hidden state cosine",
        "truncated": {"left": lengths[0] > MAX_TOKENS, "right": lengths[1] > MAX_TOKENS},
        "note": "Uncalibrated relatedness signal from a pretrained encoder. A high score does not mean compatibility or contradiction.",
    }
