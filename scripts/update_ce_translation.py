import argparse
import json
import os
from enum import IntEnum
from pathlib import Path
from typing import Any, Callable


MAPPING_PATH = Path(__file__).resolve().parents[1] / "app" / "data" / "mappings"
TRANSLATIONS: dict[str, str] = {}
ENTITY_TRANSLATIONS: dict[str, str] = {}
TRANSLATION_FILES = (
    "skill_names",
    "np_names",
    "event_names",
    "war_names",
    "entity_names",
    "servant_names",
    "equip_names",
    "cc_names",
    "mc_names",
)
DONT_USE_NA_TRANSLATION = {
    "1000万DL突破キャンペーン",
    "「1300万DL突破キャンペーン」開催記念",
    "1500万DL突破キャンペーン",
    "1800万DL突破キャンペーン",
}


class SvtType(IntEnum):
    NORMAL = 1
    HEROINE = 2
    COMBINE_MATERIAL = 3
    ENEMY = 4
    ENEMY_COLLECTION = 5
    SERVANT_EQUIP = 6
    STATUS_UP = 7
    SVT_EQUIP_MATERIAL = 8
    ENEMY_COLLECTION_DETAIL = 9
    ALL = 10
    COMMAND_CODE = 11


for translation_file in TRANSLATION_FILES:
    translation_path = MAPPING_PATH / f"{translation_file}.json"
    if translation_path.exists():
        with open(translation_path, "r", encoding="utf-8") as translation_fp:
            translation_data = json.load(translation_fp)
            TRANSLATIONS |= translation_data
            if translation_file == "servant_names":
                ENTITY_TRANSLATIONS |= translation_data


def is_servant(svt: Any) -> bool:
    return bool(
        svt["type"]
        in {SvtType.NORMAL, SvtType.HEROINE, SvtType.ENEMY_COLLECTION_DETAIL}
        and svt["collectionNo"] != 0
    )


def is_ce(svt: Any) -> bool:
    return bool(svt["type"] == SvtType.SERVANT_EQUIP and svt["collectionNo"] != 0)


def get_ce_names(mstSvt: Any) -> dict[int, str]:
    ce_names: dict[int, str] = {
        svt["collectionNo"]: svt["name"] for svt in mstSvt if is_ce(svt)
    }
    return ce_names


def get_cc_names(mstCommandCode: Any) -> dict[int, str]:
    cc_names: dict[int, str] = {
        svt["collectionNo"]: svt["name"] for svt in mstCommandCode
    }
    return cc_names


def get_names(mstEquip: Any) -> dict[int, str]:
    mc_names: dict[int, str] = {svt["id"]: svt["name"] for svt in mstEquip}
    return mc_names


def get_war_names(mstEquip: Any) -> dict[int, str]:
    mc_names: dict[int, str] = {svt["id"]: svt["longName"] for svt in mstEquip}
    return mc_names


def is_not_svt_or_ce(svt: Any) -> bool:
    return not is_servant(svt) and not is_ce(svt)


def get_entity_names(mstSvt: Any) -> dict[int, str]:
    entity_names: dict[int, str] = {
        svt["id"]: svt["name"] for svt in mstSvt if is_not_svt_or_ce(svt)
    }
    return entity_names


def update_translation(
    mapping: str,
    jp_master: Path,
    na_master: Path,
    master_file: str,
    extract_names: Callable[[Any], dict[int, str]],
) -> None:
    with open(jp_master / f"{master_file}.json", "r", encoding="utf-8") as fp:
        jp_svt = json.load(fp)
    with open(na_master / f"{master_file}.json", "r", encoding="utf-8") as fp:
        na_svt = json.load(fp)

    mapping_path = MAPPING_PATH / f"{mapping}.json"
    if mapping_path.exists():
        with open(mapping_path, "r", encoding="utf-8") as fp:
            current_translations: dict[str, str] = json.load(fp)
    else:
        current_translations = {}

    na_names = extract_names(na_svt)
    jp_names = extract_names(jp_svt)

    if master_file == "mstWar":
        with open(na_master / "mstConstant.json", "r", encoding="utf-8") as fp:
            na_constant = {
                constant["name"]: constant["value"] for constant in json.load(fp)
            }

        last_war_id = na_constant["LAST_WAR_ID"]
        na_names.pop(last_war_id + 1)

    updated_translation: dict[str, str] = {}
    for colNo, jp_name in sorted(jp_names.items(), key=lambda x: x[0]):
        if jp_name in ENTITY_TRANSLATIONS and mapping == "entity_names":
            continue
        if colNo in na_names and jp_name not in DONT_USE_NA_TRANSLATION:
            updated_translation[jp_name] = na_names[colNo]
        elif jp_name not in updated_translation:
            updated_translation[jp_name] = current_translations.get(
                jp_name, TRANSLATIONS.get(jp_name, jp_name)
            )

    with open(mapping_path, "w", encoding="utf-8", newline="\n") as fp:
        json.dump(updated_translation, fp, indent=2, ensure_ascii=False)
        fp.write("\n")


def main(jp_master: Path, na_master: Path) -> None:
    update_translation("equip_names", jp_master, na_master, "mstSvt", get_ce_names)
    update_translation("cc_names", jp_master, na_master, "mstCommandCode", get_cc_names)
    update_translation("mc_names", jp_master, na_master, "mstEquip", get_names)
    update_translation("skill_names", jp_master, na_master, "mstSkill", get_names)
    update_translation("np_names", jp_master, na_master, "mstTreasureDevice", get_names)
    update_translation("event_names", jp_master, na_master, "mstEvent", get_names)
    update_translation("war_names", jp_master, na_master, "mstWar", get_war_names)
    update_translation("item_names", jp_master, na_master, "mstItem", get_names)
    update_translation("entity_names", jp_master, na_master, "mstSvt", get_entity_names)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update CE name translation file with NA translations."
    )
    parser.add_argument(
        "--jp-master",
        type=str,
        help="Path to the JP master folder. Not needed if environment variable JP_GAMEDATA is set.",
        default=None,
    )
    parser.add_argument(
        "--na-master",
        type=str,
        help="Path to the NA master folder. Not needed if environment variable NA_GAMEDATA is set.",
        default=None,
    )

    args = parser.parse_args()
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        print("Can't find dotenv package.")

    if args.jp_master:
        jp_path = Path(args.jp_master).resolve()
    elif os.getenv("JP_GAMEDATA"):
        jp_path = Path(str(os.getenv("JP_GAMEDATA"))).resolve() / "master"
    else:
        raise KeyError("JP_GAMEDATA not found")

    if args.na_master:
        na_path = Path(args.na_master).resolve()
    elif os.getenv("NA_GAMEDATA"):
        na_path = Path(str(os.getenv("NA_GAMEDATA"))).resolve() / "master"
    else:
        raise KeyError("NA_GAMEDATA not found")

    main(jp_path, na_path)
