# Changelog

All notable changes to the public API will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## Changes to be tagged

## 5.24.0 - 2020-12-14

### Added

- Added stage to raw and nice quest phase.

## 5.23.0 - 2020-12-04

### Added

- LB5.5 names and traits
- `voiceCondSvt` option for servant search. Search for servants that have voice lines for the given servant IDs or collectionNos.

## 5.22.0 - 2020-11-26

### Added

- `warId` to nice quest and nice quest phase.

### Changed

- LB3 servant and CE English names to use NA translation.

### Fixed

- Failed to import NA data. There are entries from servant to skill IDs but there's no corresponding skill ID in the master skill table.

## 5.21.0 - 2020-11-19

### Added

- Grail cost export in `NiceSvtGrailCost.json`.
- CharaGraph and Face assets for exp and fou cards.

## 5.20.0 - 2020-11-17

### Added

- raw, nice, basic `war` endpoint.
- Export `basic_event.json` and `basic_war.json`.
- `phases` to nice quest.
- List of war IDs to nice and basic event.

## 5.19.1 - 2020-11-15

### Fixed

- Banner URLs.

## 5.19.0 - 2020-11-15

### Added

- raw, nice and basic `event` endpoints.

## 5.18.1 - 2020-11-14

### Added

- Trait `curse` and `fieldShoreOrImaginarySpace`.
- New NA CE names and JP Nemo event CE English names from Fandom.

## 5.18.0 - 2020-11-07

### Added

- `charaFigureForm` to nice servant extra assets and `mstSvtScript` to raw servant for servants with multiple charaFigure forms.
- Enums from 2.22.0.
- New traits.
- New servants English names from Nemo event.
- `changeEffect` to raw ScriptJsonInfo.

## 5.17.0 - 2020-11-07

### Added

- `atkMax` and `hpMax` to basic servant and equip.

## 5.16.1 - 2020-11-07

### Fixed

- `expGrowth` array was off by one.

## 5.16.0 - 2020-11-06

### Added

- `expGrowth` and `expFeed` to nice servant and CE.

## 5.15.0 - 2020-10-13

### Added

- `illustrator` to nice command code.

## 5.14.0 - 2020-10-13

### Added

- `INDIVIDUALITIE` to nice buff script.

### Fixed

- `classrider` trait enum to `classRider`.

## 5.13.0 - 2020-10-10

### Added

- `detail` in nice item.
- Guda 5 CE name translations.

## 5.12.1 - 2020-10-09

### Added

- Translations for Guda 5 servant names. New Nobukatsu buff name.
- Enums from 2.20.0.

### Changed

- Replaced all enum|int union types from nice servant schema for enum type. There's no need for integer type now that the enums can be kept up to date.

## 5.12.0 - 2020-10-01

### Added

- `svtChange` to nice servant that contains the details about hidden names.
- `svtId` and `voicePrefix` to `NiceVoiceGroup` that will help with identifying which limit, costume, change the voice group is for.

## 5.11.0 - 2020-09-29

### Added

- `voicePrefix` to nice servant `ascensionAdd`.

## 5.10.1 - 2020-09-29

### Fixed

- Import audio delay as decimal instead of integer.

## 5.10.0 - 2020-09-28

### Added

- `/rapidoc` documentation style.

### Changed

- Made rapidoc the default documentation style.

## 5.9.1 - 2020-09-28

### Added

- Hyde voices to Jekyll servant data.
- Masu_2 voices to Mash_1 servant data

## 5.9.0 - 2020-09-28

### Added

- URLs to voice assets in nice lore.

## 5.8.0 - 2020-09-27

### Added

- CE name translations.

## 5.7.0 - 2020-09-26

### Added

- `/quest/{quest_id}` endpoint.
- Quest Release info in nice quest phase.

### Added

- `openapi_url` environment variable that will add the `url` property to `openapi.json`. This will help with external OpenAPI schema viewer to reach the API server.

## 5.6.0 - 2020-09-19

### Added

- `relateQuestIds` property in nice servant.

## 5.5.1 - 2020-09-19

### Fixed

- Failed to get JP servant data because JP doesn't have subtitle data.

## 5.5.0 - 2020-09-19

### Added

- Hidden name and deadheat race voice lines.
- New enums from 2.19.0.

## 5.4.1 - 2020-09-17

### Removed

- Nice servant `ascensionMaterials` won't return materials for `limit` of 4.

## 5.4.0 - 2020-09-11

### Added

- `buffGroup` parameter in buff search.

## 5.3.1 - 2020-09-09

### Added

- New enums from 2.18.0.
- New buff action info from 2.17.0.

### Changed

- Buff action `ATK` has limit `NORMAL`.

### Fixed

- Ascension individuality listing.

## 5.3.0 - 2020-08-27

### Added

- All enums export.
- Summer Abby English name.

### Fixed

- Reverted the removal of nice NP filtering in 5.2.0. Will filter if the nice svt entity is a servant.

## 5.2.0 - 2020-08-23

### Added

- Skill search.
- NP search.
- `flag` property in raw, nice servant data and `flag` parameter in servant search.
- `ReleaseText`, `DamageRelease`, `relationId` in buff script.

### Changed

- For nice traits, negative trait will have the corresponding positive trait as `id` and `"negative": true` property.
- `excludeCollectionNo` in servant search will take multiple values.
- Removed nice servant NP filtering. Return all NPs available in nice servant.

## 5.1.0 - 2020-08-17

### Added

- Costume materials in nice servant.

## 5.0.0 - 2020-08-17

### Changed

- Ascension in nice servant ascensionAdd.individuality and ascensionMaterials will start at 0 like DW's.
