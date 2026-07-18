# 本番環境向けZIP作成・アップロード手順

本番公開に必要なファイルは、すべて `public/` にまとまっています。

ZIP作成スクリプトは `public/` 内のファイルを検査したうえで、その中身をすべてZIPにします。画像、フォント、CSSなどを追加した際に、ZIP作成スクリプトへファイル名を追記する必要はありません。

## フォルダの役割

```text
public/       本番環境へアップロードするファイル
source/       CSV、リンク情報、参照資料などの生成元
scripts/      画像取り込み、ページ生成、検査、ZIP作成
submissions/  作家へ渡す雛形と手順書
incoming/     Driveから展開した提出データ（Git管理外）
dist/         作成された本番用ZIP（Git管理外）
```

`public/` の直下に `index.html` があり、`public/` 自体ではなく、その中身が本番環境の公開ディレクトリに配置される構成です。

## 事前確認

作品画像の取り込みとページ再生成が完了していることを確認します。

```sh
python3 scripts/import_images.py --check
python3 scripts/build_works.py
```

本番公開ファイルだけを検査する場合は、次を実行します。

```sh
python3 scripts/validate_public.py
```

検査内容：

- `public/index.html` が存在する
- 全21作品ページが存在する
- HTML・CSSから参照されるローカルファイルが存在する
- フォントや画像の参照先が `public/` 内にある
- `links.txt`、CSV、Python、Markdownなどが `public/` に混入していない

## ZIPの作成

VS Codeで「ターミナル」→「新しいターミナル」を選択し、次を実行します。

```sh
zsh scripts/create_production_zip.sh
```

検査に成功すると、次のファイルが作成されます。

```text
dist/GeidaiGameYusi26Web-production.zip
```

同名のZIPがある場合は置き換えられます。

## ZIP内容の確認

```sh
unzip -l dist/GeidaiGameYusi26Web-production.zip
```

ZIP直下に次の構成があることを確認します。

```text
index.html
works/
assets/
  css/
  js/
  images/
  fonts/
```

必要に応じて一時フォルダへ展開します。

```sh
CHECK_DIR="$(mktemp -d)"
unzip -q dist/GeidaiGameYusi26Web-production.zip -d "$CHECK_DIR"
find "$CHECK_DIR" -maxdepth 3 -type f | sort
```

確認後は一時フォルダを削除できます。

```sh
rm -rf "$CHECK_DIR"
```

## 本番環境へのアップロード依頼

担当者へは、次の内容を伝えてください。

1. `GeidaiGameYusi26Web-production.zip` を展開する
2. 展開後の `index.html` が公開ディレクトリ直下に来るよう配置する
3. 既存の静的ファイルをZIPの内容一式で置き換える
4. 削除済みの旧画像や旧HTMLが残らないようにする

差分ファイルだけを追加すると古いファイルが残る可能性があるため、原則としてZIPの内容一式で入れ替えてください。

## 反映後の確認

- トップページが表示される
- スマートフォン用トップ画像が表示される
- 全作品カードから作品詳細ページへ移動できる
- メイン画像とギャラリー画像が表示される
- ギャラリーの左右操作、スワイプ、選択アイコンが動作する
- YouTube動画、YouTubeチャンネル、SNSリンクが正しく開く
- PCとスマートフォンの両方で大きな崩れがない

確認用URL：

https://shimak0.github.io/GeidaiGameYusi26Web/index.html

## GitHub Pagesの公開元を切り替える

GitHub Pagesは `.github/workflows/pages.yml` を使い、`public/` だけを公開します。

構成変更をGitHubへpushした後、リポジトリ管理者が次の操作を行ってください。

1. GitHubのリポジトリページを開く
2. `Settings` を開く
3. 左メニューの `Pages` を開く
4. `Build and deployment` の `Source` を `GitHub Actions` に変更する
5. `Actions` タブで `Deploy GitHub Pages` を開く
6. 自動実行されていない場合は `Run workflow` から `main` を実行する
7. `deploy` ジョブが成功したことを確認する
8. 確認用URLでトップページと作品ページを確認する

以後は `main` へpushされるたびに、`public/` の検査後、GitHub Pagesへ自動反映されます。

切り替え前のGitHub Pagesはリポジトリ直下を公開しているため、この構成変更をpushしてから切り替えが完了するまで、一時的にページを表示できない可能性があります。push後、続けてPages設定を変更してください。

## 補足

Adobe Fonts、Simple Icons、YouTube埋め込みは外部サービスを利用しています。本番環境からインターネットへ接続できる必要があります。

終了コード `127` が表示された場合は、エディターの「Run Code」ではなく、VS Codeの統合ターミナルから実行してください。
