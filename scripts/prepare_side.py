import json, os, shutil, collections

INSTALLED = os.environ.get('SYSTEM_DIR',
                           '/home/gm/fvtt-data-1/Data/systems/pf2e')
NEW_MANIFEST = 'pf2e-repo/system.pf2e.json'
NEW_LANG = 'pf2e-repo/static/lang'
OUT = 'merged-out/side'

os.makedirs(OUT, exist_ok=True)

cur = json.load(open(os.path.join(INSTALLED, 'system.json'), encoding='utf-8'))
upstream = json.load(open(NEW_MANIFEST, encoding='utf-8'))
have = {p['name'] for p in cur['packs']}
added = [p for p in upstream['packs'] if p['name'] not in have]
cur['packs'].extend(added)
json.dump(cur, open(os.path.join(OUT, 'system.json'), 'w', encoding='utf-8'),
          indent=4, ensure_ascii=False)
print(f'system.json : {len(have)} -> {len(cur["packs"])} packs '
      f'(added {[p["name"] for p in added]})')
print(f'  version stays {cur["version"]}, compatibility {cur["compatibility"]}')

def flatten(o, p=''):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from flatten(v, f'{p}.{k}' if p else k)
    else:
        yield p, o


def nest(flat):
    out = {}
    for k, v in flat.items():
        parts = k.split('.')
        cur = out
        for part in parts[:-1]:
            nxt = cur.get(part)
            if not isinstance(nxt, dict):
                nxt = {}
                cur[part] = nxt
            cur = nxt
        cur[parts[-1]] = v
    return out


os.makedirs(os.path.join(OUT, 'lang'), exist_ok=True)
for fn in sorted(os.listdir(os.path.join(INSTALLED, 'lang'))):
    if not fn.endswith('.json'):
        continue
    mine = dict(flatten(json.load(open(os.path.join(INSTALLED, 'lang', fn), encoding='utf-8'))))
    up_path = os.path.join(NEW_LANG, fn)
    if not os.path.exists(up_path):
        print(f'lang/{fn}: no upstream counterpart, left as is')
        continue
    theirs = dict(flatten(json.load(open(up_path, encoding='utf-8'))))
    new_keys = {k: v for k, v in theirs.items() if k not in mine}
    changed = {k: v for k, v in theirs.items() if k in mine and mine[k] != v}
    merged = dict(mine)
    merged.update(theirs)
    json.dump(nest(merged), open(os.path.join(OUT, 'lang', fn), 'w', encoding='utf-8'),
              indent=4, ensure_ascii=False, sort_keys=True)
    print(f'lang/{fn}: {len(mine)} -> {len(merged)} keys '
          f'(+{len(new_keys)} new, {len(changed)} updated)')

TRAITS = {
    'coshyco': 'PF2E.TraitCoshyco', 'disease': 'PF2E.TraitDisease',
    'extradimensional': 'PF2E.TraitExtradimensional',
    'gnarefuroid': 'PF2E.TraitGnarefuroid', 'impossible': 'PF2E.TraitImpossible',
    'invocation': 'PF2E.TraitInvocation', 'kholo': 'PF2E.TraitKholo',
    'linguistic': 'PF2E.TraitLinguistic', 'necromancer': 'PF2E.TraitNecromancer',
    'nuar': 'PF2E.TraitNuar', 'runesmith': 'PF2E.TraitRunesmith',
    'secret': 'PF2E.TraitSecret', 'skirmish': 'PF2E.TraitSkirmish',
    'thrall': 'PF2E.TraitThrall', 'tripkee': 'PF2E.TraitTripkee',
    'visual': 'PF2E.TraitVisual', 'vulkarisu': 'PF2E.TraitVulkarisu',
}
MODULE_ID = 'pf2e-remaster-traits-v13'
mod = {
    'id': MODULE_ID,
    'title': 'PF2e Remaster Traits (v13)',
    'description': 'Registers the traits introduced by pf2e 8.x content that '
                   'the frozen 7.12.2 code does not declare.',
    'version': '1.0.0',
    'compatibility': {'minimum': '13', 'verified': '13.351', 'maximum': '13'},
    'relationships': {'systems': [{'id': 'pf2e', 'type': 'system',
                                   'compatibility': {'minimum': '7.12.2'}}]},
    'flags': {MODULE_ID: {'pf2e-homebrew': {
        c: dict(TRAITS) for c in
        ('classTraits', 'featTraits', 'spellTraits', 'equipmentTraits',
         'actionTraits', 'creatureTraits', 'weaponTraits')
    }}},
}
md = os.path.join(OUT, MODULE_ID)
os.makedirs(md, exist_ok=True)
json.dump(mod, open(os.path.join(md, 'module.json'), 'w', encoding='utf-8'),
          indent=4, ensure_ascii=False)
print(f'companion module: {MODULE_ID}, {len(TRAITS)} traits x '
      f'{len(mod["flags"][MODULE_ID]["pf2e-homebrew"])} collections')
