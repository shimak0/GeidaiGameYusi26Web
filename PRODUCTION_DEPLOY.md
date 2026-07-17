# 本番環境向けZIP作成・アップロード手順

この手順では、`index.html` をエントリーポイントとして、本番公開に必要な静的ファイルだけをZIPにまとめます。

Pythonスクリプト、画像提出データ、CSV、運営用ドキュメントなどはZIPに含めません。

## 前提

- macOSのターミナルで実行する
- このリポジトリのルートディレクトリで実行する
- 作品画像の取り込みとページ再生成が完了している
- ブラウザでローカル表示を確認済みである

現在位置は次のコマンドで確認できます。

```sh
pwd
```

末尾が `GeidaiGameYusi26Web` になっていることを確認してください。

## ZIPの作成（推奨）

VS Codeで「ターミナル」→「新しいターミナル」を選択し、開いたターミナルで次の1行を実行します。

エディター右上の再生ボタンや「Run Code」ではなく、ターミナルへコマンドを入力してください。

```sh
zsh scripts/create_production_zip.sh
```

リポジトリ直下に次のファイルが作成されます。

```text
GeidaiGameYusi26Web-production.zip
```

同名のZIPがすでにある場合は、新しい内容で置き換えられます。

## ZIPの作成処理を直接実行する場合

スクリプトを使わずに実行する場合は、以下をまとめてターミナルへ貼り付けます。

```sh
set -e

ROOT="$(pwd)"
STAGE="$(mktemp -d)"
OUTPUT="$ROOT/GeidaiGameYusi26Web-production.zip"

trap 'rm -rf "$STAGE"' EXIT

mkdir -p \
  "$STAGE/Image/works" \
  "$STAGE/Zen_Kaku_Gothic_New"

# HTML・CSS・JavaScript
cp index.html "$STAGE/"
cp -R works assets "$STAGE/"

# トップページ・フッター・マップの画像
cp \
  Image/TopImage.jpg \
  Image/GeidaiMap.jpg \
  Image/UnderImage.jpg \
  "$STAGE/Image/"

# 作品画像だけをフォルダ階層を維持してコピー
rsync -a --prune-empty-dirs \
  --include='*/' \
  --include='*.jpg' \
  --include='*.png' \
  --exclude='*' \
  Image/works/ "$STAGE/Image/works/"

# 使用中のフォントとライセンス
cp \
  Zen_Kaku_Gothic_New/ZenKakuGothicNew-Regular.ttf \
  Zen_Kaku_Gothic_New/ZenKakuGothicNew-Medium.ttf \
  Zen_Kaku_Gothic_New/ZenKakuGothicNew-Bold.ttf \
  Zen_Kaku_Gothic_New/OFL.txt \
  "$STAGE/Zen_Kaku_Gothic_New/"

# 古い本番用ZIPを削除してから新しく作成
rm -f "$OUTPUT"
(
  cd "$STAGE"
  COPYFILE_DISABLE=1 zip -qr "$OUTPUT" . \
    -x '*.DS_Store' '__MACOSX/*'
)

# ZIPの内容を表示
unzip -l "$OUTPUT"
```

## ZIPに含まれるもの

```text
index.html
works/
  work-01.html
  ...
  work-21.html
assets/
  site.js
  work-detail.css
Image/
  TopImage.jpg
  GeidaiMap.jpg
  UnderImage.jpg
  works/
    work-01/
    ...
    work-21/
Zen_Kaku_Gothic_New/
```

作品フォルダには、公開ページから使用されるJPEG・PNG画像だけが入ります。

## ZIPに含まれないもの

次の運営用・生成用ファイルは本番公開に不要なため除外されます。

```text
.git/
scripts/
incoming/
docs/
templates/
IMAGE_SUBMISSION.md
PRODUCTION_DEPLOY.md
work-detail.html
Image/placeholders/
Image/works/*/links.txt
```

## アップロード前の確認

ZIP内の先頭階層に `index.html` があることを確認します。

```sh
unzip -l GeidaiGameYusi26Web-production.zip
```

必要に応じて一度展開し、構成を確認します。

```sh
CHECK_DIR="$(mktemp -d)"
unzip -q GeidaiGameYusi26Web-production.zip -d "$CHECK_DIR"
find "$CHECK_DIR" -maxdepth 2 -type f | sort
```

確認後は一時フォルダを削除できます。

```sh
rm -rf "$CHECK_DIR"
```

## 本番環境へのアップロード依頼

担当者へは、次の内容を伝えてください。

1. `GeidaiGameYusi26Web-production.zip` を展開する
2. 展開後の `index.html` が公開ディレクトリ直下に来るよう配置する
3. 既存の静的ファイルをZIPの内容で置き換える
4. 不要になった旧画像が残らないよう、可能であれば公開ディレクトリを入れ替える

差分ファイルだけを追加すると、削除済み画像や古いHTMLが本番環境に残る可能性があります。原則としてZIPの内容一式で置き換えてください。

## 反映後の確認

最低限、次の項目を確認します。

- トップページが表示される
- 全作品カードから作品詳細ページへ移動できる
- 更新したメイン画像とギャラリー画像が表示される
- ギャラリーの左右操作・スワイプ・選択アイコンが動作する
- YouTube動画、YouTubeチャンネル、SNSリンクが正しく開く
- PC表示とスマートフォン表示の両方で大きな崩れがない

確認用URL：

https://shimak0.github.io/GeidaiGameYusi26Web/index.html

## 補足

Adobe Fonts、Simple Icons、YouTube埋め込みは外部サービスを利用しています。本番環境からインターネットへ接続できる必要があります。

## 終了コード127が表示された場合

終了コード `127` は、実行しようとしたコマンドが見つからない場合に表示されます。

まず、VS Codeのエディター上で選択範囲を実行するのではなく、新しい統合ターミナルを開いて次のコマンドを実行してください。

```sh
zsh scripts/create_production_zip.sh
```

スクリプト内で必要なコマンドが見つからない場合は、該当するコマンド名が表示されます。

それでもターミナル自体が終了する場合は、次のコマンドでzshを確認します。

```sh
/bin/zsh -l -c 'echo "zsh OK"'
```

`zsh OK` が表示されない場合は、ZIP作成処理ではなく、VS Codeのターミナル設定または `~/.zprofile`、`~/.zshrc` などのシェル起動設定を確認してください。
