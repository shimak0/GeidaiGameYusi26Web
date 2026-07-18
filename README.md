# GeidaiGameYusi26Web

東京藝術大学大学院映像研究科ゲーム・インタラクティブアート専攻 一期生有志展「RESPAWN」の静的サイトです。

フロントエンドはバニラHTML・CSS・JavaScriptで構成されています。

## ディレクトリ

```text
public/       本番公開ルート。この中身をそのまま公開する
source/       CSV、作品リンク、参照資料などの生成元
scripts/      画像取り込み、ページ生成、公開検査、ZIP作成
submissions/  作家へ配布する提出用ファイル
incoming/     Driveから展開した提出データ（Git管理外）
dist/         本番用ZIP（Git管理外）
```

本番環境へ必要なファイルを追加する場合は、必ず `public/` 内へ配置してください。`public/` 外のファイルは本番用ZIPやGitHub Pagesには公開されません。

## 通常の更新

```sh
python3 scripts/import_images.py --check
python3 scripts/import_images.py
python3 scripts/validate_public.py
```

`import_images.py` は提出画像とリンクを取り込み、作品ページを再生成します。

## 本番用ZIP

```sh
zsh scripts/create_production_zip.sh
```

出力先：

```text
dist/GeidaiGameYusi26Web-production.zip
```

詳しくは `IMAGE_SUBMISSION.md` と `PRODUCTION_DEPLOY.md` を参照してください。
