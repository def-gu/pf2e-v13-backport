import json, os, collections

MERGED = 'merged-out/packs'
MANIFEST = 'merged-out/side/system.json'
RELEASES = {
    '2.1.4 (installed, v13 line)':
        '/home/gm/fvtt-data-1/Data/modules/pf2e-ru/data/community/pf2e/packs',
    '2.2.0 (v14 line)':
        'ru220/data/community/pf2e/packs',
    'master (verified 8.4.0)':
        'rumaster/data/community/pf2e/packs',
}

manifest = json.load(open(MANIFEST, encoding='utf-8'))
pack_id_by_dir = {p['path'].rstrip('/').split('/')[-1]: p['name']
                  for p in manifest['packs']}

content = collections.defaultdict(set)
for d in sorted(os.listdir(MERGED)):
    p = os.path.join(MERGED, d)
    if not os.path.isdir(p):
        continue
    pid = pack_id_by_dir.get(d, d)
    for fn in os.listdir(p):
        if not fn.endswith('.json') or fn == '_folders.json':
            continue
        try:
            doc = json.load(open(os.path.join(p, fn), encoding='utf-8'))
        except Exception:
            continue
        if isinstance(doc, dict) and doc.get('name'):
            content[pid].add(doc['name'])

total_docs = sum(len(v) for v in content.values())
print(f'merged content: {total_docs} named documents across {len(content)} packs\n')

for label, root in RELEASES.items():
    if not os.path.isdir(root):
        print(f'{label}: not found at {root}\n')
        continue
    covered = 0
    per_pack = {}
    for fn in os.listdir(root):
        if not fn.endswith('.json'):
            continue
        pid = fn[:-5]
        pid = pid[5:] if pid.startswith('pf2e.') else pid
        try:
            data = json.load(open(os.path.join(root, fn), encoding='utf-8'))
        except Exception:
            continue
        entries = data.get('entries')
        names = set(entries) if isinstance(entries, dict) else set()
        hit = names & content.get(pid, set())
        covered += len(hit)
        if content.get(pid):
            per_pack[pid] = (len(hit), len(content[pid]))
    pct = 100 * covered / total_docs if total_docs else 0
    print(f'{label}')
    print(f'  переведено {covered} из {total_docs}  ({pct:.1f}%)')
    worst = sorted(((h / t if t else 1), p, h, t)
                   for p, (h, t) in per_pack.items() if t >= 100)
    print('  худшее покрытие среди крупных паков:')
    for frac, p, h, t in worst[:6]:
        print(f'    {p:34s} {h:5d}/{t:<5d} {100*frac:5.1f}%')
    print()
