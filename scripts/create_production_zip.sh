#!/bin/zsh

set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PUBLIC="$ROOT/public"
DIST="$ROOT/dist"
OUTPUT="${1:-$DIST/GeidaiGameYusi26Web-production.zip}"

for command_name in python3 zip unzip; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "必要なコマンドが見つかりません: $command_name" >&2
    exit 127
  fi
done

python3 "$SCRIPT_DIR/validate_public.py"

mkdir -p "${OUTPUT:h}"
rm -f "$OUTPUT"
(
  cd "$PUBLIC"
  COPYFILE_DISABLE=1 zip -qr "$OUTPUT" . \
    -x '*.DS_Store' '__MACOSX/*'
)

echo "本番用ZIPを作成しました:"
echo "$OUTPUT"
unzip -l "$OUTPUT"
