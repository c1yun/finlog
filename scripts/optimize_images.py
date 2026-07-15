"""Extract embedded FinLog images and build lightweight browse thumbnails.

Run from the repository root. The transformation is deterministic and safe to
re-run: after data URIs are replaced, it only refreshes the card cover
thumbnails and static image dimensions.
"""

from __future__ import annotations

import base64
import hashlib
import io
import re
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DATA_URI = re.compile(r"data:image/(png|jpeg|jpg);base64,([A-Za-z0-9+/=]+)")
IMG_TAG = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
SRC_ATTR = re.compile(r"\bsrc=(['\"])(.*?)\1", re.IGNORECASE)

# Hashes identify the original embedded files without depending on document
# order. Human-readable names make later content work and accessibility audits
# much easier than opaque generated filenames.
ASSET_MAP = {
    "4e832f042e": ("assets/images/brand/finlog-mark.png", "png"),
    "c90c8ee48b": ("assets/images/brand/finlog-mark-small.png", "png"),
    "3e263848b7": ("assets/images/chatbot/goma-avatar.png", "png"),
    "d0c4b7d5bb": ("assets/images/chatbot/orso-avatar.png", "png"),
    "5187907d14": ("assets/images/chatbot/goma-full.png", "png"),
    "feaf28d042": ("assets/images/chatbot/orso-full.png", "png"),
    "e6c9d7e5d6": ("assets/images/portfolio/digital-finance-forum.webp", "webp"),
    "72b6a80e5f": ("assets/images/portfolio/card-news.webp", "webp"),
    "2b3392a911": ("assets/images/portfolio/finance-chatbot.webp", "webp"),
    "c8be785d78": ("assets/images/portfolio/topic-reports.webp", "webp"),
    "5555b0112a": ("assets/images/portfolio/content-hub.webp", "webp"),
    "cecf0543b9": ("assets/images/portfolio/ai-playbook.webp", "webp"),
    "241597a9d5": ("assets/images/portfolio/krx-museum.webp", "webp"),
    "310d0cbb63": ("assets/images/portfolio/professional-interviews.webp", "webp"),
    "7aebd1934e": ("assets/images/portfolio/interview-prep.webp", "webp"),
    "d75816a417": ("assets/images/field/digital-finance-forum.webp", "webp"),
    "d1036d2d0c": ("assets/images/field/krx-history-gallery.webp", "webp"),
    "224824f3f1": ("assets/images/field/krx-market-gallery.webp", "webp"),
    "750a28d4f9": ("assets/images/field/finlog-team.webp", "webp"),
    "cc4dc529e4": ("assets/images/forum/venue-hero.webp", "webp"),
    "2479985740": ("assets/images/forum/venue.webp", "webp"),
    "8005a3c03d": ("assets/images/forum/opening-welcome.webp", "webp"),
    "6dc48ba67c": ("assets/images/forum/congratulatory-han-ingu.webp", "webp"),
    "d1a7d7e26e": ("assets/images/forum/congratulatory-kim-youngjae.webp", "webp"),
    "66ef86dc08": ("assets/images/forum/congratulatory-lee-myeongho.webp", "webp"),
    "4689cfcc44": ("assets/images/forum/digital-finance-awards.webp", "webp"),
    "2a434a021d": ("assets/images/forum/awards-stage.webp", "webp"),
    "faf5293fd1": ("assets/images/forum/panel-discussion.webp", "webp"),
    "c3ebde8812": ("assets/images/forum/networking-dinner.webp", "webp"),
}

# The workspace also contains camera originals for these exact embedded crops.
# Prefer them for the forum hero and zoom viewer, but cap the long edge so the
# GitHub Pages payload stays modest.
HIGH_RES_SOURCES = {
    "assets/images/forum/venue-hero.webp": "KakaoTalk_20260707_101509784.jpg",
    "assets/images/forum/venue.webp": "사진1.jpg",
    "assets/images/forum/opening-welcome.webp": "KakaoTalk_20260707_101509784_01.jpg",
    "assets/images/forum/congratulatory-han-ingu.webp": "KakaoTalk_20260707_101509784_02.jpg",
    "assets/images/forum/congratulatory-kim-youngjae.webp": "KakaoTalk_20260707_101509784_03.jpg",
    "assets/images/forum/congratulatory-lee-myeongho.webp": "KakaoTalk_20260707_101509784_04.jpg",
    "assets/images/forum/digital-finance-awards.webp": "KakaoTalk_20260707_101509784_05.jpg",
    "assets/images/forum/awards-stage.webp": "KakaoTalk_20260707_101509784_06.jpg",
}


def save_asset(raw: bytes, relative_path: str, kind: str) -> None:
    target = ROOT / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(io.BytesIO(raw)) as image:
        image.load()
        if kind == "png":
            image.save(target, format="PNG", optimize=True)
            return
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGB")
        image.save(target, format="WEBP", quality=84, method=6)


def extract_embedded_images() -> tuple[int, int]:
    created: set[str] = set()
    replacements = 0
    for html_path in sorted(ROOT.glob("*.html")):
        source = html_path.read_text(encoding="utf-8")

        def replace(match: re.Match[str]) -> str:
            nonlocal replacements
            raw = base64.b64decode(match.group(2))
            digest = hashlib.sha256(raw).hexdigest()[:10]
            mapped = ASSET_MAP.get(digest)
            if not mapped:
                raise RuntimeError(f"Unmapped embedded image {digest} in {html_path.name}")
            relative_path, kind = mapped
            if relative_path not in created:
                save_asset(raw, relative_path, kind)
                created.add(relative_path)
            replacements += 1
            return relative_path

        updated = DATA_URI.sub(replace, source)
        if updated != source:
            html_path.write_text(updated, encoding="utf-8", newline="\n")
    return len(created), replacements


def build_card_cover_thumbnails() -> int:
    source_dir = ROOT / "cards"
    target_dir = source_dir / "thumbs"
    target_dir.mkdir(exist_ok=True)
    count = 0
    for source in sorted(source_dir.glob("*_01.png")):
        target = target_dir / f"{source.stem}.webp"
        with Image.open(source) as image:
            image.thumbnail((560, 560), Image.Resampling.LANCZOS)
            image.save(target, format="WEBP", quality=82, method=6)
        count += 1
    return count


def upgrade_forum_photos() -> int:
    source_root = ROOT.parents[1]
    count = 0
    for relative_target, source_name in HIGH_RES_SOURCES.items():
        source = source_root / source_name
        if not source.is_file():
            continue
        target = ROOT / relative_target
        target.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(source) as image:
            from PIL import ImageOps

            image = ImageOps.exif_transpose(image).convert("RGB")
            image.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
            image.save(target, format="WEBP", quality=84, method=6)
        count += 1
    return count


def add_static_image_metadata() -> int:
    changed_tags = 0
    for html_path in sorted(ROOT.glob("*.html")):
        source = html_path.read_text(encoding="utf-8")

        def enhance(match: re.Match[str]) -> str:
            nonlocal changed_tags
            tag = match.group(0)
            src_match = SRC_ATTR.search(tag)
            if not src_match:
                return tag
            src = src_match.group(2)
            if not src or src.startswith(("data:", "http://", "https://")):
                return tag
            path = ROOT / src.split("?", 1)[0].split("#", 1)[0]
            if not path.is_file():
                return tag
            with Image.open(path) as image:
                width, height = image.size
            additions = []
            updated_tag = tag
            for attribute, value in (("width", width), ("height", height)):
                pattern = re.compile(rf"\b{attribute}=(['\"])\d+\1", re.IGNORECASE)
                if pattern.search(updated_tag):
                    updated_tag = pattern.sub(f'{attribute}="{value}"', updated_tag)
                else:
                    additions.append(f'{attribute}="{value}"')
            if not re.search(r"\bdecoding=", tag, re.IGNORECASE):
                additions.append('decoding="async"')
            is_brand = "/brand/" in src
            if not is_brand and not re.search(r"\bloading=", tag, re.IGNORECASE):
                additions.append('loading="lazy"')
            if not additions and updated_tag == tag:
                return tag
            changed_tags += 1
            if additions:
                updated_tag = updated_tag[:-1].rstrip() + " " + " ".join(additions) + ">"
            return updated_tag

        updated = IMG_TAG.sub(enhance, source)
        if updated != source:
            html_path.write_text(updated, encoding="utf-8", newline="\n")
    return changed_tags


def main() -> None:
    created, replacements = extract_embedded_images()
    thumbnails = build_card_cover_thumbnails()
    forum_upgrades = upgrade_forum_photos()
    metadata = add_static_image_metadata()
    print(
        f"assets={created}, data_uri_replacements={replacements}, "
        f"card_thumbnails={thumbnails}, forum_high_res={forum_upgrades}, "
        f"enhanced_img_tags={metadata}"
    )


if __name__ == "__main__":
    main()
