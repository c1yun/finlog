#!/usr/bin/env python3
"""Generate FinLog's 24 x 7 editorial card-news system.

The cards are intentionally generated from structured Korean copy instead of
being flattened into an uneditable design file. This keeps wording, layout,
and visual consistency reproducible for later cohorts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


SIZE = 1080
MARGIN = 76
NAVY = (7, 23, 45)
NAVY_2 = (12, 34, 64)
INK = (13, 30, 53)
MUTED = (83, 101, 123)
PAPER = (247, 245, 239)
WHITE = (255, 255, 255)
LINE = (216, 222, 228)
CYAN = (89, 185, 223)
GOLD = (231, 177, 67)
GREEN = (44, 145, 115)
RED = (202, 76, 73)

FONT_REGULAR = Path("C:/Windows/Fonts/NotoSansKR-Regular.ttf")
FONT_MEDIUM = Path("C:/Windows/Fonts/NotoSansKR-Medium.ttf")
FONT_BOLD = Path("C:/Windows/Fonts/NotoSansKR-Bold.ttf")

CATEGORY_ACCENTS = {
    "플랫폼·규제": (90, 185, 223),
    "정책·기후금융": (67, 166, 130),
    "사회·금융포용": (217, 150, 82),
    "자본시장": (87, 145, 224),
    "무역·거시경제": (225, 153, 73),
    "사회·조직": (178, 113, 186),
    "자본시장 인프라": (57, 169, 183),
    "디지털금융": (97, 128, 226),
    "커리어 인사이트": (222, 171, 70),
    "현장·자본시장": (82, 166, 140),
    "산업·기업금융": (76, 145, 222),
    "ESG·기후금융": (57, 155, 115),
    "기업가치·거버넌스": (191, 137, 65),
    "노동·거시경제": (206, 112, 84),
    "AI·금융윤리": (128, 108, 220),
    "AI·시장감시": (73, 160, 202),
    "신용·금융포용": (58, 157, 131),
    "파생·리스크관리": (202, 98, 91),
    "회계·기업분석": (68, 139, 194),
    "레그테크·준법": (101, 137, 207),
    "현장·디지털금융": (69, 166, 164),
}


def font(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
    path = {"regular": FONT_REGULAR, "medium": FONT_MEDIUM, "bold": FONT_BOLD}[weight]
    if not path.exists():
        raise FileNotFoundError(f"Required Korean font not found: {path}")
    return ImageFont.truetype(str(path), size=size)


def text_width(draw: ImageDraw.ImageDraw, value: str, face: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), value, font=face)
    return box[2] - box[0]


def wrap_text(draw: ImageDraw.ImageDraw, value: str, face: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in value.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        words = paragraph.split(" ")
        current = ""
        for word in words:
            candidate = word if not current else f"{current} {word}"
            if text_width(draw, candidate, face) <= width:
                current = candidate
                continue
            if current:
                lines.append(current)
                current = ""
            if text_width(draw, word, face) <= width:
                current = word
                continue
            piece = ""
            for char in word:
                candidate_piece = piece + char
                if piece and text_width(draw, candidate_piece, face) > width:
                    lines.append(piece)
                    piece = char
                else:
                    piece = candidate_piece
            current = piece
        if current:
            lines.append(current)
    return lines


def fit_text(
    draw: ImageDraw.ImageDraw,
    value: str,
    width: int,
    max_height: int,
    start_size: int,
    min_size: int,
    weight: str = "bold",
    spacing_ratio: float = 0.28,
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    for size in range(start_size, min_size - 1, -2):
        face = font(size, weight)
        lines = wrap_text(draw, value, face, width)
        spacing = max(8, int(size * spacing_ratio))
        line_height = int(size * 1.16)
        height = len(lines) * line_height + max(0, len(lines) - 1) * spacing
        if height <= max_height:
            return face, lines, spacing
    face = font(min_size, weight)
    return face, wrap_text(draw, value, face, width), max(8, int(min_size * spacing_ratio))


def draw_lines(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    lines: Iterable[str],
    face: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    spacing: int,
    line_height: int | None = None,
) -> int:
    x, y = xy
    step = line_height or int(face.size * 1.16)
    last_y = y
    for idx, line in enumerate(lines):
        draw.text((x, last_y), line, font=face, fill=fill)
        last_y += step
        if idx < len(list(lines)) - 1:
            last_y += spacing
    return last_y


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    value: str,
    xy: tuple[int, int],
    width: int,
    size: int,
    fill: tuple[int, int, int],
    weight: str = "regular",
    spacing: int | None = None,
) -> int:
    face = font(size, weight)
    lines = wrap_text(draw, value, face, width)
    line_gap = spacing if spacing is not None else max(8, int(size * 0.26))
    step = int(size * 1.16)
    y = xy[1]
    for idx, line in enumerate(lines):
        draw.text((xy[0], y), line, font=face, fill=fill)
        y += step
        if idx < len(lines) - 1:
            y += line_gap
    return y


def rounded(draw: ImageDraw.ImageDraw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def mix(a, b, amount: float):
    return tuple(round(a[i] * (1 - amount) + b[i] * amount) for i in range(3))


def make_canvas(background: tuple[int, int, int]) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (SIZE, SIZE), background)
    return image, ImageDraw.Draw(image)


def draw_grid(draw: ImageDraw.ImageDraw, color, step=68, alpha_mix=0.0):
    line = mix(color, NAVY if alpha_mix else WHITE, alpha_mix) if alpha_mix else color
    for x in range(0, SIZE + 1, step):
        draw.line((x, 0, x, SIZE), fill=line, width=1)
    for y in range(0, SIZE + 1, step):
        draw.line((0, y, SIZE, y), fill=line, width=1)


def header(draw: ImageDraw.ImageDraw, item: dict, number: int, dark: bool, accent):
    base = WHITE if dark else INK
    muted = mix(base, NAVY if dark else WHITE, 0.45)
    draw.text((MARGIN, 58), "FINLOG / EDITORIAL INTELLIGENCE", font=font(24, "bold"), fill=base)
    tag_face = font(22, "medium")
    tag = item["category"]
    tag_w = text_width(draw, tag, tag_face) + 38
    rounded(draw, (MARGIN, 106, MARGIN + tag_w, 152), 23, accent)
    draw.text((MARGIN + 19, 114), tag, font=tag_face, fill=NAVY)
    page = f"{number:02d} / 07"
    draw.text((SIZE - MARGIN - text_width(draw, page, font(24, "bold")), 66), page, font=font(24, "bold"), fill=base)
    draw.line((MARGIN, 181, SIZE - MARGIN, 181), fill=muted, width=2)


def footer(draw: ImageDraw.ImageDraw, item: dict, dark: bool):
    base = WHITE if dark else INK
    muted = mix(base, NAVY if dark else WHITE, 0.5)
    y = 1021
    draw.line((MARGIN, 997, SIZE - MARGIN, 997), fill=muted, width=1)
    draw.text((MARGIN, y), "PNU × FINLOG · 금융을 번역하는 사람들", font=font(19, "medium"), fill=muted)
    right = item["week"]
    draw.text((SIZE - MARGIN - text_width(draw, right, font(19, "medium")), y), right, font=font(19, "medium"), fill=muted)


def section_label(draw, text, xy, accent, dark=False):
    draw.ellipse((xy[0], xy[1] + 7, xy[0] + 14, xy[1] + 21), fill=accent)
    draw.text((xy[0] + 28, xy[1]), text, font=font(24, "bold"), fill=WHITE if dark else INK)


def render_cover(item: dict, accent) -> Image.Image:
    image, draw = make_canvas(NAVY)
    draw_grid(draw, (19, 43, 72), 72)
    # Structured editorial motif: two precise orbits and a data rail.
    draw.ellipse((610, 535, 1115, 1040), outline=mix(accent, NAVY, 0.2), width=4)
    draw.ellipse((735, 660, 990, 915), outline=mix(accent, NAVY, 0.55), width=2)
    for idx, height in enumerate((95, 160, 240, 125, 205)):
        x = 636 + idx * 74
        draw.rounded_rectangle((x, 928 - height, x + 30, 928), radius=15, fill=mix(accent, NAVY, idx * 0.08))
    header(draw, item, 1, True, accent)
    draw.text((MARGIN, 228), "RESEARCH CARD / 2026", font=font(24, "bold"), fill=accent)
    face, lines, spacing = fit_text(draw, item["title"], 820, 300, 78, 58, "bold", 0.16)
    y = 279
    for idx, line in enumerate(lines):
        draw.text((MARGIN, y), line, font=face, fill=WHITE)
        y += int(face.size * 1.12) + (spacing if idx < len(lines) - 1 else 0)
    draw.line((MARGIN, y + 35, MARGIN + 148, y + 35), fill=accent, width=8)
    draw_wrapped(draw, item["deck"], (MARGIN, y + 73), 700, 31, (205, 218, 231), "regular", 9)
    issue_no = f"{int(item['_index']):02d}"
    draw.text((MARGIN, 817), issue_no, font=font(104, "bold"), fill=mix(accent, NAVY, 0.24))
    draw.text((MARGIN + 155, 856), "ISSUE SERIES", font=font(27, "bold"), fill=WHITE)
    footer(draw, item, True)
    return image


def render_question(item: dict, accent) -> Image.Image:
    image, draw = make_canvas(PAPER)
    draw.text((735, 190), "02", font=font(230, "bold"), fill=(232, 230, 223))
    header(draw, item, 2, False, accent)
    section_label(draw, "THE QUESTION", (MARGIN, 225), accent)
    q = item["question"]
    face, lines, spacing = fit_text(draw, q["headline"], 820, 210, 61, 48, "bold", 0.13)
    y = 277
    for idx, line in enumerate(lines):
        draw.text((MARGIN, y), line, font=face, fill=INK)
        y += int(face.size * 1.12) + (spacing if idx < len(lines) - 1 else 0)
    y = draw_wrapped(draw, q["body"], (MARGIN, y + 34), 820, 29, MUTED, "regular", 8)
    y += 44
    for idx, bullet in enumerate(q["bullets"]):
        box_y = y + idx * 102
        rounded(draw, (MARGIN, box_y, SIZE - MARGIN, box_y + 82), 18, WHITE, LINE)
        rounded(draw, (MARGIN + 18, box_y + 16, MARGIN + 68, box_y + 66), 14, accent)
        num = str(idx + 1)
        draw.text((MARGIN + 36 - text_width(draw, num, font(22, "bold")) / 2, box_y + 24), num, font=font(22, "bold"), fill=NAVY)
        draw.text((MARGIN + 92, box_y + 22), bullet, font=font(27, "medium"), fill=INK)
    footer(draw, item, False)
    return image


def render_concept(item: dict, accent) -> Image.Image:
    image, draw = make_canvas(NAVY_2)
    draw_grid(draw, (22, 50, 83), 72)
    header(draw, item, 3, True, accent)
    section_label(draw, "HOW IT WORKS", (MARGIN, 225), accent, True)
    c = item["concept"]
    face, lines, spacing = fit_text(draw, c["headline"], 850, 170, 60, 47, "bold", 0.14)
    y = 276
    for idx, line in enumerate(lines):
        draw.text((MARGIN, y), line, font=face, fill=WHITE)
        y += int(face.size * 1.12) + (spacing if idx < len(lines) - 1 else 0)
    y = draw_wrapped(draw, c["body"], (MARGIN, y + 28), 850, 28, (191, 207, 224), "regular", 7)
    card_top = max(610, y + 52)
    card_w = 272
    gap = 55
    for idx, step in enumerate(c["steps"]):
        x = MARGIN + idx * (card_w + gap)
        rounded(draw, (x, card_top, x + card_w, 912), 25, (16, 44, 76), mix(accent, NAVY, 0.35), 2)
        draw.text((x + 26, card_top + 28), f"0{idx + 1}", font=font(25, "bold"), fill=accent)
        draw.text((x + 26, card_top + 82), step["title"], font=font(28, "bold"), fill=WHITE)
        draw_wrapped(draw, step["body"], (x + 26, card_top + 139), card_w - 52, 23, (190, 207, 225), "regular", 6)
        if idx < 2:
            arrow_x = x + card_w + 12
            draw.line((arrow_x, card_top + 145, arrow_x + 29, card_top + 145), fill=accent, width=3)
            draw.polygon([(arrow_x + 29, card_top + 145), (arrow_x + 19, card_top + 137), (arrow_x + 19, card_top + 153)], fill=accent)
    footer(draw, item, True)
    return image


def render_balance(item: dict, accent) -> Image.Image:
    image, draw = make_canvas(PAPER)
    header(draw, item, 4, False, accent)
    section_label(draw, "THE TRADE-OFF", (MARGIN, 225), accent)
    draw.text((MARGIN, 278), "기회와 위험을\n같은 화면에 놓기", font=font(58, "bold"), fill=INK, spacing=10)
    top = 470
    gap = 28
    col_w = (SIZE - 2 * MARGIN - gap) // 2
    columns = [
        ("OPPORTUNITY", "기회", item["balance"]["opportunity"], GREEN, mix(GREEN, WHITE, 0.9)),
        ("RISK", "위험", item["balance"]["risk"], RED, mix(RED, WHITE, 0.9)),
    ]
    for idx, (eng, kor, bullets, color, bg) in enumerate(columns):
        x = MARGIN + idx * (col_w + gap)
        rounded(draw, (x, top, x + col_w, 918), 28, bg, mix(color, WHITE, 0.5), 2)
        draw.text((x + 30, top + 28), eng, font=font(21, "bold"), fill=color)
        draw.text((x + 30, top + 71), kor, font=font(40, "bold"), fill=INK)
        draw.line((x + 30, top + 133, x + col_w - 30, top + 133), fill=mix(color, WHITE, 0.5), width=2)
        y = top + 174
        for bidx, bullet in enumerate(bullets):
            draw.ellipse((x + 31, y + 7, x + 45, y + 21), fill=color)
            y = draw_wrapped(draw, bullet, (x + 62, y), col_w - 94, 27, INK, "medium", 7) + 45
    footer(draw, item, False)
    return image


def render_signals(item: dict, accent) -> Image.Image:
    image, draw = make_canvas(NAVY)
    header(draw, item, 5, True, accent)
    section_label(draw, "DECISION SIGNALS", (MARGIN, 225), accent, True)
    s = item["signals"]
    face, lines, spacing = fit_text(draw, s["headline"], 850, 165, 59, 47, "bold", 0.12)
    y = 278
    for idx, line in enumerate(lines):
        draw.text((MARGIN, y), line, font=face, fill=WHITE)
        y += int(face.size * 1.12) + (spacing if idx < len(lines) - 1 else 0)
    y += 45
    for idx, signal in enumerate(s["items"]):
        box_y = y + idx * 155
        rounded(draw, (MARGIN, box_y, SIZE - MARGIN, box_y + 128), 22, (14, 40, 70), (37, 66, 96), 2)
        draw.text((MARGIN + 29, box_y + 23), f"0{idx + 1}", font=font(22, "bold"), fill=accent)
        label_x = MARGIN + 87
        draw.text((label_x, box_y + 19), signal["label"], font=font(25, "bold"), fill=WHITE)
        draw_wrapped(draw, signal["text"], (label_x, box_y + 61), 740, 24, (190, 207, 225), "regular", 5)
    footer(draw, item, True)
    return image


def render_career(item: dict, accent) -> Image.Image:
    image, draw = make_canvas(PAPER)
    header(draw, item, 6, False, accent)
    section_label(draw, "ROLE TRANSLATION", (MARGIN, 225), accent)
    c = item["career"]
    face, lines, spacing = fit_text(draw, c["headline"], 835, 176, 58, 46, "bold", 0.14)
    y = 278
    for idx, line in enumerate(lines):
        draw.text((MARGIN, y), line, font=face, fill=INK)
        y += int(face.size * 1.12) + (spacing if idx < len(lines) - 1 else 0)
    y = draw_wrapped(draw, c["body"], (MARGIN, y + 28), 835, 28, MUTED, "regular", 7)
    y += 52
    rail_x = MARGIN + 24
    draw.line((rail_x, y + 18, rail_x, y + 300), fill=mix(accent, WHITE, 0.45), width=4)
    for idx, action in enumerate(c["actions"]):
        cy = y + idx * 105
        draw.ellipse((rail_x - 14, cy, rail_x + 14, cy + 28), fill=accent)
        draw.text((MARGIN + 76, cy - 4), f"0{idx + 1}", font=font(22, "bold"), fill=accent)
        draw_wrapped(draw, action, (MARGIN + 135, cy - 7), 710, 28, INK, "medium", 7)
    rounded(draw, (MARGIN, 900, SIZE - MARGIN, 946), 23, INK)
    draw.text((MARGIN + 24, 910), "KNOWLEDGE → JUDGMENT → OUTPUT", font=font(21, "bold"), fill=WHITE)
    footer(draw, item, False)
    return image


def render_view(item: dict, accent) -> Image.Image:
    image, draw = make_canvas(NAVY_2)
    draw.ellipse((735, 150, 1140, 555), outline=mix(accent, NAVY, 0.35), width=3)
    draw.ellipse((810, 225, 1065, 480), outline=mix(accent, NAVY, 0.58), width=2)
    header(draw, item, 7, True, accent)
    section_label(draw, "FINLOG VIEW", (MARGIN, 225), accent, True)
    v = item["view"]
    face, lines, spacing = fit_text(draw, v["conclusion"], 860, 195, 57, 44, "bold", 0.14)
    y = 278
    for idx, line in enumerate(lines):
        draw.text((MARGIN, y), line, font=face, fill=WHITE)
        y += int(face.size * 1.12) + (spacing if idx < len(lines) - 1 else 0)
    y += 35
    draw.line((MARGIN, y, MARGIN + 132, y), fill=accent, width=7)
    y += 35
    for idx, takeaway in enumerate(v["takeaways"]):
        draw.text((MARGIN, y), f"0{idx + 1}", font=font(22, "bold"), fill=accent)
        y = draw_wrapped(draw, takeaway, (MARGIN + 66, y - 3), 790, 25, (211, 223, 234), "medium", 6) + 18
    terms_y = 760
    draw.text((MARGIN, terms_y), "KEY TERMS", font=font(21, "bold"), fill=accent)
    draw.line((MARGIN, terms_y + 40, SIZE - MARGIN, terms_y + 40), fill=(48, 75, 102), width=1)
    col_w = (SIZE - 2 * MARGIN - 30) // 3
    for idx, term in enumerate(v["terms"]):
        x = MARGIN + idx * (col_w + 15)
        draw.text((x, terms_y + 61), term["term"], font=font(20, "bold"), fill=WHITE)
        draw_wrapped(draw, term["definition"], (x, terms_y + 98), col_w - 10, 19, (161, 183, 204), "regular", 5)
    draw.text((MARGIN, 960), "학습용 요약 · 기준시점 2026년 상반기 · 투자 권유 아님", font=font(18, "medium"), fill=(131, 155, 179))
    footer(draw, item, True)
    return image


RENDERERS = [render_cover, render_question, render_concept, render_balance, render_signals, render_career, render_view]


def validate_content(items: list[dict]) -> None:
    if len(items) != 24:
        raise ValueError(f"Expected 24 sets, found {len(items)}")
    slugs = [item["slug"] for item in items]
    if len(set(slugs)) != len(slugs):
        raise ValueError("Duplicate slug in card content")
    for item in items:
        if len(item["question"]["bullets"]) != 3:
            raise ValueError(f"{item['slug']}: question needs 3 bullets")
        if len(item["concept"]["steps"]) != 3:
            raise ValueError(f"{item['slug']}: concept needs 3 steps")
        if len(item["balance"]["opportunity"]) != 2 or len(item["balance"]["risk"]) != 2:
            raise ValueError(f"{item['slug']}: balance needs 2 + 2 items")
        if len(item["signals"]["items"]) != 3:
            raise ValueError(f"{item['slug']}: signals needs 3 items")
        if len(item["career"]["actions"]) != 3:
            raise ValueError(f"{item['slug']}: career needs 3 actions")
        if len(item["view"]["takeaways"]) != 3 or len(item["view"]["terms"]) != 3:
            raise ValueError(f"{item['slug']}: view needs 3 takeaways and terms")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="Render one slug for visual iteration")
    parser.add_argument("--quality", type=int, default=92, help="Reserved for future WebP output")
    args = parser.parse_args()

    project = Path(__file__).resolve().parents[1]
    data_path = project / "cards_content.json"
    out_dir = project / "cards"
    items = json.loads(data_path.read_text(encoding="utf-8"))
    validate_content(items)
    out_dir.mkdir(parents=True, exist_ok=True)

    rendered = 0
    for index, item in enumerate(items, start=1):
        if args.only and item["slug"] != args.only:
            continue
        item["_index"] = index
        accent = CATEGORY_ACCENTS.get(item["category"], CYAN)
        for card_no, renderer in enumerate(RENDERERS, start=1):
            image = renderer(item, accent)
            output = out_dir / f"{item['slug']}_{card_no:02d}.png"
            image.save(output, format="PNG", optimize=True, compress_level=9)
            rendered += 1
    print(f"Rendered {rendered} cards to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
