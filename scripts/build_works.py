#!/usr/bin/env python3
"""CSVから作品一覧と静的な作品詳細ページを生成する。"""

from __future__ import annotations

import argparse
import csv
import html
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = ROOT / "docs" / "有志展キャプション情報 - シート1.csv"
WORKS_START = "      <!-- WORKS:START -->"
WORKS_END = "      <!-- WORKS:END -->"
PUBLIC_ORDER = [
    "セ・ボ〜ンズ",
    "この形を作レ",
    "Boundary",
    "Player",
    "透き通る",
    "しふとべると！",
    "祭細壇断",
    "Tutti",
    "灯台登り",
    "KISS・FIND",
    "復元文庫",
    "Animemory -記憶の図書館-",
    "Play Room",
    "NewMe",
    "くるくる、ぐるぐる",
    "別の世界",
    "声のゆくえ",
    "Astrrow",
    "COLORS",
    "アルカビット",
    "受験番号パチンコ",
]
PUBLIC_AUTHOR_OVERRIDES = {
    "Tutti": "鈴木 ひなの",
    "灯台登り": "陳禹霖（チンウリン）",
    "Play Room": "鈴木 ひなの・中山 大成・松浦 恵夢・村山 海",
}


def normalized(value: str | None) -> str:
    cleaned = (value or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    return unicodedata.normalize("NFC", cleaned)


def find_csv() -> Path:
    if DEFAULT_CSV.exists():
        return DEFAULT_CSV
    candidates = sorted((ROOT / "docs").glob("*.csv"))
    if len(candidates) == 1:
        return candidates[0]
    raise SystemExit("CSVを特定できません。--csv でファイルを指定してください。")


def load_works(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {
            "名前（日本語表記）",
            "Name（英語表記）",
            "作品タイトル（日本語）",
            "作品タイトル（英語）",
            "体験時間",
            "コンセプト・遊び方など",
        }
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"CSVに必要な列がありません: {', '.join(sorted(missing))}")

        works = []
        for row in reader:
            work = {key: normalized(value) for key, value in row.items() if key}
            if not work["作品タイトル（日本語）"]:
                raise SystemExit("作品タイトルが空の行があります。")
            works.append(work)

    by_title = {work["作品タイトル（日本語）"]: work for work in works}
    duplicate_titles = {
        title for title in by_title if sum(work["作品タイトル（日本語）"] == title for work in works) > 1
    }
    missing = set(PUBLIC_ORDER).difference(by_title)
    unexpected = set(by_title).difference(PUBLIC_ORDER)
    if duplicate_titles or missing or unexpected:
        messages = []
        if duplicate_titles:
            messages.append(f"重複タイトル: {', '.join(sorted(duplicate_titles))}")
        if missing:
            messages.append(f"公開順にあるがCSVにない作品: {', '.join(sorted(missing))}")
        if unexpected:
            messages.append(f"CSVにあるが公開順にない作品: {', '.join(sorted(unexpected))}")
        raise SystemExit("\n".join(messages))

    works = [by_title[title] for title in PUBLIC_ORDER]
    for number, work in enumerate(works, start=1):
        work["id"] = f"work-{number:02d}"
        title = work["作品タイトル（日本語）"]
        if title in PUBLIC_AUTHOR_OVERRIDES:
            work["名前（日本語表記）"] = PUBLIC_AUTHOR_OVERRIDES[title]
    return works


def escape_lines(value: str) -> str:
    return html.escape(value).replace("\n", "<br>\n        ")


def public_description(value: str) -> str:
    """CSVに残った矢印付きの校正会話を公開本文から除外する。"""
    return re.split(r"\s*[（(]?←", value, maxsplit=1)[0].rstrip()


def card_html(work: dict[str, str]) -> str:
    title = html.escape(work["作品タイトル（日本語）"])
    author = escape_lines(work["名前（日本語表記）"])
    work_id = work["id"]
    return f'''        <a class="work-card" href="works/{work_id}.html">
          <div class="work-thumb">
            <img src="Image/works/{work_id}/thumbnail.jpg" data-fallback-srcs="Image/works/{work_id}/thumbnail.png,Image/works/{work_id}/main.jpg,Image/works/{work_id}/main.png" alt="{title}" loading="lazy" data-optional-image>
          </div>
          <h3 class="work-title">{title}</h3>
          <p class="work-author">{author}</p>
        </a>'''


def detail_html(work: dict[str, str]) -> str:
    title_ja = html.escape(work["作品タイトル（日本語）"])
    title_en_raw = work["作品タイトル（英語）"]
    title_en = html.escape(title_en_raw)
    author_ja = escape_lines(work["名前（日本語表記）"])
    author_en = html.escape(work["Name（英語表記）"])
    duration = html.escape(work["体験時間"])
    description_raw = public_description(work["コンセプト・遊び方など"])
    description = escape_lines(description_raw)
    work_id = work["id"]
    title_en_markup = (
        f'\n        <span class="work-title-en" lang="en">{title_en}</span>'
        if title_en_raw and title_en_raw.casefold() != work["作品タイトル（日本語）"].casefold()
        else ""
    )
    author_en_markup = (
        f' <span class="work-author-en" lang="en">/ {author_en}</span>' if author_en else ""
    )
    carousel_images = "\n".join(
        f'''            <img class="carousel-image" src="../Image/works/{work_id}/gallery-{number:02d}.jpg" data-fallback-src="../Image/works/{work_id}/gallery-{number:02d}.png" alt="{title_ja} 作品画像 {number}" loading="lazy" hidden>'''
        for number in range(1, 6)
    )
    carousel_dots = "\n".join(
        f'        <button class="carousel-dot" type="button" aria-label="作品画像 {number} を表示" data-carousel-dot="{number - 1}"></button>'
        for number in range(1, 6)
    )

    return f'''<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{html.escape(description_raw[:120])}">
  <title>{title_ja} | RESPAWN</title>
  <link rel="stylesheet" href="https://use.typekit.net/qsa7gru.css">
  <link rel="stylesheet" href="../assets/work-detail.css">
</head>
<body>
  <nav class="site-nav" aria-label="サイト内ナビゲーション">
    <button class="nav-toggle" type="button" aria-controls="site-menu" aria-expanded="false" aria-label="メニューを開く">
      <span></span><span></span><span></span>
    </button>
    <ul id="site-menu">
      <li><a href="../index.html#greeting">ご挨拶</a></li>
      <li><a href="../index.html#works">展示作品</a></li>
      <li><a href="../index.html#info">開催概要</a></li>
    </ul>
  </nav>

  <main>
    <section class="hero-image" aria-label="{title_ja} メイン画像">
      <span class="image-placeholder">作品画像準備中</span>
      <img src="../Image/works/{work_id}/main.jpg" data-fallback-src="../Image/works/{work_id}/main.png" alt="{title_ja}" data-optional-image>
    </section>

    <section class="work-info" aria-labelledby="work-title">
      <h1 class="work-title" id="work-title">{title_ja}{title_en_markup}</h1>
      <p class="work-author">{author_ja}{author_en_markup}</p>
      <p class="work-duration">体験時間：{duration}</p>
      <p class="work-description">{description}</p>
    </section>

    <section class="carousel" aria-label="作品画像スライダー" data-carousel>
      <div class="carousel-track">
        <button class="carousel-side prev" type="button" aria-label="前の作品画像" data-carousel-prev></button>
        <div class="carousel-frame">
          <span class="carousel-placeholder">作品画像<br>（3 から 5 枚程度，無くても可）</span>
          <div class="carousel-images">
{carousel_images}
          </div>
        </div>
        <button class="carousel-side next" type="button" aria-label="次の作品画像" data-carousel-next></button>
      </div>
      <div class="carousel-dots">
{carousel_dots}
      </div>
    </section>

    <section class="video-box" aria-label="作品映像">
      映像<br>（YoutubeURL 等，無くても可）
    </section>

    <ul class="sns-links" aria-label="SNSリンク">
      <li><span class="sns-link" aria-disabled="true"><span class="sns-label">SNS 1</span></span></li>
      <li><span class="sns-link" aria-disabled="true"><span class="sns-label">SNS 2</span></span></li>
      <li><span class="sns-link" aria-disabled="true"><span class="sns-label">SNS 3</span></span></li>
    </ul>

    <div class="back-wrap">
      <a class="back-button" href="../index.html#works">BACK</a>
    </div>
  </main>
  <footer class="under-image" aria-label="下部画像">
    <img src="../Image/UnderImage.jpg" alt="">
  </footer>
  <script src="../assets/site.js"></script>
</body>
</html>
'''


def bootstrap_assets() -> None:
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    css_path = assets / "work-detail.css"
    if not css_path.exists():
        source = (ROOT / "work-detail.html").read_text(encoding="utf-8")
        match = re.search(r"<style>\s*(.*?)\s*</style>", source, flags=re.DOTALL)
        if not match:
            raise SystemExit("work-detail.html からCSSを抽出できません。")
        css = match.group(1).replace('url("Zen_Kaku_Gothic_New/', 'url("../Zen_Kaku_Gothic_New/')
        css_path.write_text(css + "\n", encoding="utf-8")


def update_index(works: list[dict[str, str]]) -> None:
    index_path = ROOT / "index.html"
    source = index_path.read_text(encoding="utf-8")
    cards = "\n".join(card_html(work) for work in works)
    block = f'''{WORKS_START}
      <div class="works-grid">
{cards}
      </div>
{WORKS_END}'''

    if WORKS_START in source and WORKS_END in source:
        pattern = re.escape(WORKS_START) + r".*?" + re.escape(WORKS_END)
    else:
        pattern = r'      <p class="coming-soon">.*?</p>\s*<div class="works-grid is-hidden" aria-hidden="true">.*?      </div>'
    updated, count = re.subn(pattern, block, source, count=1, flags=re.DOTALL)
    if count != 1:
        raise SystemExit("index.html の作品一覧更新位置を特定できません。")
    index_path.write_text(updated, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, help="作品情報CSV")
    args = parser.parse_args()
    csv_path = (args.csv or find_csv()).resolve()
    works = load_works(csv_path)
    bootstrap_assets()
    update_index(works)

    works_dir = ROOT / "works"
    works_dir.mkdir(exist_ok=True)
    for work in works:
        (works_dir / f"{work['id']}.html").write_text(detail_html(work), encoding="utf-8")
    print(f"{len(works)}作品を生成しました: {csv_path}")


if __name__ == "__main__":
    main()
