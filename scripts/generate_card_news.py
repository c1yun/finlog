#!/usr/bin/env python3
"""Render FinLog's 24 x 7 card-news system from its original structured data.

The renderer never rewrites editorial copy. Every title, explanation, signal,
and conclusion is read from cards_content.json and placed into a reproducible
banking-research visual system.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo


SIZE = 1080
RAIL = 42
LEFT = 82
RIGHT = 78
CONTENT_W = SIZE - LEFT - RIGHT

MIDNIGHT = (8, 24, 43)
NAVY = (14, 38, 66)
INK = (19, 35, 51)
SLATE = (82, 98, 113)
PAPER = (247, 246, 242)
CLOUD = (237, 241, 243)
WHITE = (255, 255, 255)
LINE = (207, 214, 218)
GOLD = (188, 148, 77)
GREEN = (49, 124, 99)
RED = (169, 76, 72)
CYAN = (73, 151, 183)
RENDERER_VERSION = "finlog-research-note-2.1"

FONT_REGULAR = Path("C:/Windows/Fonts/NotoSansKR-Regular.ttf")
FONT_MEDIUM = Path("C:/Windows/Fonts/NotoSansKR-Medium.ttf")
FONT_BOLD = Path("C:/Windows/Fonts/NotoSansKR-Bold.ttf")

CATEGORY_ACCENTS = {
    "플랫폼·규제": (71, 139, 166),
    "정책·기후금융": (62, 133, 105),
    "사회·금융포용": (178, 126, 72),
    "자본시장": (67, 113, 169),
    "무역·거시경제": (175, 123, 68),
    "사회·조직": (137, 96, 145),
    "자본시장 인프라": (54, 136, 144),
    "디지털금융": (81, 105, 172),
    "커리어 인사이트": (166, 129, 65),
    "현장·자본시장": (65, 133, 112),
    "산업·기업금융": (66, 116, 170),
    "ESG·기후금융": (53, 128, 91),
    "기업가치·거버넌스": (151, 111, 60),
    "노동·거시경제": (164, 91, 69),
    "AI·금융윤리": (104, 88, 173),
    "AI·시장감시": (58, 127, 158),
    "신용·금융포용": (48, 129, 106),
    "파생·리스크관리": (158, 78, 75),
    "회계·기업분석": (58, 111, 153),
    "레그테크·준법": (80, 105, 159),
    "현장·디지털금융": (55, 132, 132),
}


def font(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
    path = {"regular": FONT_REGULAR, "medium": FONT_MEDIUM, "bold": FONT_BOLD}[weight]
    if not path.exists():
        raise FileNotFoundError(f"Required Korean font not found: {path}")
    return ImageFont.truetype(str(path), size=size)


def text_width(draw: ImageDraw.ImageDraw, value: str, face: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), value, font=face)
    return box[2] - box[0]


def mix(a: tuple[int, int, int], b: tuple[int, int, int], amount: float):
    return tuple(round(a[i] * (1 - amount) + b[i] * amount) for i in range(3))


def rounded(draw: ImageDraw.ImageDraw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def wrap_text(draw: ImageDraw.ImageDraw, value: str, face: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in value.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        current = ""
        for word in paragraph.split(" "):
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
    gap_ratio: float = 0.16,
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    for size in range(start_size, min_size - 1, -2):
        face = font(size, weight)
        lines = wrap_text(draw, value, face, width)
        gap = max(6, int(size * gap_ratio))
        height = len(lines) * int(size * 1.16) + max(0, len(lines) - 1) * gap
        if height <= max_height:
            return face, lines, gap
    face = font(min_size, weight)
    return face, wrap_text(draw, value, face, width), max(6, int(min_size * gap_ratio))


def draw_fitted(
    draw: ImageDraw.ImageDraw,
    value: str,
    xy: tuple[int, int],
    width: int,
    max_height: int,
    start_size: int,
    min_size: int,
    fill,
    weight: str = "bold",
    gap_ratio: float = 0.16,
) -> int:
    face, lines, gap = fit_text(draw, value, width, max_height, start_size, min_size, weight, gap_ratio)
    y = xy[1]
    for idx, line in enumerate(lines):
        draw.text((xy[0], y), line, font=face, fill=fill)
        y += int(face.size * 1.16)
        if idx < len(lines) - 1:
            y += gap
    return y


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    value: str,
    xy: tuple[int, int],
    width: int,
    size: int,
    fill,
    weight: str = "regular",
    gap: int = 7,
) -> int:
    face = font(size, weight)
    lines = wrap_text(draw, value, face, width)
    y = xy[1]
    for idx, line in enumerate(lines):
        draw.text((xy[0], y), line, font=face, fill=fill)
        y += int(size * 1.16)
        if idx < len(lines) - 1:
            y += gap
    return y


def canvas(background):
    image = Image.new("RGB", (SIZE, SIZE), background)
    return image, ImageDraw.Draw(image)


def grid(draw: ImageDraw.ImageDraw, color, step=62, area=(0, 0, SIZE, SIZE)):
    left, top, right, bottom = area
    for x in range(left, right + 1, step):
        draw.line((x, top, x, bottom), fill=color, width=1)
    for y in range(top, bottom + 1, step):
        draw.line((left, y, right, y), fill=color, width=1)


def chrome(draw: ImageDraw.ImageDraw, item: dict, number: int, dark: bool, accent):
    base = WHITE if dark else INK
    muted = (164, 181, 196) if dark else SLATE
    draw.rectangle((0, 0, RAIL, SIZE), fill=accent)
    draw.text((LEFT, 54), "FINLOG / RESEARCH NOTE", font=font(23, "bold"), fill=base)
    issue = f"ISSUE {item['_index']:02d}"
    draw.text((LEFT, 92), issue, font=font(16, "bold"), fill=muted)

    page = f"{number:02d} / 07"
    page_face = font(23, "bold")
    draw.text((SIZE - RIGHT - text_width(draw, page, page_face), 56), page, font=page_face, fill=base)
    draw.line((LEFT, 137, SIZE - RIGHT, 137), fill=(50, 70, 90) if dark else LINE, width=2)

    tag_face = font(18, "medium")
    tag_w = text_width(draw, item["category"], tag_face) + 34
    rounded(draw, (LEFT, 157, LEFT + tag_w, 197), 8, mix(accent, WHITE, 0.08) if dark else mix(accent, WHITE, 0.82))
    draw.text((LEFT + 17, 165), item["category"], font=tag_face, fill=WHITE if dark else INK)


def section(draw: ImageDraw.ImageDraw, eyebrow: str, title: str, dark: bool, accent, y=224):
    base = WHITE if dark else INK
    draw.rectangle((LEFT, y + 3, LEFT + 7, y + 31), fill=accent)
    draw.text((LEFT + 22, y), eyebrow, font=font(18, "bold"), fill=accent)
    draw.text((LEFT + 22, y + 37), title, font=font(27, "bold"), fill=base)


def sequence(draw: ImageDraw.ImageDraw, active: int, dark: bool, accent, y=927):
    inactive = (65, 84, 103) if dark else (198, 205, 209)
    base = WHITE if dark else INK
    width = 76
    gap = 14
    for idx in range(7):
        x = LEFT + idx * (width + gap)
        fill = accent if idx + 1 == active else inactive
        draw.rectangle((x, y, x + width, y + 5), fill=fill)
        draw.text((x, y + 14), f"0{idx + 1}", font=font(15, "bold"), fill=base if idx + 1 == active else inactive)


def footer(draw: ImageDraw.ImageDraw, item: dict, dark: bool):
    base = (154, 173, 190) if dark else SLATE
    draw.line((LEFT, 1004, SIZE - RIGHT, 1004), fill=(49, 69, 88) if dark else LINE, width=1)
    source_note = f"자료 ID {item['slug']} · 검토 2026.07.16 · 투자 권유 아님"
    draw.text((LEFT, 1022), source_note, font=font(16, "medium"), fill=base)
    right = item["week"]
    right_face = font(16, "medium")
    draw.text((SIZE - RIGHT - text_width(draw, right, right_face), 1022), right, font=right_face, fill=base)


def render_cover(item: dict, accent) -> Image.Image:
    image, draw = canvas(MIDNIGHT)
    grid(draw, (15, 39, 62), 66, (510, 205, SIZE, 875))
    draw.rectangle((510, 205, SIZE, 875), outline=(34, 57, 79), width=2)
    draw.text((594, 232), f"{item['_index']:02d}", font=font(310, "bold"), fill=mix(accent, MIDNIGHT, 0.68))
    for idx, value in enumerate((0.35, 0.62, 0.48, 0.78, 0.57)):
        x = 640 + idx * 65
        top = 738 - int(value * 170)
        draw.rectangle((x, top, x + 22, 738), fill=mix(accent, MIDNIGHT, 0.2 + idx * 0.08))
    chrome(draw, item, 1, True, accent)
    draw.text((LEFT, 231), "ORIGINAL DATA BRIEF", font=font(19, "bold"), fill=accent)
    y = draw_fitted(draw, item["title"], (LEFT, 282), 785, 265, 76, 55, WHITE)
    draw.rectangle((LEFT, y + 24, LEFT + 118, y + 31), fill=accent)
    draw_wrapped(draw, item["deck"], (LEFT, y + 60), 720, 29, (205, 216, 227), "regular", 8)

    rounded(draw, (LEFT, 787, 488, 868), 12, NAVY, (48, 69, 91), 1)
    draw.text((LEFT + 22, 805), "DATA LINEAGE", font=font(16, "bold"), fill=accent)
    draw.text((LEFT + 22, 836), "cards_content.json / 7-card system", font=font(18, "medium"), fill=WHITE)
    sequence(draw, 1, True, accent)
    footer(draw, item, True)
    return image


def render_question(item: dict, accent) -> Image.Image:
    image, draw = canvas(PAPER)
    chrome(draw, item, 2, False, accent)
    section(draw, "01 / ISSUE DEFINITION", "무엇을 판단해야 하는가", False, accent)
    q = item["question"]
    y = draw_fitted(draw, q["headline"], (LEFT, 325), CONTENT_W, 156, 58, 44, INK)
    rounded(draw, (LEFT, y + 25, SIZE - RIGHT, y + 142), 12, WHITE, LINE, 1)
    draw.text((LEFT + 22, y + 43), "CONTEXT", font=font(16, "bold"), fill=accent)
    draw_wrapped(draw, q["body"], (LEFT + 132, y + 40), CONTENT_W - 165, 25, SLATE, "regular", 6)

    top = max(600, y + 177)
    for idx, bullet in enumerate(q["bullets"]):
        box_y = top + idx * 92
        draw.line((LEFT, box_y + 78, SIZE - RIGHT, box_y + 78), fill=LINE, width=1)
        rounded(draw, (LEFT, box_y, LEFT + 62, box_y + 62), 10, mix(accent, WHITE, 0.82))
        draw.text((LEFT + 17, box_y + 13), f"0{idx + 1}", font=font(20, "bold"), fill=accent)
        draw_wrapped(draw, bullet, (LEFT + 87, box_y + 8), CONTENT_W - 87, 26, INK, "medium", 5)
    sequence(draw, 2, False, accent)
    footer(draw, item, False)
    return image


def render_concept(item: dict, accent) -> Image.Image:
    image, draw = canvas(CLOUD)
    chrome(draw, item, 3, False, accent)
    section(draw, "02 / MECHANISM", "구조와 작동 원리", False, accent)
    c = item["concept"]
    y = draw_fitted(draw, c["headline"], (LEFT, 325), CONTENT_W, 145, 56, 43, INK)
    y = draw_wrapped(draw, c["body"], (LEFT, y + 18), CONTENT_W, 25, SLATE, "regular", 6)
    top = max(575, y + 32)
    for idx, step in enumerate(c["steps"]):
        box_y = top + idx * 108
        rounded(draw, (LEFT, box_y, SIZE - RIGHT, box_y + 88), 12, WHITE, LINE, 1)
        draw.rectangle((LEFT, box_y, LEFT + 13, box_y + 88), fill=accent)
        draw.text((LEFT + 34, box_y + 17), f"0{idx + 1}", font=font(19, "bold"), fill=accent)
        draw.text((LEFT + 105, box_y + 13), step["title"], font=font(26, "bold"), fill=INK)
        draw_wrapped(draw, step["body"], (LEFT + 290, box_y + 13), CONTENT_W - 315, 22, SLATE, "regular", 5)
        if idx < 2:
            draw.line((LEFT + 64, box_y + 88, LEFT + 64, box_y + 108), fill=accent, width=3)
    sequence(draw, 3, False, accent)
    footer(draw, item, False)
    return image


def render_balance(item: dict, accent) -> Image.Image:
    image, draw = canvas(PAPER)
    chrome(draw, item, 4, False, accent)
    section(draw, "03 / BALANCE SHEET", "기회와 위험을 함께 읽기", False, accent)
    draw_wrapped(draw, "한 방향의 주장보다 조건과 상충관계를 함께 확인합니다.", (LEFT, 323), CONTENT_W, 28, SLATE, "regular", 7)

    gap = 24
    top = 410
    col_w = (CONTENT_W - gap) // 2
    columns = [
        ("OPPORTUNITY", "기회", item["balance"]["opportunity"], GREEN),
        ("RISK", "위험", item["balance"]["risk"], RED),
    ]
    for idx, (eng, kor, bullets, color) in enumerate(columns):
        x = LEFT + idx * (col_w + gap)
        rounded(draw, (x, top, x + col_w, 882), 16, WHITE, mix(color, WHITE, 0.58), 2)
        draw.rectangle((x, top, x + col_w, top + 10), fill=color)
        draw.text((x + 26, top + 31), eng, font=font(17, "bold"), fill=color)
        draw.text((x + 26, top + 66), kor, font=font(40, "bold"), fill=INK)
        draw.line((x + 26, top + 127, x + col_w - 26, top + 127), fill=LINE, width=1)
        item_y = top + 161
        for bidx, bullet in enumerate(bullets):
            draw.text((x + 27, item_y), f"0{bidx + 1}", font=font(18, "bold"), fill=color)
            item_y = draw_wrapped(draw, bullet, (x + 77, item_y - 3), col_w - 104, 25, INK, "medium", 6) + 50
    sequence(draw, 4, False, accent)
    footer(draw, item, False)
    return image


def render_signals(item: dict, accent) -> Image.Image:
    image, draw = canvas(MIDNIGHT)
    grid(draw, (14, 37, 59), 66, (580, 0, SIZE, SIZE))
    chrome(draw, item, 5, True, accent)
    section(draw, "04 / REVIEW GRID", "판단 전에 확인할 신호", True, accent)
    s = item["signals"]
    y = draw_fitted(draw, s["headline"], (LEFT, 325), CONTENT_W, 145, 55, 43, WHITE)
    top = max(535, y + 30)
    for idx, signal in enumerate(s["items"]):
        box_y = top + idx * 121
        rounded(draw, (LEFT, box_y, SIZE - RIGHT, box_y + 100), 12, NAVY, (45, 68, 89), 1)
        draw.text((LEFT + 24, box_y + 21), f"CHECK {idx + 1:02d}", font=font(16, "bold"), fill=accent)
        draw.text((LEFT + 155, box_y + 17), signal["label"], font=font(23, "bold"), fill=WHITE)
        draw_wrapped(draw, signal["text"], (LEFT + 335, box_y + 16), CONTENT_W - 360, 21, (194, 207, 219), "regular", 5)
    sequence(draw, 5, True, accent)
    footer(draw, item, True)
    return image


def render_career(item: dict, accent) -> Image.Image:
    image, draw = canvas(PAPER)
    chrome(draw, item, 6, False, accent)
    section(draw, "05 / ROLE LENS", "금융 직무의 언어로 연결하기", False, accent)
    c = item["career"]
    y = draw_fitted(draw, c["headline"], (LEFT, 325), CONTENT_W, 140, 55, 43, INK)
    y = draw_wrapped(draw, c["body"], (LEFT, y + 20), CONTENT_W, 24, SLATE, "regular", 6)
    top = max(595, y + 36)
    for idx, action in enumerate(c["actions"]):
        box_y = top + idx * 88
        draw.text((LEFT, box_y + 6), f"0{idx + 1}", font=font(18, "bold"), fill=accent)
        draw.line((LEFT + 52, box_y + 17, LEFT + 103, box_y + 17), fill=accent, width=3)
        draw_wrapped(draw, action, (LEFT + 130, box_y), CONTENT_W - 130, 26, INK, "medium", 5)
    rounded(draw, (LEFT, 861, SIZE - RIGHT, 909), 8, INK)
    draw.text((LEFT + 20, 873), "KNOWLEDGE   →   JUDGMENT   →   COMMUNICATION", font=font(18, "bold"), fill=WHITE)
    sequence(draw, 6, False, accent)
    footer(draw, item, False)
    return image


def render_view(item: dict, accent) -> Image.Image:
    image, draw = canvas(NAVY)
    grid(draw, (19, 46, 75), 66, (620, 190, SIZE, 740))
    chrome(draw, item, 7, True, accent)
    section(draw, "06 / FINLOG VIEW", "정리와 핵심 용어", True, accent)
    v = item["view"]
    y = draw_fitted(draw, v["conclusion"], (LEFT, 325), CONTENT_W, 175, 54, 41, WHITE)
    draw.rectangle((LEFT, y + 19, LEFT + 110, y + 25), fill=GOLD)
    take_y = y + 52
    for idx, takeaway in enumerate(v["takeaways"]):
        draw.text((LEFT, take_y + 2), f"0{idx + 1}", font=font(18, "bold"), fill=accent)
        take_y = draw_wrapped(draw, takeaway, (LEFT + 56, take_y), CONTENT_W - 56, 23, (213, 223, 232), "medium", 5) + 14

    terms_top = 748
    draw.text((LEFT, terms_top), "KEY TERMS / ORIGINAL DATA", font=font(17, "bold"), fill=GOLD)
    draw.line((LEFT, terms_top + 35, SIZE - RIGHT, terms_top + 35), fill=(55, 78, 99), width=1)
    col_gap = 18
    col_w = (CONTENT_W - col_gap * 2) // 3
    for idx, term in enumerate(v["terms"]):
        x = LEFT + idx * (col_w + col_gap)
        draw.text((x, terms_top + 57), term["term"], font=font(18, "bold"), fill=WHITE)
        draw_wrapped(draw, term["definition"], (x, terms_top + 92), col_w - 8, 17, (164, 183, 199), "regular", 4)
    sequence(draw, 7, True, accent)
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
            raise ValueError(f"{item['slug']}: view needs 3 takeaways and 3 terms")


def png_metadata(item: dict, card_no: int, source_hash: str) -> PngInfo:
    info = PngInfo()
    info.add_text("Title", item["title"])
    info.add_text("Source", f"cards_content.json#{item['slug']}")
    info.add_text("SourceSHA256", source_hash)
    info.add_text("Card", f"{card_no}/7")
    info.add_text("Renderer", RENDERER_VERSION)
    return info


def write_manifest(project: Path, source_hash: str, items: list[dict]):
    manifest = {
        "schema_version": RENDERER_VERSION,
        "source": "cards_content.json",
        "source_sha256": source_hash,
        "sets": len(items),
        "cards_per_set": len(RENDERERS),
        "rendered_cards": len(items) * len(RENDERERS),
        "dimensions": [SIZE, SIZE],
        "copy_policy": "verbatim-from-structured-source",
    }
    (project / "cards_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="Render one slug for visual iteration")
    args = parser.parse_args()

    project = Path(__file__).resolve().parents[1]
    data_path = project / "cards_content.json"
    out_dir = project / "cards"
    source_bytes = data_path.read_bytes()
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    items = json.loads(source_bytes.decode("utf-8"))
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
            image.save(
                output,
                format="PNG",
                optimize=True,
                compress_level=9,
                pnginfo=png_metadata(item, card_no, source_hash),
            )
            if card_no == 1:
                thumb_dir = out_dir / "thumbs"
                thumb_dir.mkdir(parents=True, exist_ok=True)
                thumb = image.copy()
                thumb.thumbnail((560, 560), Image.Resampling.LANCZOS)
                thumb.convert("RGB").save(
                    thumb_dir / f"{item['slug']}_01.webp",
                    format="WEBP",
                    quality=84,
                    method=6,
                )
            rendered += 1

    if not args.only:
        write_manifest(project, source_hash, items)
    print(f"Rendered {rendered} cards from cards_content.json with {RENDERER_VERSION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
