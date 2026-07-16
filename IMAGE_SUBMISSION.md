# 作品画像の提出・取り込み手順

Google Drive では、下記の「作品ID」と同じ名前のフォルダを作品ごとに作成してください。
Drive から ZIP ダウンロードした後、ZIP をこのリポジトリの `incoming/` に展開します。

## 提出ファイル

各作品フォルダには、以下の名前で画像を入れてください。

```text
work-01/
  thumbnail.jpg   必須：一覧用画像
  main.png        必須：作品ページのメイン画像
  gallery-01.jpg  任意：作品ページの追加画像
  gallery-02.png  任意
```

- ファイル形式：JPEGまたはPNG
- 拡張子：小文字の `.jpg` または `.png`
- 同じ画像名についてJPEGとPNGの両方を入れない
- 写真は容量を抑えやすいJPEG、透過が必要な画像はPNGを推奨
- カラーモード：RGB
- 推奨比率：16:9
- 推奨サイズ：
  - `thumbnail`：1280 × 720 px
  - `main`、`gallery-XX`：1920 × 1080 px
- 上限：1ファイル10MB
- 追加画像は `gallery-01` から番号を飛ばさずに命名
- ZIP内にGoogle Driveが作る親フォルダが含まれていても取り込み可能

ファイル名が異なる画像、JPEG・PNG以外の画像、必須画像が不足した作品は取り込まれません。

## 作品ID対応表

| 作品ID | 作品名 | 作家名 |
| --- | --- | --- |
| work-01 | セ・ボ〜ンズ | 福眞 奏太 |
| work-02 | この形を作レ | 横山 立門 |
| work-03 | Boundary | 天野 兼太 |
| work-04 | Player | 中山 大成 |
| work-05 | 透き通る | 藤森 玲央 |
| work-06 | しふとべると！ | 大塚 敏郎 |
| work-07 | 祭細壇断 | ニルギリ |
| work-08 | Tutti | 鈴木 ひなの |
| work-09 | 灯台登り | 陳禹霖（チンウリン） |
| work-10 | KISS・FIND | ダイ ミンミン |
| work-11 | 復元文庫 | 佐々木 隼 |
| work-12 | Animemory -記憶の図書館- | 大髙 那由子 |
| work-13 | Play Room | 鈴木 ひなの・中山 大成・松浦 恵夢・村山 海 |
| work-14 | NewMe | 大久保 麻央 |
| work-15 | くるくる、ぐるぐる | 平山 理貴 |
| work-16 | 別の世界 | 平山 理貴 |
| work-17 | 声のゆくえ | 藤井 嗣音 |
| work-18 | Astrrow | 横山 立門 |
| work-19 | COLORS | 横山 立門 |
| work-20 | アルカビット | 嶋 晃平 |
| work-21 | 受験番号パチンコ | 大塚 敏郎 |

## ZIP展開後の取り込み

例：

```text
incoming/
  有志展作品画像/
    work-01/
      thumbnail.jpg
      main.jpg
      gallery-01.jpg
    work-02/
      thumbnail.jpg
      main.jpg
```

最初に検査だけを実行します。

```sh
python3 scripts/import_images.py --check
```

すべて `OK` になったら公開用フォルダへコピーします。

```sh
python3 scripts/import_images.py
```

画像は `Image/works/work-XX/` にコピーされます。同じ作品IDを再度取り込むと、その作品の既存画像を新しい提出内容で置き換えます。

その後、ローカル表示を確認してからコミット・pushします。GitHub Pagesへの反映には数分かかることがあります。

## CSVからページを再生成する

作品名やキャプションをCSVで修正した場合は、次のコマンドで `index.html` と全作品ページを再生成します。

```sh
python3 scripts/build_works.py
```

作品IDは `scripts/build_works.py` の公開順で固定されています。CSVの行順を変更しても作品IDは変わりません。
