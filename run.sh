#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
source ./config.sh

WORK=${WORK:-./work}
mkdir -p "$WORK"

step_fetch() {
    if [ -d "$WORK/pf2e-repo/.git" ]; then
        git -C "$WORK/pf2e-repo" fetch --all --tags --prune
    else
        git clone --filter=blob:none https://github.com/foundryvtt/pf2e.git "$WORK/pf2e-repo"
    fi
    git -C "$WORK/pf2e-repo" checkout -q -f "$PF2E_TAG"

    rm -rf "$WORK/v13packs"
    mkdir -p "$WORK/v13packs"
    git -C "$WORK/pf2e-repo" archive "$PF2E_V13_REF" packs/pf2e system.pf2e.json \
        | tar x -C "$WORK/v13packs"
    echo "fetched $PF2E_TAG and baseline $PF2E_V13_REF"
}

step_scope() {
    cd "$WORK" && python3 ../scripts/scope_full.py
}

step_merge() {
    cd "$WORK" && python3 ../scripts/merge_system.py
    cd "$WORK" && python3 - <<'PY'
import os, shutil
n = 0
for pack in os.listdir('pf2e-repo/packs/pf2e'):
    src = os.path.join('pf2e-repo/packs/pf2e', pack, '_folders.json')
    dst = os.path.join('merged-out/packs', pack, '_folders.json')
    if os.path.exists(src) and os.path.isdir(os.path.dirname(dst)):
        shutil.copy(src, dst); n += 1
print(f'carried {n} folder definitions')
PY
    cd "$WORK" && SYSTEM_DIR="$SYSTEM_DIR" python3 ../scripts/prepare_side.py
}

step_compile() {
    cd "$WORK" && rm -rf merged-out/packs-compiled
    cd "$WORK" && node ../scripts/compile-system.mjs \
        merged-out/packs merged-out/packs-compiled merged-out/side/system.json
}

step_verify() {
    cd "$WORK" && node ../scripts/verify-system.mjs
}

step_deploy() {
    [ -d "$WORK/merged-out/packs-compiled" ] || { echo "run compile first"; exit 1; }
    local stamp backup
    stamp=$(date +%Y%m%d-%H%M%S)
    backup="$BACKUP_ROOT/pf2e-system-$stamp"

    [ -n "$FOUNDRY_SERVICE" ] && systemctl stop "$FOUNDRY_SERVICE" && sleep 2

    mkdir -p "$backup"
    cp -a "$SYSTEM_DIR/packs" "$backup/packs"
    cp -a "$SYSTEM_DIR/lang" "$backup/lang"
    cp -a "$SYSTEM_DIR/system.json" "$backup/system.json"
    echo "backed up to $backup"

    rm -rf "$SYSTEM_DIR/packs"
    cp -a "$WORK/merged-out/packs-compiled" "$SYSTEM_DIR/packs"
    cp -a "$WORK/merged-out/side/system.json" "$SYSTEM_DIR/system.json"
    cp -a "$WORK/merged-out/side/lang/." "$SYSTEM_DIR/lang/"

    local companion="$WORK/merged-out/side/pf2e-remaster-traits-v13"
    [ -d "$companion" ] && rm -rf "$MODULES_DIR/pf2e-remaster-traits-v13" \
        && cp -a "$companion" "$MODULES_DIR/"

    chown -R "$(stat -c '%U:%G' "$FOUNDRY_DATA")" "$SYSTEM_DIR" || true

    [ -n "$FOUNDRY_SERVICE" ] && systemctl start "$FOUNDRY_SERVICE"

    cat <<EOF

deployed. rollback:
  systemctl stop $FOUNDRY_SERVICE
  rm -rf $SYSTEM_DIR/packs && cp -a $backup/packs $SYSTEM_DIR/packs
  cp -a $backup/system.json $SYSTEM_DIR/system.json
  cp -a $backup/lang/. $SYSTEM_DIR/lang/
  systemctl start $FOUNDRY_SERVICE
EOF
}

case "${1:-}" in
    fetch|scope|merge|compile|verify|deploy) "step_$1" ;;
    *) echo "usage: $0 {fetch|scope|merge|compile|verify|deploy}"; exit 1 ;;
esac
