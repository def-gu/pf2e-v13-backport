# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `scripts/check-module.mjs`, which resolves every core API reference in a module against the installed Foundry build and reports the core version stamped on its packed documents
- `scripts/sync-translation.sh`, which polls the translation repository, pulls only what changed into a shallow clone, backs up the installed dictionaries and swaps them
- `docs/backport-audit.md`, recording the per-commit review of the backported code fixes after the blast bug
- English README as the canonical document, with the Russian text moved to `README.ru.md`

### Removed

- Code backport tooling and notes, which need manual verification and do not belong in a pipeline aimed at end users

## [7.13.4] - 2026-08-15

### Fixed

- Kineticist elemental blast now scales its damage dice with level again. A backported v14 commit (#22098) passed the rule predicate through `resolveValue`, which on the v13 path validated it as a dice-number; the predicate string failed that check and the rule was permanently marked `ignored`. The commit is reverted, leaving 60 backported fixes. No DamageAlteration in the content uses injected predicates, so the revert changes nothing else. This affected every DamageAlteration with an `@actor.level` formula, not only blast.

## [7.13.3] - 2026-08-15

### Fixed

- Compendium packs are now built with the upstream pf2e pack pipeline instead of a custom compiler. The custom step skipped slug generation, leaving about half of all documents without a `system.slug`; code that looks items up by slug failed silently, most visibly the kineticist elemental blast. All top-level documents now carry a slug, matching the official build.

## [7.13.2] - 2026-08-15

### Added

- Full trait config from pf2e 8.4.0. Fixes validation errors for remaster content whose traits (kholo, tripkee, necromancer, runesmith, thrall, invocation and others) the frozen 7.12.2 code did not declare.

## [7.13.1] - 2026-08-11

### Fixed

- Compendium Browser equipment sorting by price, which silently sorted by name because the equipment index omitted the field the sorter reads

## [7.13.0] - 2026-08-06

First published package. Installable through the Install System dialog in Foundry.

### Added

- Content from pf2e 8.4.0 merged into the frozen 7.12.2 system, 29544 documents in 97 compendiums
- Compendiums for Hell's Destiny, Bastion of Blasphemies and Troubles in Grayce
- Companion module registering 17 traits that 8.x content uses and 7.12.2 does not declare
- 61 upstream fixes from the v14 line, each verified by compilation

### Fixed

- Embedded documents written under their own keys, so journals load and creatures keep their items
- Compendium links resolved to ids with the pack from the link honoured, so classes grant their features
- `_stats.coreVersion` stamped with a v13 version, so Foundry accepts the documents

[Unreleased]: https://github.com/def-gu/pf2e-v13-backport/compare/7.13.1...HEAD
[7.13.1]: https://github.com/def-gu/pf2e-v13-backport/compare/7.13.0...7.13.1
[7.13.0]: https://github.com/def-gu/pf2e-v13-backport/releases/tag/7.13.0
[7.13.4]: https://github.com/def-gu/pf2e-v13-backport/releases/tag/7.13.4
[7.13.3]: https://github.com/def-gu/pf2e-v13-backport/releases/tag/7.13.3
[7.13.2]: https://github.com/def-gu/pf2e-v13-backport/releases/tag/7.13.2
