#!/bin/zsh

set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT="${1:-$ROOT/GeidaiGameYusi26Web-production.zip}"
STAGE="$(mktemp -d)"

trap 'rm -rf "$STAGE"' EXIT

for command_name in mktemp cp rsync zip unzip; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "必要なコマンドが見つかりません: $command_name" >&2
    exit 127
  fi
done

mkdir -p \
  "$STAGE/Image/works" \
  "$STAGE/Zen_Kaku_Gothic_New"

cp "$ROOT/index.html" "$STAGE/"
cp -R "$ROOT/works" "$ROOT/assets" "$STAGE/"

cp \
  "$ROOT/Image/TopImage.jpg" \
  "$ROOT/Image/GeidaiMap.jpg" \
  "$ROOT/Image/UnderImage.jpg" \
  "$STAGE/Image/"

rsync -a --prune-empty-dirs \
  --include='*/' \
  --include='*.jpg' \
  --include='*.png' \
  --exclude='*' \
  "$ROOT/Image/works/" "$STAGE/Image/works/"

cp \
  "$ROOT/Zen_Kaku_Gothic_New/ZenKakuGothicNew-Regular.ttf" \
  "$ROOT/Zen_Kaku_Gothic_New/ZenKakuGothicNew-Medium.ttf" \
  "$ROOT/Zen_Kaku_Gothic_New/ZenKakuGothicNew-Bold.ttf" \
  "$ROOT/Zen_Kaku_Gothic_New/OFL.txt" \
  "$STAGE/Zen_Kaku_Gothic_New/"

rm -f "$OUTPUT"
(
  cd "$STAGE"
  COPYFILE_DISABLE=1 zip -qr "$OUTPUT" . \
    -x '*.DS_Store' '__MACOSX/*'
)

echo "本番用ZIPを作成しました:"
echo "$OUTPUT"
unzip -l "$OUTPUT"
