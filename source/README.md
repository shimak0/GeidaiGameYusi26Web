# source

本番環境へ直接公開しない、ページ生成用のデータと参照資料を置きます。

```text
data/        作品名、作家名、キャプションを含むCSV
work-links/  作品ごとのYouTube・SNS・関連リンク
placeholders/未提出作品用の仮画像
reference/   旧レイアウトや地図などの参照資料
```

`reference/work-detail-original.html` は修正前レイアウトの参照用であり、現在の作品ページ生成には使用されません。作品ページのHTMLは `scripts/build_works.py` が生成します。
