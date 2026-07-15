#!/usr/bin/env python3
"""Build compact QA sheets for one position across all card-news sets."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("card", type=int, choices=range(1, 8), help="Card position (1-7)")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    sources = sorted((root / "cards").glob(f"*_{args.card:02d}.png"))
    if len(sources) != 24:
        raise SystemExit(f"Expected 24 source cards, found {len(sources)}")

    thumb = 250
    label_h = 32
    columns = 6
    rows = 4
    sheet = Image.new("RGB", (columns * thumb, rows * (thumb + label_h)), (9, 21, 39))
    draw = ImageDraw.Draw(sheet)
    face = ImageFont.truetype("C:/Windows/Fonts/NotoSansKR-Medium.ttf", 17)
    for index, source in enumerate(sources):
        with Image.open(source) as image:
            image = image.convert("RGB").resize((thumb, thumb), Image.Resampling.LANCZOS)
        x = (index % columns) * thumb
        y = (index // columns) * (thumb + label_h)
        sheet.paste(image, (x, y))
        draw.text((x + 8, y + thumb + 5), source.stem.rsplit("_", 1)[0], font=face, fill=(205, 219, 234))
    output = args.output or root / ".qa" / f"cards_{args.card:02d}_contact.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, optimize=True)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
