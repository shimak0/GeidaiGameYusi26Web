#!/usr/bin/env python3
"""展開済みの提出画像を検査し、公開用フォルダへ取り込む。"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from work_links import LINK_KEYS, MAX_LINKS_BYTES, parse_links, parse_links_text


ROOT = Path(__file__).resolve().parent.parent
WORK_FOLDER_NAMES = {
    "work-01": "work-01-cest-bones",
    "work-02": "work-02-make-this-shape",
    "work-03": "work-03-boundary",
    "work-04": "work-04-player",
    "work-05": "work-05-transparent",
    "work-06": "work-06-shiftwelt",
    "work-07": "work-07-shred-shrine",
    "work-08": "work-08-tutti",
    "work-09": "work-09-lighthouse-climbing",
    "work-10": "work-10-kiss-find",
    "work-11": "work-11-restoration-library",
    "work-12": "work-12-animemories-the-library-of-memories",
    "work-13": "work-13-play-room",
    "work-14": "work-14-newme",
    "work-15": "work-15-kurukuru-guruguru",
    "work-16": "work-16-another-world",
    "work-17": "work-17-where-the-voice-goes",
    "work-18": "work-18-astrrow",
    "work-19": "work-19-colors",
    "work-20": "work-20-arcabbit",
    "work-21": "work-21-exam-pachinko",
}
FOLDER_TO_WORK_ID = {folder_name: work_id for work_id, folder_name in WORK_FOLDER_NAMES.items()}
REQUIRED_BASENAMES = {"main"}
OPTIONAL_BASENAMES = {"thumbnail"} | {f"gallery-{number:02d}" for number in range(1, 6)}
ALLOWED_BASENAMES = REQUIRED_BASENAMES | OPTIONAL_BASENAMES
ALLOWED_EXTENSIONS = {".jpg", ".png"}
LINKS_FILENAME = "links.txt"
LINKS_DOCX_FILENAMES = {"links.docx", "links.txt.docx"}
LINKS_FILENAMES = {LINKS_FILENAME} | LINKS_DOCX_FILENAMES
MAX_BYTES = 10 * 1024 * 1024
MAX_DOCX_BYTES = 1024 * 1024
MAX_DOCX_XML_BYTES = 256 * 1024
WORD_NAMESPACE = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def work_id_from_folder_name(folder_name: str) -> str | None:
    if folder_name in WORK_FOLDER_NAMES:
        return folder_name
    return FOLDER_TO_WORK_ID.get(folder_name)


def image_directories(incoming: Path) -> list[tuple[str, Path]]:
    candidates = [path for path in incoming.rglob("work-*") if path.is_dir()]
    invalid_names = sorted(
        path.name for path in candidates if work_id_from_folder_name(path.name) is None
    )
    if invalid_names:
        raise SystemExit(f"認識できない作品フォルダ名があります: {', '.join(invalid_names)}")

    directories = [
        (work_id_from_folder_name(path.name), path)
        for path in candidates
        if work_id_from_folder_name(path.name) is not None
    ]
    duplicate_ids = {
        work_id
        for work_id, _ in directories
        if sum(item_id == work_id for item_id, _ in directories) > 1
    }
    if duplicate_ids:
        raise SystemExit(f"同じ作品IDのフォルダが複数あります: {', '.join(sorted(duplicate_ids))}")
    return sorted(directories)


def parse_links_docx(path: Path) -> dict[str, str]:
    if path.stat().st_size > MAX_DOCX_BYTES:
        raise ValueError("linksのDOCXファイルが1MBを超えています")
    try:
        with zipfile.ZipFile(path) as archive:
            document_info = archive.getinfo("word/document.xml")
            if document_info.file_size > MAX_DOCX_XML_BYTES:
                raise ValueError("linksのDOCX文書データが256KBを超えています")
            document_xml = archive.read("word/document.xml")
        document = ElementTree.fromstring(document_xml)
    except (KeyError, ElementTree.ParseError, zipfile.BadZipFile) as error:
        raise ValueError("linksのDOCXファイルを読み取れません") from error

    namespace = f"{{{WORD_NAMESPACE}}}"
    lines = []
    for paragraph in document.iter(f"{namespace}p"):
        parts = []
        for node in paragraph.iter():
            if node.tag == f"{namespace}t" and node.text:
                parts.append(node.text)
            elif node.tag == f"{namespace}tab":
                parts.append("\t")
            elif node.tag in {f"{namespace}br", f"{namespace}cr"}:
                parts.append("\n")
        lines.append("".join(parts))
    text = "\n".join(lines)
    if len(text.encode("utf-8")) > MAX_LINKS_BYTES:
        raise ValueError("linksのDOCX内容が16KBを超えています")
    return parse_links_text(text)


def parse_submission_links(path: Path) -> dict[str, str]:
    if path.name.lower() in LINKS_DOCX_FILENAMES:
        return parse_links_docx(path)
    return parse_links(path)


def formatted_links(links: dict[str, str]) -> str:
    lines = [f"{key}: {links[key]}" if links.get(key) else f"{key}:" for key in LINK_KEYS]
    return "\n".join(lines) + "\n"


def validate(directory: Path) -> list[Path]:
    files = [
        path
        for path in directory.iterdir()
        if path.is_file() and path.name.lower() != ".ds_store"
    ]
    links_files = [path for path in files if path.name.lower() in LINKS_FILENAMES]
    if len(links_files) > 1:
        raise ValueError("links.txt または links.txt.docx が複数あります")

    image_files = [path for path in files if path.name.lower() not in LINKS_FILENAMES]
    unexpected = {
        path.name
        for path in image_files
        if path.stem.lower() not in ALLOWED_BASENAMES
        or path.suffix.lower() not in ALLOWED_EXTENSIONS
    }
    basenames = {
        path.stem.lower() for path in image_files if path.name not in unexpected
    }
    missing = REQUIRED_BASENAMES - basenames
    if missing:
        required_names = ", ".join(
            f"{name}.jpg または {name}.png" for name in sorted(missing)
        )
        raise ValueError(f"必須画像がありません: {required_names}")
    if unexpected:
        raise ValueError(f"使用できないファイル名です: {', '.join(sorted(unexpected))}")

    duplicates = {
        basename
        for basename in basenames
        if sum(path.stem.lower() == basename for path in image_files) > 1
    }
    if duplicates:
        raise ValueError("同じ画像名が複数あります: " + ", ".join(sorted(duplicates)))

    gallery_numbers = sorted(
        int(basename.removeprefix("gallery-"))
        for basename in basenames
        if basename.startswith("gallery-")
    )
    if gallery_numbers and gallery_numbers != list(range(1, gallery_numbers[-1] + 1)):
        raise ValueError("gallery画像の番号が連続していません。gallery-01 から順に指定してください")

    for path in image_files:
        if path.stat().st_size > MAX_BYTES:
            raise ValueError(f"10MBを超えています: {path.name}")
        result = subprocess.run(
            ["file", "--brief", "--mime-type", str(path)],
            check=True,
            capture_output=True,
            text=True,
        )
        expected_mime = "image/jpeg" if path.suffix.lower() == ".jpg" else "image/png"
        if result.stdout.strip() != expected_mime:
            raise ValueError(f"拡張子と画像形式が一致しません: {path.name}")
    if links_files:
        parse_submission_links(links_files[0])
    return sorted(files)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("incoming", nargs="?", type=Path, default=ROOT / "incoming")
    parser.add_argument("--check", action="store_true", help="検査のみ行い、コピーしない")
    args = parser.parse_args()
    incoming = args.incoming.resolve()
    if not incoming.is_dir():
        raise SystemExit(f"展開先フォルダが見つかりません: {incoming}")

    directories = image_directories(incoming)
    if not directories:
        raise SystemExit("work-01 〜 work-21 の作品フォルダが見つかりません。")

    validated: list[tuple[str, Path, list[Path]]] = []
    errors = []
    for work_id, directory in directories:
        try:
            validated.append((work_id, directory, validate(directory)))
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            errors.append(f"{directory.name}: {error}")
    if errors:
        raise SystemExit("画像を取り込めませんでした:\n" + "\n".join(errors))

    for work_id, directory, files in validated:
        if args.check:
            print(f"OK {directory.name} -> {work_id}: {len(files)} files")
            continue
        destination = ROOT / "Image" / "works" / work_id
        destination.mkdir(parents=True, exist_ok=True)
        for old_file in destination.iterdir():
            if (
                old_file.is_file()
                and (
                    old_file.name.lower() in LINKS_FILENAMES
                    or (
                        old_file.stem.lower() in ALLOWED_BASENAMES
                        and old_file.suffix.lower() in ALLOWED_EXTENSIONS
                    )
                )
            ):
                old_file.unlink()
        for source in files:
            if source.name.lower() in LINKS_DOCX_FILENAMES:
                links = parse_links_docx(source)
                (destination / LINKS_FILENAME).write_text(
                    formatted_links(links), encoding="utf-8"
                )
            else:
                shutil.copy2(source, destination / source.name.lower())
        print(f"IMPORTED {directory.name} -> {work_id}: {len(files)} files")

    if args.check:
        return

    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_works.py")],
        check=True,
    )
    print("作品ページを再生成しました")


if __name__ == "__main__":
    main()
