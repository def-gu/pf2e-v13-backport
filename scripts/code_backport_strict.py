import subprocess, collections, json, re, sys, os

REPO = 'pf2e-repo'
TREE = 'v13tree'
MB = '37d1936e51742569983a9ef396694c9293f7574a'
HEAD = 'pf2e-8.4.0'
EXCLUDE = ':(exclude)src/module/migration/migrations/*'


def git(*args, cwd=REPO, **kw):
    return subprocess.run(['git', *args], cwd=cwd, capture_output=True,
                          text=True, **kw)


commits = git('rev-list', '--reverse', f'{MB}..{HEAD}', '--',
              'src/', EXCLUDE).stdout.split()
print(f'commits touching src/ (excluding migrations): {len(commits)}')

clean, dirty = [], []
for i, sha in enumerate(commits, 1):
    subject = git('log', '-1', '--format=%s', sha).stdout.strip()
    diff = git('format-patch', '-1', '--stdout', sha, '--',
               'src/', EXCLUDE).stdout
    if not diff.strip():
        continue
    check = subprocess.run(
        ['git', 'apply', '--check', '-'],
        cwd=TREE, input=diff, capture_output=True, text=True)
    files = [l.split()[-1] for l in diff.splitlines()
             if l.startswith('+++ b/')]
    rec = {'sha': sha[:9], 'subject': subject, 'files': files}
    (clean if check.returncode == 0 else dirty).append(rec)
    if i % 40 == 0:
        print(f'  ... {i}/{len(commits)}', file=sys.stderr)

total = len(clean) + len(dirty)
print()
print(f'applies cleanly onto 7.12.2 : {len(clean)}  ({100*len(clean)/total:.0f}%)')
print(f'conflicts                   : {len(dirty)}  ({100*len(dirty)/total:.0f}%)')

json.dump({'clean': clean, 'dirty': dirty},
          open('code_backport_strict.json', 'w'), indent=1, ensure_ascii=False)


def top_areas(recs):
    c = collections.Counter()
    for r in recs:
        for f in r['files']:
            c['/'.join(f.split('/')[:3])] += 1
    return c


print('\nчисто ложится, по областям:')
for area, n in top_areas(clean).most_common(10):
    print(f'  {area:44s} {n}')
print('\nконфликтует, по областям:')
for area, n in top_areas(dirty).most_common(10):
    print(f'  {area:44s} {n}')

print('\nпримеры чисто ложащихся исправлений:')
for r in clean:
    if re.match(r'^Fix ', r['subject']):
        print(f"  {r['sha']}  {r['subject'][:78]}")
