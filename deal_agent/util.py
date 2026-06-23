"""Small helpers shared across tools and agents."""

from __future__ import annotations

import base64
import mimetypes
import os
from typing import Any

# MIME types accepted as inline images by the Messages API
IMAGE_MIME = {"image/jpeg", "image/png", "image/gif", "image/webp"}


def message_text(message: Any) -> str:
    """Concatenate the text blocks of a Message / BetaMessage response."""
    if message is None:
        return ""
    parts = [
        block.text
        for block in getattr(message, "content", [])
        if getattr(block, "type", None) == "text"
    ]
    return "\n".join(parts).strip()


def file_to_content_block(path: str) -> dict:
    """Turn a local image or PDF into a Messages API content block.

    Images -> {"type": "image", ...}; PDFs -> {"type": "document", ...}.
    Raises ValueError for unsupported types.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    media_type, _ = mimetypes.guess_type(path)
    with open(path, "rb") as fh:
        data = base64.standard_b64encode(fh.read()).decode("utf-8")

    if media_type in IMAGE_MIME:
        return {
            "type": "image",
            "source": {"type": "base64", "media_type": media_type, "data": data},
        }
    if media_type == "application/pdf" or path.lower().endswith(".pdf"):
        return {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": data,
            },
        }
    raise ValueError(
        f"Unsupported visual file type for {path!r} (got {media_type!r}). "
        "Provide a PNG/JPG/GIF/WebP image or a PDF."
    )
