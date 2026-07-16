#!/usr/bin/env python3
"""展開済みの提出画像を検査し、公開用フォルダへ取り込む。"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
WORK_ID = re.compile(r"work-(0[1-9]|1[0-9]|2[01])$")
REQUIRED_BASENAMES = {"thumbnail", "main"}
OPTIONAL_BASENAMES = {f"gallery-{number:02d}" for number in range(1, 6)}
ALLOWED_BASENAMES = REQUIRED_BASENAMES | OPTIONAL_BASENAMES
ALLOWED_EXTENSIONS = {".jpg", ".png"}
MAX_BYTES = 10 * 1024 * 1024


def image_directories(incoming: Path) -> list[Path]:
    directories = [path for path in incoming.rglob("work-??") if path.is_dir() and WORK_ID.fullmatch(path.name)]
    duplicate_ids = {path.name for path in directories if sum(item.name == path.name for item in directories) > 1}
    if duplicate_ids:
        raise SystemExit(f"同じ作品IDのフォルダが複数あります: {', '.join(sorted(duplicate_ids))}")
    return sorted(directories)


def validate(directory: Path) -> list[Path]:
    files = [path for path in directory.iterdir() if path.is_file() and path.name != ".DS_Store"]
    unexpected = {
        path.name
        for path in files
        if path.stem not in ALLOWED_BASENAMES or path.suffix not in ALLOWED_EXTENSIONS
    }
    basenames = {path.stem for path in files if path.name not in unexpected}
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
        if sum(path.stem == basename for path in files) > 1
    }
    if duplicates:
        raise ValueError(
            "同じ画像のJPEGとPNGが両方あります: " + ", ".join(sorted(duplicates))
        )

    gallery_numbers = sorted(
        int(basename.removeprefix("gallery-"))
        for basename in basenames
        if basename.startswith("gallery-")
    )
    if gallery_numbers and gallery_numbers != list(range(1, gallery_numbers[-1] + 1)):
        raise ValueError("gallery画像の番号が連続していません。gallery-01 から順に指定してください")

    for path in files:
        if path.stat().st_size > MAX_BYTES:
            raise ValueError(f"10MBを超えています: {path.name}")
        result = subprocess.run(
            ["file", "--brief", "--mime-type", str(path)],
            check=True,
            capture_output=True,
            text=True,
        )
        expected_mime = "image/jpeg" if path.suffix == ".jpg" else "image/png"
        if result.stdout.strip() != expected_mime:
            raise ValueError(f"拡張子と画像形式が一致しません: {path.name}")
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

    validated: list[tuple[Path, list[Path]]] = []
    errors = []
    for directory in directories:
        try:
            validated.append((directory, validate(directory)))
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            errors.append(f"{directory.name}: {error}")
    if errors:
        raise SystemExit("画像を取り込めませんでした:\n" + "\n".join(errors))

    for directory, files in validated:
        if args.check:
            print(f"OK {directory.name}: {len(files)} files")
            continue
        destination = ROOT / "Image" / "works" / directory.name
        destination.mkdir(parents=True, exist_ok=True)
        for old_file in destination.iterdir():
            if (
                old_file.is_file()
                and old_file.stem in ALLOWED_BASENAMES
                and old_file.suffix in ALLOWED_EXTENSIONS
            ):
                old_file.unlink()
        for source in files:
            shutil.copy2(source, destination / source.name)
        print(f"IMPORTED {directory.name}: {len(files)} files")


if __name__ == "__main__":
    main()
