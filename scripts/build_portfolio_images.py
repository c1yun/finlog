"""Build deterministic FinLog portfolio and social-preview images."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = Path("C:/Windows/Fonts")


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        FONT_DIR / ("malgunbd.ttf" if bold else "malgun.ttf"),
        FONT_DIR / ("arialbd.ttf" if bold else "arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def add_grid(draw: ImageDraw.ImageDraw, size: tuple[int, int], step: int, color: tuple[int, int, int]) -> None:
    width, height = size
    for x in range(0, width, step):
        draw.line((x, 0, x, height), fill=color, width=1)
    for y in range(0, height, step):
        draw.line((0, y, width, y), fill=color, width=1)


def paste_card(canvas: Image.Image, source: Path, box: int, position: tuple[int, int], angle: float) -> None:
    card = Image.open(source).convert("RGB").resize((box, box), Image.Resampling.LANCZOS)
    card = card.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True, fillcolor=(5, 8, 13))
    shadow = Image.new("RGBA", card.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((18, 18, card.width - 4, card.height - 4), radius=22, fill=(0, 0, 0, 175))
    shadow = shadow.filter(ImageFilter.GaussianBlur(20))
    x, y = position
    canvas.alpha_composite(shadow, (x + 14, y + 20))
    canvas.alpha_composite(card.convert("RGBA"), (x, y))


def build_card_news_preview() -> Path:
    output = ROOT / "assets/images/portfolio/card-news-v2.webp"
    canvas = Image.new("RGBA", (1400, 900), (5, 8, 13, 255))
    draw = ImageDraw.Draw(canvas)
    add_grid(draw, canvas.size, 72, (18, 37, 58))
    draw.rectangle((0, 0, 1400, 92), fill=(8, 14, 22))
    draw.line((0, 91, 1400, 91), fill=(34, 48, 68), width=2)
    draw.text((64, 27), "FINLOG / LEARNING ARCHIVE", font=font(27, bold=True), fill=(242, 246, 251))
    draw.text((1060, 32), "24 SETS / 168 CARDS", font=font(19, bold=True), fill=(98, 215, 255))

    sources = [
        ROOT / "cards/stablecoin_01.png",
        ROOT / "cards/ai-fairness_01.png",
        ROOT / "cards/hbm_01.png",
    ]
    paste_card(canvas, sources[0], 520, (70, 218), -4)
    paste_card(canvas, sources[1], 560, (425, 143), 0)
    paste_card(canvas, sources[2], 520, (840, 218), 4)
    draw.rounded_rectangle((70, 786, 1330, 842), radius=9, fill=(7, 12, 19), outline=(52, 71, 96), width=2)
    draw.text((94, 803), "QUESTION  →  STRUCTURE  →  ISSUE  →  EVIDENCE  →  JUDGEMENT", font=font(18, bold=True), fill=(214, 179, 106))
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output, "WEBP", quality=88, method=6)
    return output


def build_social_preview() -> Path:
    output = ROOT / "og-v2.png"
    canvas = Image.new("RGB", (1200, 630), (5, 8, 13))
    draw = ImageDraw.Draw(canvas)
    add_grid(draw, canvas.size, 48, (12, 28, 44))
    draw.rectangle((0, 0, 1200, 9), fill=(98, 215, 255))

    draw.text((72, 55), "FINLOG / LEARNING ARCHIVE", font=font(25, bold=True), fill=(98, 215, 255))
    draw.text((72, 126), "함께 공부하고,", font=font(58, bold=True), fill=(242, 246, 251))
    draw.text((72, 204), "기록으로 남겼습니다", font=font(58, bold=True), fill=(242, 246, 251))
    draw.text((72, 300), "공식 자료 확인 · 팀 토론 · 교차 검토 · 웹 기록", font=font(24), fill=(150, 167, 188))

    metrics = [("108", "TERMS"), ("168", "CARDS"), ("86", "PAGES"), ("6", "MEMBERS")]
    x = 72
    for number, label in metrics:
        draw.text((x, 395), number, font=font(36, bold=True), fill=(242, 246, 251))
        draw.text((x, 443), label, font=font(16, bold=True), fill=(214, 179, 106))
        x += 142

    panel = (760, 72, 1128, 548)
    draw.rounded_rectangle(panel, radius=18, fill=(8, 14, 22), outline=(52, 71, 96), width=2)
    draw.line((760, 126, 1128, 126), fill=(34, 48, 68), width=2)
    draw.text((786, 91), "EDITORIAL FLOW", font=font(17, bold=True), fill=(150, 167, 188))
    draw.ellipse((1066, 94, 1080, 108), fill=(96, 214, 177))
    draw.text((1088, 91), "PASS", font=font(14, bold=True), fill=(96, 214, 177))

    rows = [
        ("01", "SOURCE", "공식 자료 확인"),
        ("02", "NORMALIZE", "지식·이미지 구조화"),
        ("03", "REVIEW", "교차 검토"),
        ("04", "PUBLISH", "웹 아카이브 발행"),
    ]
    y = 154
    for number, title, description in rows:
        draw.ellipse((788, y + 4, 822, y + 38), outline=(98, 215, 255), width=2)
        draw.text((797, y + 10), number, font=font(12, bold=True), fill=(98, 215, 255))
        draw.text((844, y), title, font=font(17, bold=True), fill=(232, 239, 247))
        draw.text((844, y + 25), description, font=font(15), fill=(150, 167, 188))
        if number != "04":
            draw.line((805, y + 41, 805, y + 72), fill=(52, 71, 96), width=2)
        y += 88

    draw.line((72, 526, 690, 526), fill=(34, 48, 68), width=2)
    draw.text((72, 551), "PNU · ONGOING", font=font(20, bold=True), fill=(214, 179, 106))
    draw.text((270, 553), "c1yun.github.io/finlog", font=font(18), fill=(111, 132, 157))
    canvas.save(output, "PNG", optimize=True)
    return output


def main() -> None:
    for output in (build_card_news_preview(), build_social_preview()):
        print(f"built {output.relative_to(ROOT)} ({output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
