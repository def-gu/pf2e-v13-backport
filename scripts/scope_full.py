import json, os, collections

NEW = 'pf2e-repo/packs/pf2e'
OLD = 'v13packs/packs/pf2e'
SUPPORTED_RE = set(l.strip() for l in open('re_v13.txt') if l.strip())


def load(root):
    docs = {}
    for pack in sorted(os.listdir(root)):
        d = os.path.join(root, pack)
        if not os.path.isdir(d):
            continue
        for dp, _, fs in os.walk(d):
            for fn in fs:
                if not fn.endswith('.json'):
                    continue
                try:
                    doc = json.load(open(os.path.join(dp, fn), encoding='utf-8'))
                except Exception:
                    continue
                if isinstance(doc, dict) and doc.get('_id'):
                    docs[(pack, doc['_id'])] = doc
    return docs


def rule_keys(doc, out):
    if isinstance(doc, dict):
        if isinstance(doc.get('rules'), list):
            for r in doc['rules']:
                if isinstance(r, dict) and isinstance(r.get('key'), str):
                    out.add(r['key'])
        for v in doc.values():
            rule_keys(v, out)
    elif isinstance(doc, list):
        for v in doc:
            rule_keys(v, out)


print('loading ...')
new = load(NEW)
old = load(OLD)
print(f'  8.4.0  : {len(new)} documents')
print(f'  7.12.2 : {len(old)} documents')

added = updated = identical = 0
removed = 0
blocked = collections.Counter()
blocked_docs = 0
per_pack = collections.Counter()

for key, doc in new.items():
    keys = set()
    rule_keys(doc, keys)
    bad = keys - SUPPORTED_RE
    if bad:
        blocked_docs += 1
        for b in bad:
            blocked[b] += 1
        continue
    if key not in old:
        added += 1
        per_pack[key[0]] += 1
    elif json.dumps(old[key], sort_keys=True) != json.dumps(doc, sort_keys=True):
        updated += 1
        per_pack[key[0]] += 1
    else:
        identical += 1

for key in old:
    if key not in new:
        removed += 1

print()
print(f'документов к добавлению   : {added}')
print(f'документов к обновлению   : {updated}')
print(f'без изменений             : {identical}')
print(f'есть в 7.12.2, нет в 8.4.0: {removed}   (upstream удалил/переименовал)')
print(f'заблокировано по RE       : {blocked_docs}')
for k, c in blocked.most_common(10):
    print(f'    {k}: {c}')
print()
print('топ паков по объёму изменений:')
for p, c in per_pack.most_common(15):
    print(f'    {p:34s} {c}')
