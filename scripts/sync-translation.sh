#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$ROOT/config.sh"

WORK=${WORK:-$ROOT/work}
CLONE="$WORK/pf2r"
STATE="$WORK/pf2r.sha"
TARGET="$MODULES_DIR/pf2e-ru/data/community"

mkdir -p "$WORK"

remote_sha=$(git ls-remote "$TRANSLATION_REPO" "$TRANSLATION_REF" | cut -f1)
[ -n "$remote_sha" ] || { echo "cannot reach $TRANSLATION_REPO"; exit 1; }

if [ -f "$STATE" ] && [ "$(cat "$STATE")" = "$remote_sha" ] && [ -d "$CLONE" ]; then
    echo "up to date: ${remote_sha:0:8}"
    exit 0
fi

if [ -d "$CLONE/.git" ]; then
    git -C "$CLONE" fetch -q --depth 1 origin "$TRANSLATION_REF"
    git -C "$CLONE" checkout -q -B "$TRANSLATION_REF" "origin/$TRANSLATION_REF"
    git -C "$CLONE" reflog expire --expire=now --all
    git -C "$CLONE" gc -q --prune=now
else
    git clone -q --depth 1 --branch "$TRANSLATION_REF" --single-branch \
        "$TRANSLATION_REPO" "$CLONE"
fi

[ -d "$CLONE/data/community" ] || { echo "no data/community in $TRANSLATION_REF"; exit 1; }
[ -d "$MODULES_DIR/pf2e-ru" ] || { echo "pf2e-ru is not installed at $MODULES_DIR"; exit 1; }

backup="$BACKUP_ROOT/pf2e-ru-community-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_ROOT"
cp -a "$TARGET" "$backup"

ls -1dt "$BACKUP_ROOT"/pf2e-ru-community-* 2>/dev/null | tail -n +4 | while read -r old; do
    rm -rf "$old"
done

rm -rf "$TARGET"
cp -a "$CLONE/data/community" "$TARGET"
chown -R "$(stat -c '%U:%G' "$MODULES_DIR/pf2e-ru")" "$TARGET" 2>/dev/null || true

echo "$remote_sha" > "$STATE"
echo "updated to ${remote_sha:0:8}, previous dictionaries in $backup"
echo "reload the world for Babele to pick them up"
