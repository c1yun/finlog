"""Static quality checks for the FinLog GitHub Pages site."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

from lxml import html


ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = sorted(ROOT.glob("*.html"))
URL_PATTERN = re.compile(r"url\((['\"]?)(.*?)\1\)", re.IGNORECASE)


def local_target(value: str) -> tuple[Path, str] | None:
    value = value.strip()
    if not value or value.startswith(("#", "data:", "mailto:", "tel:", "http://", "https://", "javascript:")):
        return None
    path_text, _, fragment = value.partition("#")
    path_text = unquote(path_text.split("?", 1)[0])
    return ROOT / path_text, fragment


def main() -> int:
    errors: list[str] = []
    image_count = 0
    local_references = 0
    parsed: dict[Path, html.HtmlElement] = {}

    for html_path in HTML_FILES:
        source = html_path.read_text(encoding="utf-8")
        if "data:image" in source:
            errors.append(f"{html_path.name}: embedded data image remains")
        try:
            document = html.fromstring(source)
        except Exception as exc:
            errors.append(f"{html_path.name}: HTML parse failure: {exc}")
            continue
        parsed[html_path] = document
        ids = [value for value in document.xpath("//*[@id]/@id") if value]
        duplicates = sorted({value for value in ids if ids.count(value) > 1})
        if duplicates:
            errors.append(f"{html_path.name}: duplicate ids {', '.join(duplicates)}")

        if not document.xpath("//script[@src='assets/site-upgrade.js']"):
            errors.append(f"{html_path.name}: shared image/accessibility runtime missing")

        for image in document.xpath("//img"):
            image_count += 1
            src = image.get("src")
            if src and not image.get("alt") and image.get("alt") != "":
                errors.append(f"{html_path.name}: image without alt: {src[:80]}")
            target = local_target(src or "")
            if target:
                local_references += 1
                path, _ = target
                if not path.is_file():
                    errors.append(f"{html_path.name}: missing image {src}")
                elif "/brand/" not in src.replace("\\", "/"):
                    for attribute in ("width", "height", "decoding"):
                        if image.get(attribute) is None:
                            errors.append(f"{html_path.name}: {src} missing {attribute}")

        references = []
        references.extend(document.xpath("//a[@href]/@href"))
        references.extend(document.xpath("//script[@src]/@src"))
        references.extend(document.xpath("//link[@href]/@href"))
        for style in document.xpath("//@style") + document.xpath("//style/text()"):
            references.extend(match.group(2) for match in URL_PATTERN.finditer(style))

        for reference in references:
            target = local_target(reference)
            if not target:
                continue
            local_references += 1
            path, fragment = target
            if not path.is_file():
                errors.append(f"{html_path.name}: missing local reference {reference}")
                continue
            if fragment and path.suffix.lower() in (".html", ".htm"):
                target_doc = parsed.get(path)
                if target_doc is None:
                    try:
                        target_doc = html.fromstring(path.read_text(encoding="utf-8"))
                    except Exception:
                        continue
                if not target_doc.xpath("//*[@id=$target]", target=fragment):
                    errors.append(f"{html_path.name}: missing anchor {reference}")

    if errors:
        print("FinLog static validation failed:")
        for error in sorted(set(errors)):
            print(f"- {error}")
        return 1

    print(
        f"FinLog static validation passed: pages={len(HTML_FILES)}, "
        f"images={image_count}, local_references={local_references}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
