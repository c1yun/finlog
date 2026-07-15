#!/usr/bin/env python3
"""Validate the generated FinLog card-news archive."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    content = json.loads((ROOT / "cards_content.json").read_text(encoding="utf-8"))
    metadata = json.loads((ROOT / "cards_meta.json").read_text(encoding="utf-8"))
    if len(content) != 24 or len(metadata) != 24:
        raise SystemExit(f"Expected 24 sets: content={len(content)}, metadata={len(metadata)}")

    content_slugs = [item["slug"] for item in content]
    metadata_slugs = [item["slug"] for item in metadata]
    if content_slugs != metadata_slugs:
        raise SystemExit("cards_content.json and cards_meta.json slug order differs")

    expected = {f"{slug}_{number:02d}.png" for slug in content_slugs for number in range(1, 8)}
    actual = {path.name for path in (ROOT / "cards").glob("*.png")}
    if expected != actual:
        raise SystemExit(f"Card file mismatch: missing={sorted(expected-actual)}, extra={sorted(actual-expected)}")

    invalid_sizes = []
    total_bytes = 0
    for path in sorted((ROOT / "cards").glob("*.png")):
        with Image.open(path) as image:
            if image.size != (1080, 1080):
                invalid_sizes.append((path.name, image.size))
        total_bytes += path.stat().st_size
    if invalid_sizes:
        raise SystemExit(f"Invalid card dimensions: {invalid_sizes}")

    thumbs = sorted((ROOT / "cards" / "thumbs").glob("*.webp"))
    if len(thumbs) != 24:
        raise SystemExit(f"Expected 24 thumbnails, found {len(thumbs)}")
    for path in thumbs:
        with Image.open(path) as image:
            if image.size != (560, 560):
                raise SystemExit(f"Invalid thumbnail dimensions: {path.name} {image.size}")

    print(
        f"Card validation passed: sets={len(content)}, cards={len(actual)}, "
        f"dimensions=1080x1080, thumbnails={len(thumbs)}, bytes={total_bytes}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
