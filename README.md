[English] | [Русский](README.ru.md)

# pf2e content backport for Foundry v13

Current Pathfinder 2e books on Foundry v13, without moving to v14.

The pf2e maintainers froze the v13 branch at release 7.12.2 and moved to v14. Everything published since, including Impossible Magic, Hell's Destiny, Bastion of Blasphemies, Lost Omens High Seas, Secrets of the Unlit Star, Troubles in Grayce and NPC Core, ships for v14 only.

This brings it to v13.

## Install

Paste this manifest URL into the Install System dialog in Foundry.

```
https://github.com/def-gu/pf2e-v13-backport/releases/latest/download/system.json
```

The system id stays `pf2e`, so existing worlds keep working and need no changes.

The package carries all 8.4.0 content, 29544 documents in 97 compendiums, on top of the 7.12.2 code base.

## Build it yourself

Edit the paths in `config.sh`, then run the stages.

```bash
./run.sh fetch
./run.sh scope
./run.sh merge
./run.sh compile
./run.sh verify
sudo ./run.sh deploy
```

`scope` reports what would change before anything changes. `verify` checks the build before it is written.

Requirements are Foundry v13 with pf2e 7.12.2, Node and Python 3 on the same machine, and the ability to stop the server while packs are written. Linux with systemd is the target. On macOS the `deploy` stage needs adjusting, on Windows the shell scripts need WSL.

## Backups

`deploy` copies the current packs, language files and manifest into `BACKUP_ROOT` before writing anything, and prints the rollback command when it finishes. Rollback is a directory copy.

Verify that you can restore that copy before running `deploy` on a world you care about.

## Translation

Babele dictionaries key on the English document name, so a translation built for 8.x works on 7.12.2.

Take the branch built against the same content version. For 8.4.0 that is `master` in [gnuraco/pf2r](https://gitlab.com/gnuraco/pf2r), giving around 90 percent coverage. The same directory carries translations for 83 modules.

```bash
./scripts/sync-translation.sh
```

It polls for a new revision at a cost of 59 bytes, pulls only what changed into a shallow clone, backs up the dictionaries in place and swaps them. Safe to run from cron. Reload the world afterwards for Babele to pick up the change.

## Modules built for v14

Most run on v13 once their declarations are adjusted. Check one before touching it.

```bash
node scripts/check-module.mjs <module-directory>
```

The check reads the manifest, resolves every core API reference against the installed Foundry build, and reports the core version stamped on documents in the module compendiums. It says whether porting alone is enough or code changes are also needed.

```bash
node scripts/port-module.mjs <module-directory>
```

Porting rewrites `compatibility` in the manifest and `_stats.coreVersion` in the compendiums. Foundry refuses documents stamped with a core version above its own, which is the most common reason a v14 module appears broken.

## Updating

This is a snapshot. Each pf2e release means running the stages again after changing `PF2E_TAG`.

`scope` reports how many documents are blocked by missing rule elements. While that stays at zero, the approach holds.

## License

MIT for the scripts. Content is fetched from the pf2e repository at run time and is not redistributed here.

Released packages do redistribute the built system and carry the upstream Apache 2.0, OGL and ORC licenses. Not affiliated with the pf2e system maintainers or Paizo.
