# 作品画像の提出・取り込み手順

Google Drive では、下記の「作品ID＋英語作品名」のフォルダを作品ごとに使用してください。
Drive から ZIP ダウンロードした後、ZIP をこのリポジトリの `incoming/` に展開します。

## 提出ファイル

各作品フォルダには、以下の名前で画像を入れてください。

```text
work-01-cest-bones/
  main.png        必須：作品ページのメイン画像
  thumbnail.jpg   任意：一覧用画像
  gallery-01.jpg  任意：作品ページの追加画像
  gallery-02.png  任意
  ...
  gallery-10.jpg  任意：追加画像は最大10枚
  links.txt       任意：YouTube・SNS・関連サイト
```

- ファイル形式：JPEGまたはPNG
- ファイル名と拡張子の大文字・小文字は区別せず、取り込み時に小文字へ統一される
- 同じ画像名についてJPEGとPNGの両方を入れない
- 写真は容量を抑えやすいJPEG、透過が必要な画像はPNGを推奨
- カラーモード：RGB
- 推奨比率：16:9
- 推奨サイズ：
  - `thumbnail`：1280 × 720 px
  - `main`、`gallery-XX`：1920 × 1080 px
- `thumbnail` がない場合は `main` が一覧画像として使用される
- 上限：1ファイル10MB
- 追加画像は最大10枚。`gallery-01` から `gallery-10` まで番号を飛ばさずに命名
- ZIP内にGoogle Driveが作る親フォルダが含まれていても取り込み可能

ファイル名が異なる画像、JPEG・PNG以外の画像、`main` が不足した作品は取り込まれません。

作品画像が未提出の場合は、運営側で用意した `coming soon...` 画像を `main.jpg` として使用します。
後日、作家から提出された画像で同名の `main.jpg` または `main.png` を置き換えてください。
`thumbnail` が未提出の場合、一覧ページには同じ `main` 画像が自動的に表示されます。

## YouTube・SNS・関連リンク

掲載を希望する場合は、作品フォルダの `links.txt` にURLを記入してください。
空欄の項目は作品ページに表示されません。

```text
youtube: https://www.youtube.com/watch?v=xxxxxxxxxxx
youtube_channel: https://www.youtube.com/@example
x: https://x.com/example
instagram: https://www.instagram.com/example/
steam: https://store.steampowered.com/app/000000/example/
website: https://example.com/
```

- ファイル名は `links.txt`（大文字・小文字は区別せず、取り込み時に小文字へ統一）
- Googleドキュメント経由で保存された `links.docx`、`links.txt.docx` も受付可能で、取り込み時に `links.txt` へ変換される
- 文字コードはUTF-8
- URLは `https://` から記入
- キー名は変更しない
- YouTubeは動画ページ、短縮URL、Shorts、LiveのURLに対応
- `youtube` は動画埋め込み、`youtube_channel` はYouTubeアイコン付きのチャンネルリンクとして表示
- チャンネルURLが `youtube` に記入されていても、自動的にチャンネルリンクとして取り込まれる
- X、Instagram、Steamは各サービスの正規ドメインのみ受付
- `website` は任意のHTTPSサイトを指定可能
- 不正URL、未知のキー、キー重複がある場合は取り込みを停止

空の雛形は `templates/links.txt` にあります。

## 作品ID対応表

| 作品ID | Driveフォルダ名 | 作品名 | 作家名 |
| --- | --- | --- | --- |
| work-01 | `work-01-cest-bones` | セ・ボ〜ンズ | 福眞 奏太 |
| work-02 | `work-02-make-this-shape` | この形を作レ | 横山 立門 |
| work-03 | `work-03-boundary` | Boundary | 天野 兼太 |
| work-04 | `work-04-player` | Player | 中山 大成 |
| work-05 | `work-05-transparent` | 透き通る | 藤森 玲央 |
| work-06 | `work-06-shiftwelt` | しふとべると！ | 大塚 敏郎 |
| work-07 | `work-07-shred-shrine` | 祭細壇断 | ニルギリ |
| work-08 | `work-08-tutti` | Tutti | 鈴木 ひなの |
| work-09 | `work-09-lighthouse-climbing` | 灯台登り | 陳禹霖（チンウリン） |
| work-10 | `work-10-kiss-find` | KISS・FIND | ダイ ミンミン |
| work-11 | `work-11-restoration-library` | 復元文庫 | 佐々木 隼 |
| work-12 | `work-12-animemories-the-library-of-memories` | Animemory -記憶の図書館- | 大髙 那由子 |
| work-13 | `work-13-play-room` | Play Room | 鈴木 ひなの・中山 大成・松浦 恵夢・村山 海 |
| work-14 | `work-14-newme` | NewMe | 大久保 麻央 |
| work-15 | `work-15-kurukuru-guruguru` | くるくる、ぐるぐる | 平山 理貴 |
| work-16 | `work-16-another-world` | 別の世界 | 平山 理貴 |
| work-17 | `work-17-where-the-voice-goes` | 声のゆくえ | 藤井 嗣音 |
| work-18 | `work-18-astrrow` | Astrrow | 横山 立門 |
| work-19 | `work-19-colors` | COLORS | 横山 立門 |
| work-20 | `work-20-arcabbit` | アルカビット | 嶋 晃平 |
| work-21 | `work-21-exam-pachinko` | 受験番号パチンコ | 大塚 敏郎 |

## ZIP展開後の取り込み

例：

```text
incoming/
  有志展作品画像/
    work-01-cest-bones/
      thumbnail.jpg
      main.jpg
      gallery-01.jpg
      links.txt
    work-02-make-this-shape/
      thumbnail.jpg
      main.jpg
      links.txt
```

最初に検査だけを実行します。

```sh
python3 scripts/import_images.py --check
```

すべて `OK` になったら公開用フォルダへコピーします。

```sh
python3 scripts/import_images.py
```

旧形式の `work-01`〜`work-21` フォルダも取り込み可能です。新旧両方の同じ作品IDがある場合は、重複として取り込みを停止します。

画像と `links.txt` はprefixを使って `Image/works/work-XX/` にコピーされます。同じ作品IDを再度取り込むと、その作品の既存内容を新しい提出内容で置き換えます。
取り込み完了後、作品ページは自動的に再生成されます。

再生成時、メイン画像・一覧画像・ギャラリー画像のURLには、画像内容から算出したクエリパラメータ（例：`main.jpg?v=abc123...`）が自動的に付きます。
画像を同名のまま更新してもクエリ値が変わるため、GitHub Pagesやブラウザに残った古い画像キャッシュを回避できます。ファイル名を変更する必要はありません。

その後、ローカル表示を確認してからコミット・pushします。GitHub Pagesへの反映には数分かかることがあります。

## CSVからページを再生成する

作品名やキャプションをCSVで修正した場合は、次のコマンドで `index.html` と全作品ページを再生成します。

```sh
python3 scripts/build_works.py
```

作品IDは `scripts/build_works.py` の公開順で固定されています。CSVの行順を変更しても作品IDは変わりません。
