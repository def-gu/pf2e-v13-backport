# Бэкпорт исправлений кода

**61 коммитов** апстрима из ветки v14 применены на pf2e 7.12.2,
проходят проверку типов и собираются.

## Как отбирались

Первый заход был ошибочным, и это стоит знать: отбор по `git apply` даёт
98 коммитов из 190, но `git apply` проверяет только текстовые контексты.
Код написан против типов v14, а переносится только `src/`, поэтому все 98
ложатся без конфликтов и дают **250 ошибок компиляции**. Чистая 7.12.2 при
этом собирается с нулём ошибок.

Настоящий критерий — компиляция. Каждый кандидат добавлялся к набору с
полной проверкой `tsc --noEmit` после каждого шага. Прошли 61 из 71.

| этап | коммитов |
|---|---|
| затрагивают `src/` (без миграций) | 190 |
| применяются строго `git apply` | 98 |
| не про механику v14 | 71 |
| **компилируются на 7.12.2** | **61** |

## Сборка

```bash
./build-system.sh
```

Скрипт создаёт ветку от `v13-dev`, применяет набор, проверяет типы и собирает.
Результат в `work/v13build/dist/pf2e/`.

Проверка того, что тулчейн воспроизводит апстрим: `vendor.mjs`,
`rolldown-runtime.mjs` и `template.json` в сборке побайтово совпадают с
файлами официального релиза 7.12.2. Отличаются только `pf2e.mjs` и стили.

## Установка

Скопировать из `dist/pf2e/` поверх `Data/systems/pf2e/` всё, **кроме**
`packs/` и `system.json`: паки пишет основной конвейер, а манифест содержит
добавленные компендиумы.

## Исправления (23)

| commit | что чинит | область |
|---|---|---|
| `25e5715de` | Fix inventory and basic tags search icons | styles/_fonts.scss, styles/actor |
| `e2317b287` | Fix sizing of pips in character and familiar sheets | styles/actor |
| `36752d136` | Fix double-barrel icon on PC sheet (#22004) | styles/actor |
| `319661cdc` | Fix Compendium Browser header controls (#22009) | module/apps |
| `e4bcf6047` | Fix empty tooltips flashing when hovering over the effect panel (#22052) | module/sheet |
| `2a8de0900` | Fix calculation of critical damage given precision immunity (#21932) | module/system |
| `715d3ca3b` | Fix icon of add/remove currency dialog (#22353) | module/actor |
| `ea9e0e3ef` | Fix DOM helpers returning null cross-window in PopOut! (#22434) | util/dom.ts |
| `4fcd3122c` | Fix setting initial value of AuraEffectSchema#effects#affects field (#22480) | module/rules |
| `d677dc968` | Fix attribute builder breaking after opening it for a second character (#22488) | module/actor |
| `bc6f1a4f0` | Fix total price not updating on item transfer dialogs (#22542) | module/actor |
| `c08c8a942` | Fix background color on dragged equipment (#22554) | styles/actor |
| `b66101b75` | Fix runes added to handwraps via item alterations not applying to unarmed strikes (#22565) | module/actor |
| `4a8e57a5d` | Fix senses granted via Details not upgrading (#22586) | module/item |
| `4f35a5efd` | Fix ammo quantity input when there is more than one type (#22645) | module/actor |
| `24d7d34f4` | Fix double applied penalties when battle form statistics are compared with actor's own (#22647) | module/rules |
| `e5083d51c` | Fix image path for UBP item/currency (#22800) | module/actor |
| `9bae13ee2` | Fix setting always-show-dialog checkbox state in `DamageModifierDialog` (#22072) | module/actor |
| `06c365b47` | Fix troop creation in unviewed scenes (#22108) | module/scene |
| `e65e4e514` | Fix tag strikethrough when rerolling untrained improv using mythic (#22145) | module/system |
| `a7ed3c531` | Fix migration choking on embedded spells without flags (#22207) | module/migration |
| `b77619817` | Fix Item Transfer message localization (#22268) | module/actor |
| `26e103eb6` | Fix weapon trait toggles on attached weapons (#22653) | module/item |

## Улучшения и автоматизация (38)

| commit | что даёт | область |
|---|---|---|
| `36008d0ed` | Apply minor fixes to loot sheet styling | styles/actor |
| `b1f5003cf` | Resolve injected properties in DamageAlteration predicates (#22098) | module/rules |
| `86f091171` | Propagate elite/weak updates to all troop siblings (#22107) | module/actor |
| `5f19d7fec` | Add draconic benefactors from draconic codex to dragon disciple choices (#21978) | module/migration |
| `42ea8a49d` | Avoid coercing boost to number in trait config (#22165) | module/item |
| `1d256f8ef` | Correct instances of "sf2e remaster" table classes in Journals and select NPC entries (#22227) | module/actor, scripts/config |
| `5693fc172` | Add sniper weapon crit specialization damage automatically (#22234) | module/rules |
| `8c62342ce` | Include spell attack and dc domains for special statistic spellcasting (#22281) | module/rules |
| `58d6451ba` | Restore missing radio buttons in shield block dialog (#22286) | styles/ui |
| `8d64043ea` | Set `ignored` if predicate fails in `StrikeRuleElement#beforePrepareData` (#22317) | module/rules |
| `199311a09` | Set default token ring to steel in sf2e (#22352) | scripts/hooks |
| `a9cb28709` | Hide ActorsDeadAtZero setting from players (#22355) | scripts/hooks |
| `e55435a4a` | Add RuleElement for Seugathi Guard's Magic Item Mastery feature (#22460) | scripts/config |
| `5014e1a39` | Improve Dice So Nice integration with damage types (#22456) | module/system, scripts/hooks |
| `ceb762946` | Remove padding from traits and paizo-style (#22309) | styles/_tags.scss, styles/actor |
| `513a87eb9` | Apply roll options to inline damage rolled from effect tooltips (#22508) | module/apps |
| `220b300b1` | Include origin item roll options in effects dragged from a sheet (#22514) | scripts/system |
| `830946c5e` | Improve visual accessibility of spell slot number input (#22555) | styles/actor |
| `eac9ba3aa` | Add missing Skirmish trait and skirmish actions (#22589) | scripts/config |
| `8f586ffcd` | Always use action image for unusable actions in character sheet (#22669) | module/actor |
| `127f53569` | Fill in schema definitions for `GrantItemRuleElement#onDeleteActions` and `#preselectChoices` (#22686) | module/rules |
| `6c853b4a8` | Update weapon damage die calculation for errata (#21924) | module/rules |
| `93bc5a93c` | Add Beyond the Blood Door Player's Guide content (#22735) | scripts/config |
| `669dc661d` | Add content from Impossible magic (#22769) | module/item, scripts/config |
| `3e10cb824` | Increase `SceneConfig` width | module/scene |
| `5cf893e72` | Use modifier type to find proficiency modifier in mythic rerolls (#22110) | module/system |
| `c5a25057d` | Prevent troop token flags from being saved to prototype tokens (#22167) | module/actor |
| `b6dda73a7` | Refresh token bars on Temp HP updates. (#22246) | module/scene |
| `b4f2e3d0d` | Allow "base" actor and item subtypes to construct (#22297) | module/actor, module/item |
| `333235651` | Add weapon boost automation (#22298) | module/actor, module/system |
| `5e5e5ecd8` | Include piloting/computers in RK skills list in party sheet (#22328) | module/actor |
| `d94c684bc` | Add {item|id}-{meleeOrRanged}-damage domain to attacks, to enable ammunition rules (#22332) | module/actor |
| `4494a0909` | Patch a typo in mandatoryMelee regexp (#22398) | module/item |
| `c95e08a57` | Preserve token mirror state when applying TokenImage scale override (#22414) | module/scene |
| `1e16270e7` | Apply each persistent damage from dragged formula (#22503) | module/actor |
| `b0cd9544d` | Improve trade initiation: party-sheet member drops, request expiry with alerts on both sides, prevent sending to familiars (#22520) | module/actor, module/apps |
| `74bd0afc5` | Remove manipulate trait from alchemical bomb strikes (#22621) | module/actor |
| `20a14cd71` | Snapshot area fire save dc in chat message context (#22626) | module/actor, module/chat-message |

## Отклонены компилятором (10)

Применяются текстом, но опираются на типы v14.

| commit | что это было |
|---|---|
| `b2e8e632b` | Update some deletions in feat sheet |
| `06ebbdb36` | Pass along `Scene#view` options (#21970) |
| `6ebbdef62` | Restore token effect icons (#21990) |
| `e7fac23f4` | Refactor `EncounterPF2e` to utilize core turn-event handlers (#22077) |
| `5189f2530` | Assign unique slug for each flat damage instance in NPC attacks (#22204) |
| `7e3903b68` | Fix errors deleting min and max effect badge fields (#22209) |
| `d405a2566` | Add expend tag to weapon description and strikes (#22276) |
| `96a499492` | Prevent chat bubbles if message doesn't look like in-character text (#22525) |
| `8e4dddc87` | Fix issues with transferring credits (#22588) |
| `387834a5d` | Convert `LootNPCsPopup` to DialogV2 (#22732) |
