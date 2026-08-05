import re, subprocess, sys

REPO = sys.argv[1] if len(sys.argv) > 1 else 'pf2e-repo'
REF = sys.argv[2] if len(sys.argv) > 2 else 'origin/v13-dev'
OUT = sys.argv[3] if len(sys.argv) > 3 else 're_v13.txt'

src = subprocess.run(
    ['git', '-C', REPO, 'show', f'{REF}:src/module/rules/index.ts'],
    capture_output=True, text=True, check=True).stdout

block = re.search(r'class RuleElements\b.*?\n\}', src, re.S)
if not block:
    raise SystemExit('rule element registry not found in src/module/rules/index.ts')

keys = sorted(set(re.findall(r'^\s{8}([A-Za-z][A-Za-z0-9]*):', block.group(0), re.M)))
if len(keys) < 20:
    raise SystemExit(f'implausible rule element count: {len(keys)}')

open(OUT, 'w', encoding='utf-8').write('\n'.join(keys) + '\n')
print(f'rule elements implemented by {REF}: {len(keys)} -> {OUT}')
