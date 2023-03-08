import argparse
import json
import os
import re
from difflib import ndiff
from enum import IntEnum
from pathlib import Path
from typing import Any, Callable, Union


MAPPING_PATH = Path(__file__).resolve().parents[1] / "app" / "data" / "mappings"
CONFIG_JSON_PATH = Path(__file__).resolve().parents[1] / "config.json"
TRANSLATIONS: dict[str, str] = {}
ENTITY_TRANSLATIONS: dict[str, str] = {}
TRANSLATION_FILES = (
    "voice_names",
    "overwrite_voice_names",
    "bgm_names",
    "skill_names",
    "np_names",
    "event_names",
    "war_names",
    "entity_names",
    "quest_names",
    "spot_names",
    "illustrator_names",
    "cv_names",
    "servant_names",
    "equip_names",
    "cc_names",
    "mc_names",
    "costume_names",
)
LOGIN_ITEM_REGEX = re.compile(r"(\d+)月交換券\((\d+)\)")
VOICE_NAME_REGEX = re.compile(r"^(.*?)(\d+)$", re.DOTALL)
NEW_YEAR_LINE_REGEX = re.compile(r"^謹賀新年(.*)$")
MASTER_MISSION_REGEX = re.compile(r"^マスターミッション\s(\d+)年(\d+)月 ")
ENGLISH_MONTHS = {
    1: "JAN",
    2: "FEB",
    3: "MAR",
    4: "APR",
    5: "MAY",
    6: "JUN",
    7: "JUL",
    8: "AUG",
    9: "SEP",
    10: "OCT",
    11: "NOV",
    12: "DEC",
}
overwrite_na_path = MAPPING_PATH / "overwrite_na_translations.json"
if overwrite_na_path.exists():
    with open(overwrite_na_path, "r", encoding="utf-8") as overwrote_fp:
        DONT_USE_NA_TRANSLATION = set(json.load(overwrote_fp))
else:
    DONT_USE_NA_TRANSLATION = set()


def strip_space(translations: dict[Any, str]) -> dict[Any, str]:
    return {k: v.strip() for k, v in translations.items()}


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


def update_enemy_translation() -> None:
    translations: dict[str, str] = {}
    for translation_f in TRANSLATION_FILES:
        translation_p = MAPPING_PATH / f"{translation_f}.json"
        if translation_p.exists():
            with open(translation_p, "r", encoding="utf-8") as fp:
                translations |= json.load(fp)

    with open(MAPPING_PATH / "enemy_names.json", "r", encoding="utf-8") as fp:
        enemies = json.load(fp)

    translated = {k: translations.get(k, v) for k, v in enemies.items()}

    with open(
        MAPPING_PATH / "enemy_names.json", "w", encoding="utf-8", newline="\n"
    ) as fp:
        json.dump(strip_space(translated), fp, indent=2, ensure_ascii=False)
        fp.write("\n")


def is_servant(svt: Any) -> bool:
    return bool(
        svt["type"]
        in {SvtType.NORMAL, SvtType.HEROINE, SvtType.ENEMY_COLLECTION_DETAIL}
        and svt["collectionNo"] != 0
    )


def get_servant_names(mstSvt: Any) -> dict[tuple[int, int, int], str]:
    names = {}

    for svt in mstSvt:
        if is_servant(svt):
            names[(svt["collectionNo"], -1, -1)] = svt["name"]
            names[(svt["collectionNo"], -1, 1)] = svt["battleName"]

    return names


def update_servant_translation(jp_master: Path, na_master: Path) -> None:
    with open(jp_master / "mstSvt.json", "r", encoding="utf-8") as fp:
        jp_svt = json.load(fp)
    with open(na_master / "mstSvt.json", "r", encoding="utf-8") as fp:
        na_svt = json.load(fp)

    col_nos = {
        svt["id"]: svt["collectionNo"]
        for svt in jp_svt
        if svt["type"]
        in {
            SvtType.NORMAL,
            SvtType.HEROINE,
            SvtType.ENEMY_COLLECTION_DETAIL,
        }
        and svt["collectionNo"] != 0
    }

    mapping_path = MAPPING_PATH / "servant_names.json"
    if mapping_path.exists():
        with open(mapping_path, "r", encoding="utf-8") as fp:
            current_translations: dict[str, str] = json.load(fp)
    else:
        current_translations = {}

    jp_names = get_servant_names(jp_svt)
    na_names = get_servant_names(na_svt)

    with open(jp_master / "mstSvtLimitAdd.json", "r", encoding="utf-8") as fp:
        jp_limit_add = json.load(fp)
    with open(na_master / "mstSvtLimitAdd.json", "r", encoding="utf-8") as fp:
        na_limit_add = json.load(fp)

    for limit_add, names_dict in [[jp_limit_add, jp_names], [na_limit_add, na_names]]:
        for limit in limit_add:
            if limit["svtId"] in col_nos:
                limit_id = (col_nos[limit["svtId"]], limit["limitCount"], 0)
                if "overWriteServantName" in limit["script"]:
                    names_dict[limit_id] = limit["script"]["overWriteServantName"]
                if "overWriteServantBattleName" in limit["script"]:
                    names_dict[
                        (col_nos[limit["svtId"]], limit["limitCount"], 1)
                    ] = limit["script"]["overWriteServantBattleName"]

    updated_translation = {}
    for jp_key in sorted(jp_names.keys()):
        jp_name = jp_names[jp_key]
        current_translation = current_translations.get(jp_name)
        na_translation = na_names.get(jp_key)

        if current_translation is not None:
            new_translation = current_translation
        elif na_translation is not None:
            new_translation = na_translation
        else:
            new_translation = jp_name

        if (
            current_translation is not None
            and na_translation is not None
            and current_translation != na_translation
        ):
            diff = "".join(
                li.removeprefix("+ ")
                for li in ndiff(current_translation, na_translation)
                if li[0] == "+"
            ).strip()

            if not (
                (diff.startswith("(") and diff.endswith(")"))  # (class name)
                or (
                    diff.startswith("(")
                    and current_translation.endswith(")")
                    and not diff.endswith(")")  # (class name
                )
            ):
                print(
                    f"Different translation: {jp_name} to Current: {current_translation} vs NA: {na_translation}"
                )

        updated_translation[jp_name] = new_translation

    with open(mapping_path, "w", encoding="utf-8", newline="\n") as fp:
        json.dump(strip_space(updated_translation), fp, indent=2, ensure_ascii=False)
        fp.write("\n")


def is_ce(svt: Any) -> bool:
    return bool(svt["type"] == SvtType.SERVANT_EQUIP and svt["collectionNo"] != 0)


def get_ce_names(mstSvt: Any) -> dict[int, str]:
    return {svt["collectionNo"]: svt["name"] for svt in mstSvt if is_ce(svt)}


def get_cc_names(mstCommandCode: Any) -> dict[int, str]:
    return {svt["collectionNo"]: svt["name"] for svt in mstCommandCode}


def get_names(mstEquip: Any) -> dict[int, str]:
    return {svt["id"]: svt["name"] for svt in mstEquip}


def get_np_names(mstTreasureDevice: Any) -> dict[int, str]:
    return {
        td["id"]: td["ruby"] if td["ruby"] not in ("", "-") else td["name"]
        for td in mstTreasureDevice
    }


def get_war_names(mstWar: Any) -> dict[int, str]:
    return {svt["id"]: svt["longName"] for svt in mstWar}


def is_not_svt_or_ce(svt: Any) -> bool:
    return not is_servant(svt) and not is_ce(svt)


def get_entity_names(mstSvt: Any) -> dict[int, str]:
    return {svt["id"]: svt["name"] for svt in mstSvt if is_not_svt_or_ce(svt)}


def get_voice_names(mstVoice: Any) -> dict[str, str]:
    out_dict = {}
    for voice in mstVoice:
        if match := VOICE_NAME_REGEX.match(voice["name"]):
            out_dict[voice["id"]] = match.group(1)
        else:
            out_dict[voice["id"]] = voice["name"]
    return out_dict


def get_svt_voice_names(mstSvtVoice: Any) -> dict[str, str]:
    out_dict = {}
    for voice in mstSvtVoice:
        for script in voice["scriptJson"]:
            first_script_id = script["infos"][0]["id"]
            script_id = f'{voice["id"]}_{voice["voicePrefix"]}_{voice["type"]}_{first_script_id}'
            overwriteName = (
                script["overwriteName"] if script["overwriteName"] is not None else ""
            )
            if match := VOICE_NAME_REGEX.match(overwriteName):
                out_dict[script_id] = match.group(1)
            else:
                out_dict[script_id] = overwriteName
    return out_dict


def get_costume_names(mstCostume: Any) -> dict[str, str]:
    return {
        str(costume["svtId"]) + "-" + str(costume["id"]): costume["shortName"]
        for costume in mstCostume
    }


def update_translation(
    mapping: str,
    jp_master: Path,
    na_master: Path,
    master_file: str,
    extract_names: Union[
        Callable[[Any], dict[int, str]], Callable[[Any], dict[str, str]]
    ],
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

        last_war_id = na_constant["LAST_WAR_ID"] + 1
        if last_war_id in na_names:
            na_names.pop(last_war_id)

    if master_file == "mstTreasureDevice":
        na_names = get_names(na_svt)
        with open(na_master / "mstSvtLimitAdd.json", "r", encoding="utf-8") as fp:
            for limit_add in json.load(fp):
                if "overWriteTDName" in limit_add["script"]:
                    td_id = limit_add["svtId"] * 100 + limit_add["limitCount"]
                    na_names[td_id] = limit_add["script"]["overWriteTDName"]
        with open(jp_master / "mstSvtLimitAdd.json", "r", encoding="utf-8") as fp:
            for limit_add in json.load(fp):
                if "overWriteTDName" in limit_add["script"]:
                    td_name = limit_add["script"]["overWriteTDName"]
                    td_id = limit_add["svtId"] * 100 + limit_add["limitCount"]
                    jp_names[td_id] = limit_add["script"].get(
                        "overWriteTDRuby", td_name
                    )

    if master_file == "mstSkill":
        with open(jp_master / "mstSkillAdd.json", "r", encoding="utf-8") as fp:
            for skill_add in json.load(fp):
                skill_id = skill_add["skillId"] * 10 + skill_add["priority"]
                jp_names[skill_id] = skill_add["name"]

    updated_translation: dict[str, str] = {}
    for colNo, jp_name in sorted(jp_names.items(), key=lambda x: x[0]):
        if jp_name == "":
            continue

        if jp_name in ENTITY_TRANSLATIONS and mapping == "entity_names":
            continue

        if mapping == "item_names" and (match := LOGIN_ITEM_REGEX.match(jp_name)):
            month, year = match.groups()
            na_name = f"Exchange Ticket ({ENGLISH_MONTHS[int(month)]} {year})"
            updated_translation[jp_name] = na_name
            continue

        if mapping == "voice_names":
            if ny_match := NEW_YEAR_LINE_REGEX.match(jp_name):
                year = ny_match.group(1)
                na_name = f"Happy New Year {year}"
                updated_translation[jp_name] = na_name
                continue

        if mapping == "overwrite_voice_names":
            if mm_match := MASTER_MISSION_REGEX.match(jp_name):
                year, month = mm_match.groups()
                na_name = f"Master Mission, {ENGLISH_MONTHS[int(month)]} {year} "
                updated_translation[jp_name] = na_name
                continue

        if colNo in na_names and na_names[colNo] != "" and jp_name not in DONT_USE_NA_TRANSLATION:  # type: ignore
            updated_translation[jp_name] = na_names[colNo]  # type: ignore
        elif jp_name not in updated_translation:
            updated_translation[jp_name] = current_translations.get(
                jp_name, TRANSLATIONS.get(jp_name, jp_name)
            )

    if master_file == "mstSkill":
        with open(MAPPING_PATH / "skill_names.json", "r", encoding="utf-8") as fp:
            updated_translation = json.load(fp) | updated_translation

    with open(mapping_path, "w", encoding="utf-8", newline="\n") as fp:
        json.dump(strip_space(updated_translation), fp, indent=2, ensure_ascii=False)
        fp.write("\n")


def main(jp_master: Path, na_master: Path) -> None:
    update_servant_translation(jp_master, na_master)
    update_translation("equip_names", jp_master, na_master, "mstSvt", get_ce_names)
    update_translation("cc_names", jp_master, na_master, "mstCommandCode", get_cc_names)
    update_translation("mc_names", jp_master, na_master, "mstEquip", get_names)
    update_translation("skill_names", jp_master, na_master, "mstSkill", get_names)
    update_translation(
        "np_names", jp_master, na_master, "mstTreasureDevice", get_np_names
    )
    update_translation("event_names", jp_master, na_master, "mstEvent", get_names)
    update_translation("war_names", jp_master, na_master, "mstWar", get_war_names)
    update_translation("war_short_names", jp_master, na_master, "mstWar", get_names)
    update_translation("item_names", jp_master, na_master, "mstItem", get_names)
    update_translation("entity_names", jp_master, na_master, "mstSvt", get_entity_names)
    update_translation("bgm_names", jp_master, na_master, "mstBgm", get_names)
    update_translation("voice_names", jp_master, na_master, "mstVoice", get_voice_names)
    update_translation("quest_names", jp_master, na_master, "mstQuest", get_names)
    update_translation("spot_names", jp_master, na_master, "mstSpot", get_names)
    update_translation(
        "illustrator_names", jp_master, na_master, "mstIllustrator", get_names
    )
    update_translation(
        "costume_names", jp_master, na_master, "mstSvtCostume", get_costume_names
    )
    update_translation("cv_names", jp_master, na_master, "mstCv", get_names)
    update_translation(
        "overwrite_voice_names",
        jp_master,
        na_master,
        "mstSvtVoice",
        get_svt_voice_names,
    )
    update_enemy_translation()


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

    if CONFIG_JSON_PATH.exists():
        config = json.load(CONFIG_JSON_PATH.open("r", encoding="utf-8"))
    else:
        config = {}

    if data_env := os.getenv("DATA"):
        data = json.loads(data_env)
    else:
        data = {}

    if args.jp_master:
        jp_path = Path(args.jp_master).resolve()
    elif "data" in config and "JP" in config["data"]:
        jp_path = Path(config["data"]["JP"]["gamedata"]).resolve() / "master"
    elif "JP" in data:
        jp_path = Path(data["JP"]["gamedata"]).resolve() / "master"
    else:
        raise KeyError("JP_GAMEDATA not found")

    if args.na_master:
        na_path = Path(args.na_master).resolve()
    elif "data" in config and "NA" in config["data"]:
        na_path = Path(config["data"]["NA"]["gamedata"]).resolve() / "master"
    elif "NA" in data:
        na_path = Path(data["NA"]["gamedata"]).resolve() / "master"
    else:
        raise KeyError("NA_GAMEDATA not found")

    main(jp_path, na_path)
