# Кандидаты на бэкпорт кода

Из 190 коммитов апстрима, затрагивающих `src/` (без миграций), **98 применяются
на 7.12.2 чисто** строгим `git apply`. Из них 27 чинят саму механику v14
(Regions, Levels, ApplicationV2, замена ключей удаления на `ForcedDeletion`) —
на v13 они либо бесполезны, либо вредны, потому что там нужны префиксы `-=`.
Остаётся **71**.

Проверялось воспроизводимо: `scripts/code_backport_strict.py` прогоняет каждый
коммит через `git apply --check` против рабочего дерева `v13-dev`. Строгий
режим, без `--3way`: трёхстороннее слияние даёт 97% и вводит в заблуждение.

> Применение требует форка pf2e 7.12.2 и пересборки: установленная система —
> скомпилированный бандл, патч в него не положишь.

## Багфиксы (25)

| commit | что чинит | область |
|---|---|---|
| `25e5715de` | Fix inventory and basic tags search icons | src/styles |
| `e2317b287` | Fix sizing of pips in character and familiar sheets | src/styles |
| `36752d136` | Fix double-barrel icon on PC sheet (#22004) | src/styles |
| `319661cdc` | Fix Compendium Browser header controls (#22009) | src/module |
| `e4bcf6047` | Fix empty tooltips flashing when hovering over the effect panel (#22052) | src/module |
| `9bae13ee2` | Fix setting always-show-dialog checkbox state in `DamageModifierDialog` (#22072) | src/module |
| `06c365b47` | Fix troop creation in unviewed scenes (#22108) | src/module |
| `e65e4e514` | Fix tag strikethrough when rerolling untrained improv using mythic (#22145) | src/module |
| `2a8de0900` | Fix calculation of critical damage given precision immunity (#21932) | src/module |
| `a7ed3c531` | Fix migration choking on embedded spells without flags (#22207) | src/module |
| `7e3903b68` | Fix errors deleting min and max effect badge fields (#22209) | src/module |
| `b77619817` | Fix Item Transfer message localization (#22268) | src/module |
| `715d3ca3b` | Fix icon of add/remove currency dialog (#22353) | src/module |
| `ea9e0e3ef` | Fix DOM helpers returning null cross-window in PopOut! (#22434) | src/util |
| `4fcd3122c` | Fix setting initial value of AuraEffectSchema#effects#affects field (#22480) | src/module |
| `d677dc968` | Fix attribute builder breaking after opening it for a second character (#22488) | src/module |
| `bc6f1a4f0` | Fix total price not updating on item transfer dialogs (#22542) | src/module |
| `c08c8a942` | Fix background color on dragged equipment (#22554) | src/styles |
| `b66101b75` | Fix runes added to handwraps via item alterations not applying to unarmed strikes (#22565) | src/module |
| `4a8e57a5d` | Fix senses granted via Details not upgrading (#22586) | src/module |
| `8e4dddc87` | Fix issues with transferring credits (#22588) | src/module |
| `4f35a5efd` | Fix ammo quantity input when there is more than one type (#22645) | src/module |
| `26e103eb6` | Fix weapon trait toggles on attached weapons (#22653) | src/module |
| `24d7d34f4` | Fix double applied penalties when battle form statistics are compared with actor's own (#22647) | src/module |
| `e5083d51c` | Fix image path for UBP item/currency (#22800) | src/module |

## Улучшения и новая автоматизация (46)

| commit | что даёт | область |
|---|---|---|
| `36008d0ed` | Apply minor fixes to loot sheet styling | src/styles |
| `3e10cb824` | Increase `SceneConfig` width | src/module |
| `b2e8e632b` | Update some deletions in feat sheet | src/module |
| `06ebbdb36` | Pass along `Scene#view` options (#21970) | src/module |
| `6ebbdef62` | Restore token effect icons (#21990) | src/module |
| `e7fac23f4` | Refactor `EncounterPF2e` to utilize core turn-event handlers (#22077) | src/module |
| `b1f5003cf` | Resolve injected properties in DamageAlteration predicates (#22098) | src/module |
| `86f091171` | Propagate elite/weak updates to all troop siblings (#22107) | src/module |
| `5cf893e72` | Use modifier type to find proficiency modifier in mythic rerolls (#22110) | src/module |
| `5f19d7fec` | Add draconic benefactors from draconic codex to dragon disciple choices (#21978) | src/module |
| `42ea8a49d` | Avoid coercing boost to number in trait config (#22165) | src/module |
| `c5a25057d` | Prevent troop token flags from being saved to prototype tokens (#22167) | src/module |
| `5189f2530` | Assign unique slug for each flat damage instance in NPC attacks (#22204) | src/module |
| `1d256f8ef` | Correct instances of "sf2e remaster" table classes in Journals and select NPC entries (#22227) | src/module, src/scripts |
| `5693fc172` | Add sniper weapon crit specialization damage automatically (#22234) | src/module |
| `b6dda73a7` | Refresh token bars on Temp HP updates. (#22246) | src/module |
| `8c62342ce` | Include spell attack and dc domains for special statistic spellcasting (#22281) | src/module |
| `58d6451ba` | Restore missing radio buttons in shield block dialog (#22286) | src/styles |
| `d405a2566` | Add expend tag to weapon description and strikes (#22276) | src/module |
| `b4f2e3d0d` | Allow "base" actor and item subtypes to construct (#22297) | src/module |
| `333235651` | Add weapon boost automation (#22298) | src/module, src/scripts |
| `8d64043ea` | Set `ignored` if predicate fails in `StrikeRuleElement#beforePrepareData` (#22317) | src/module |
| `5e5e5ecd8` | Include piloting/computers in RK skills list in party sheet (#22328) | src/module |
| `d94c684bc` | Add {item|id}-{meleeOrRanged}-damage domain to attacks, to enable ammunition rules (#22332) | src/module |
| `199311a09` | Set default token ring to steel in sf2e (#22352) | src/scripts |
| `4494a0909` | Patch a typo in mandatoryMelee regexp (#22398) | src/module |
| `c95e08a57` | Preserve token mirror state when applying TokenImage scale override (#22414) | src/module |
| `a9cb28709` | Hide ActorsDeadAtZero setting from players (#22355) | src/scripts |
| `e55435a4a` | Add RuleElement for Seugathi Guard's Magic Item Mastery feature (#22460) | src/scripts |
| `5014e1a39` | Improve Dice So Nice integration with damage types (#22456) | src/module, src/scripts |
| `ceb762946` | Remove padding from traits and paizo-style (#22309) | src/styles |
| `1e16270e7` | Apply each persistent damage from dragged formula (#22503) | src/module |
| `513a87eb9` | Apply roll options to inline damage rolled from effect tooltips (#22508) | src/module |
| `220b300b1` | Include origin item roll options in effects dragged from a sheet (#22514) | src/scripts |
| `96a499492` | Prevent chat bubbles if message doesn't look like in-character text (#22525) | src/module |
| `b0cd9544d` | Improve trade initiation: party-sheet member drops, request expiry with alerts on both sides, prevent sending to familiars (#22520) | src/module |
| `830946c5e` | Improve visual accessibility of spell slot number input (#22555) | src/styles |
| `eac9ba3aa` | Add missing Skirmish trait and skirmish actions (#22589) | src/scripts |
| `74bd0afc5` | Remove manipulate trait from alchemical bomb strikes (#22621) | src/module |
| `20a14cd71` | Snapshot area fire save dc in chat message context (#22626) | src/module |
| `8f586ffcd` | Always use action image for unusable actions in character sheet (#22669) | src/module |
| `127f53569` | Fill in schema definitions for `GrantItemRuleElement#onDeleteActions` and `#preselectChoices` (#22686) | src/module |
| `6c853b4a8` | Update weapon damage die calculation for errata (#21924) | src/module |
| `93bc5a93c` | Add Beyond the Blood Door Player's Guide content (#22735) | src/scripts |
| `387834a5d` | Convert `LootNPCsPopup` to DialogV2 (#22732) | src/module, src/styles |
| `669dc661d` | Add content from Impossible magic (#22769) | src/module, src/scripts |

## Как применить

```bash
git clone https://github.com/foundryvtt/pf2e.git
cd pf2e && git checkout -b v13-patched origin/v13-dev
git cherry-pick <commit> ...
npm install && npm run build
```

Собранное дерево кладётся поверх `Data/systems/pf2e/`, но **не** поверх
папки `packs/` — её пишет основной конвейер.

Порядок применения имеет значение: коммиты перечислены в хронологическом
порядке, и часть поздних опирается на ранние.
