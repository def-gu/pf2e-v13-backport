#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
source "$ROOT/config.sh"

WORK=${WORK:-./work}
TREE="$WORK/v13build"
REPO="$WORK/pf2e-repo"
SET="$ROOT/docs/backport_final.json"

[ -d "$REPO/.git" ] || { echo "run ./run.sh fetch first"; exit 1; }

BASE=$(git -C "$REPO" rev-parse "$PF2E_V13_REF")

if [ ! -d "$TREE" ]; then
    git -C "$REPO" worktree add -f -b v13-patched "$(cd "$WORK" && pwd)/v13build" "$PF2E_V13_REF"
fi

git -C "$TREE" checkout -q -f "$BASE"
git -C "$TREE" clean -qfd src

python3 - "$REPO" "$TREE" "$SET" <<'PY'
import json, subprocess, sys
repo, tree, setfile = sys.argv[1:4]
records = json.load(open(setfile, encoding='utf-8'))
ok = 0
for rec in records:
    diff = subprocess.run(
        ['git', '-C', repo, 'format-patch', '-1', '--stdout', rec['sha'], '--',
         'src/', ':(exclude)src/module/migration/migrations/*'],
        capture_output=True, text=True).stdout
    r = subprocess.run(['git', '-C', tree, 'apply', '--index', '-'],
                       input=diff, capture_output=True, text=True)
    if r.returncode == 0:
        ok += 1
    else:
        print(f"did not apply: {rec['sha']} {rec['subject'][:60]}")
print(f'applied {ok}/{len(records)}')
PY

cd "$TREE"
[ -d node_modules ] || npm ci --no-audit --no-fund

mkdir -p .shim
cat > .shim/pnpm <<'EOF'
#!/bin/sh
if [ "$1" = "run" ]; then
    shift
    script="$1"
    shift
    exec npm run "$script" -- "$@"
fi
exec npm "$@"
EOF
chmod +x .shim/pnpm
export PATH="$PWD/.shim:$PATH"
export NODE_OPTIONS=--max-old-space-size=3072

npx tsc --noEmit

SYSTEM_ID=pf2e npx vite build

echo
echo "built: $TREE/dist/pf2e"
echo "install everything except packs/ and system.json over $SYSTEM_DIR"
