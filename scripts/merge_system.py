import json, os, re, collections, sys

NEW = 'pf2e-repo/packs/pf2e'
OLD = 'v13packs/packs/pf2e'
OUT = 'merged-out/packs'
NEW_MANIFEST = 'pf2e-repo/system.pf2e.json'
OLD_MANIFEST = 'v13packs/system.pf2e.json'
KEEP_REMOVED = True

ID_RE = re.compile(r'^[A-Za-z0-9]{16}$')
LINK_RE = re.compile(
    r'Compendium\.(?P<pkg>pf2e|sf2e)\.(?P<pack>[A-Za-z0-9_-]+)\.'
    r'(?P<type>Item|Actor|JournalEntry|Macro|RollTable)\.(?P<ref>[^\]}"|#]+)')

OPTION_TOKEN = re.compile(r'^(inline|caption|cite|hr|classes)(=\S*)?$')


def split_options(ref):
    parts = ref.split(' ')
    cut = len(parts)
    while cut > 1 and OPTION_TOKEN.match(parts[cut - 1]):
        cut -= 1
    return ' '.join(parts[:cut]), (' ' + ' '.join(parts[cut:]) if cut < len(parts) else '')

stats = collections.Counter()


def dir_to_pack_id(manifest_path):
    m = json.load(open(manifest_path, encoding='utf-8'))
    return {p['path'].rstrip('/').split('/')[-1]: p['name'] for p in m['packs']}


def load(root):
    docs = collections.defaultdict(dict)
    for pack in sorted(os.listdir(root)):
        d = os.path.join(root, pack)
        if not os.path.isdir(d):
            continue
        for dp, _, fs in os.walk(d):
            for fn in sorted(fs):
                if not fn.endswith('.json'):
                    continue
                try:
                    doc = json.load(open(os.path.join(dp, fn), encoding='utf-8'))
                except Exception:
                    continue
                if isinstance(doc, dict) and doc.get('_id'):
                    docs[pack][doc['_id']] = doc
    return docs


print('loading source trees ...')
new = load(NEW)
old = load(OLD)
DIRMAP = dir_to_pack_id(NEW_MANIFEST)
PACK_ID_TO_DIR = {v: k for k, v in DIRMAP.items()}

merged = collections.defaultdict(dict)
for pack, docs in new.items():
    merged[pack].update(docs)

carried = 0
if KEEP_REMOVED:
    for pack, docs in old.items():
        for i, doc in docs.items():
            if i not in merged.get(pack, {}):
                merged[pack][i] = doc
                carried += 1

total = sum(len(v) for v in merged.values())
print(f'  merged set          : {total} documents in {len(merged)} packs')
print(f'  carried from 7.12.2 : {carried}')

name_map = collections.defaultdict(dict)
for pack, docs in merged.items():
    pid = DIRMAP.get(pack, pack)
    for i, doc in docs.items():
        n = doc.get('name')
        if n:
            name_map[pid].setdefault(n, i)


def resolve(pack_id, ref):
    if ID_RE.match(ref):
        stats['already id'] += 1
        return ref
    ids = name_map.get(pack_id, {})
    if ref in ids:
        stats['resolved'] += 1
        return ids[ref]
    alt = DIRMAP.get(pack_id)
    if alt and ref in name_map.get(alt, {}):
        stats['resolved (dir alias)'] += 1
        return name_map[alt][ref]
    stats['UNRESOLVED'] += 1
    stats[f'unresolved:{pack_id}'] += 1
    return None


def fix_string(s):
    def sub(m):
        ref, opts = split_options(m.group('ref').rstrip())
        got = resolve(m.group('pack'), ref)
        if got is None:
            return m.group(0)
        return (f"Compendium.{m.group('pkg')}.{m.group('pack')}."
                f"{m.group('type')}.{got}{opts}")
    return LINK_RE.sub(sub, s)


def fix(node):
    if isinstance(node, str):
        return fix_string(node)
    if isinstance(node, list):
        return [fix(v) for v in node]
    if isinstance(node, dict):
        return {k: fix(v) for k, v in node.items()}
    return node


print('resolving links ...')
if os.path.exists('merged-out'):
    import shutil
    shutil.rmtree('merged-out')

written = 0
for pack, docs in sorted(merged.items()):
    d = os.path.join(OUT, pack)
    os.makedirs(d, exist_ok=True)
    for i, doc in docs.items():
        fixed = fix(doc)
        with open(os.path.join(d, f'{i}.json'), 'w', encoding='utf-8') as f:
            json.dump(fixed, f, ensure_ascii=False, indent=2, sort_keys=True)
        written += 1

print(f'  documents written   : {written}')
print()
for k, v in stats.most_common(8):
    print(f'  {k:26s} {v}')
worst = [(v, k) for k, v in stats.items() if k.startswith('unresolved:')]
if worst:
    print('  worst unresolved packs:')
    for v, k in sorted(worst, reverse=True)[:6]:
        print(f'    {k[11:]:30s} {v}')
