#!/usr/bin/env python3
"""本番公開ルート内の構成とローカル参照を検査する。"""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
EXPECTED_WORK_PAGES = {f"work-{number:02d}.html" for number in range(1, 22)}
FORBIDDEN_NAMES = {"links.txt", ".DS_Store"}
FORBIDDEN_SUFFIXES = {".csv", ".docx", ".md", ".py", ".pyc"}
CSS_URL = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        for name, value in attrs:
            if not value:
                continue
            if name in {"href", "src"}:
                self.references.append(value)
            elif name == "srcset":
                self.references.extend(
                    candidate.strip().split()[0]
                    for candidate in value.split(",")
                    if candidate.strip()
                )


def local_path(reference: str, source: Path) -> Path | None:
    stripped = reference.strip()
    if not stripped or stripped.startswith("#") or stripped.startswith("//"):
        return None
    parsed = urlsplit(stripped)
    if parsed.scheme or parsed.netloc:
        return None
    path_text = unquote(parsed.path)
    if not path_text:
        return None
    if path_text.startswith("/"):
        target = PUBLIC / path_text.lstrip("/")
    else:
        target = source.parent / path_text
    return target.resolve()


def validate_reference(reference: str, source: Path, errors: list[str]) -> None:
    target = local_path(reference, source)
    if target is None:
        return
    try:
        target.relative_to(PUBLIC.resolve())
    except ValueError:
        errors.append(f"{source.relative_to(ROOT)}: public外を参照しています: {reference}")
        return
    if not target.is_file():
        errors.append(f"{source.relative_to(ROOT)}: 参照先がありません: {reference}")


def main() -> None:
    errors: list[str] = []
    if not (PUBLIC / "index.html").is_file():
        errors.append("public/index.html がありません")

    works_dir = PUBLIC / "works"
    actual_work_pages = (
        {path.name for path in works_dir.glob("work-*.html")}
        if works_dir.is_dir()
        else set()
    )
    missing_pages = EXPECTED_WORK_PAGES - actual_work_pages
    unexpected_pages = actual_work_pages - EXPECTED_WORK_PAGES
    if missing_pages:
        errors.append("不足している作品ページ: " + ", ".join(sorted(missing_pages)))
    if unexpected_pages:
        errors.append("想定外の作品ページ: " + ", ".join(sorted(unexpected_pages)))

    public_files = [path for path in PUBLIC.rglob("*") if path.is_file()]
    for path in public_files:
        if path.name in FORBIDDEN_NAMES:
            errors.append(f"本番公開対象に含められないファイルです: {path.relative_to(ROOT)}")
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append(f"本番公開対象に含められないファイルです: {path.relative_to(ROOT)}")
        if path.suffix.lower() == ".txt" and not (
            path.name == "OFL.txt" and "fonts" in path.parts
        ):
            errors.append(f"本番公開対象に含められないテキストです: {path.relative_to(ROOT)}")

    for html_path in PUBLIC.rglob("*.html"):
        text = html_path.read_text(encoding="utf-8")
        parser = ReferenceParser()
        parser.feed(text)
        for reference in parser.references:
            validate_reference(reference, html_path, errors)
        for match in CSS_URL.finditer(text):
            validate_reference(match.group(2), html_path, errors)

    for css_path in PUBLIC.rglob("*.css"):
        text = css_path.read_text(encoding="utf-8")
        for match in CSS_URL.finditer(text):
            validate_reference(match.group(2), css_path, errors)

    if errors:
        raise SystemExit("本番公開ファイルの検査に失敗しました:\n" + "\n".join(errors))

    print(
        f"OK public/: {len(public_files)} files, "
        f"{len(actual_work_pages)} work pages"
    )


if __name__ == "__main__":
    main()
