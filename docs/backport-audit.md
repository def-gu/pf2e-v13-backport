# Backport audit

The kineticist elemental-blast dice-scaling bug (fixed in 7.13.4) came from one
backported commit that compiled cleanly but broke at runtime on v13: `b1f5003cf`
(#22098) passed a rule predicate through `resolveValue`, whose v13 path validates
the result as a `dice-number`. The predicate string failed that numeric check,
called `failValidation`, and the rule stayed permanently `ignored`.

That class of defect — semantically dependent on the v14 code path, invisible to
`tsc` — prompted an audit of the remaining commits.

## Method

The build now carries **60** backported commits (`b1f5003cf` reverted). Each was
classified by the files it touches, and every high-risk commit was scanned for the
patterns that made `b1f5003cf` dangerous: a `resolveValue` call on something other
than a rule value, direct `ignored` assignment, DataModel schema changes, v14-only
API, and `resolveInjectedProperties`.

Only `b1f5003cf` carried the `resolveValue(non-value)` pattern. It is reverted.
Two other commits matched a pattern and were read by hand; both are safe.

## High-risk commits (18)

| commit | verdict |
|---|---|
| `86f091171` Propagate elite/weak updates to all troop si | clean by pattern scan |
| `5f19d7fec` Add draconic benefactors from draconic codex | clean by pattern scan |
| `2a8de0900` Fix calculation of critical damage given pre | clean by pattern scan |
| `5693fc172` Add sniper weapon crit specialization damage | clean by pattern scan |
| `8c62342ce` Include spell attack and dc domains for spec | clean by pattern scan |
| `8d64043ea` Set `ignored` if predicate fails in `StrikeR | safe — sets ignored via ordinary predicate.test(), only on real predicate failure; not the resolveValue path |
| `5014e1a39` Improve Dice So Nice integration with damage | clean by pattern scan |
| `4fcd3122c` Fix setting initial value of AuraEffectSchem | clean by pattern scan |
| `b66101b75` Fix runes added to handwraps via item altera | clean by pattern scan |
| `24d7d34f4` Fix double applied penalties when battle for | clean by pattern scan |
| `127f53569` Fill in schema definitions for `GrantItemRul | safe — moves fields into the DataModel schema using v13-native field classes only, no v14-only fields |
| `6c853b4a8` Update weapon damage die calculation for err | clean by pattern scan |
| `c5a25057d` Prevent troop token flags from being saved t | clean by pattern scan |
| `b4f2e3d0d` Allow "base" actor and item subtypes to cons | clean by pattern scan |
| `333235651` Add weapon boost automation (#22298) | clean by pattern scan |
| `1e16270e7` Apply each persistent damage from dragged fo | clean by pattern scan |
| `b0cd9544d` Improve trade initiation: party-sheet member | clean by pattern scan |
| `74bd0afc5` Remove manipulate trait from alchemical bomb | clean by pattern scan |

## Medium and low risk (42)

Actor/item/system UI fixes, dialog fixes, content data, localization, styles and
icons. No rules-resolution or lifecycle code; considered safe without line review.

## Limitation

The scan catches the *known* pattern. A commit that silently relies on the v14
lifecycle ordering without a visible code pattern would not be caught statically —
it surfaces only at runtime on a specific mechanic, the way the blast bug did. The
diagnostic-module approach used to find that bug is the tool for any future one.

## If you re-run the backport

Do not re-add `b1f5003cf`. The set of 60 is what ships in 7.13.4 and later.
