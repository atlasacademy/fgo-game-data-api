import time
from collections import defaultdict

import orjson
from pydantic import DirectoryPath

from ..config import Settings, logger
from ..schemas.common import Region
from ..schemas.enums import FUNC_VALS_NOT_BUFF
from ..schemas.raw import BAD_COMBINE_SVT_LIMIT, Master


settings = Settings()


masters: dict[Region, Master] = {}
MASTER_WITH_ID = {
    "mstSvt",
    "mstFunc",
    "mstSkill",
    "mstTreasureDevice",
}
MASTER_WITHOUT_ID = {
    "mstEquipSkill",
    "mstCommandCodeSkill",
    "mstStage",
    "mstAi",
    "mstAiField",
    "mstAiAct",
    "mstSvtPassiveSkill",
}
SVT_STUFFS = {
    "mstCombineSkill",
    "mstCombineLimit",
    "mstCombineCostume",
}
SKILL_STUFFS = {"mstSvtSkill", "mstSkillLv"}
TD_STUFFS = {"mstSvtTreasureDevice", "mstTreasureDeviceLv"}


def update_masters(region_path: dict[Region, DirectoryPath]) -> None:
    logger.info("Loading game data …")
    start_loading_time = time.perf_counter()

    for region_name, gamedata in region_path.items():
        master = {}

        for entity in (
            MASTER_WITH_ID | MASTER_WITHOUT_ID | SVT_STUFFS | SKILL_STUFFS | TD_STUFFS
        ):
            with open(gamedata / "master" / f"{entity}.json", "rb") as fp:
                master[entity] = orjson.loads(fp.read())

        for entity in MASTER_WITH_ID:
            master[f"{entity}Id"] = {item["id"]: item for item in master[entity]}

        master["buffToFunc"] = defaultdict(set)
        for func in master["mstFunc"]:
            if func["funcType"] not in FUNC_VALS_NOT_BUFF:
                for buff_id in func["vals"]:
                    master["buffToFunc"][buff_id].add(func["id"])

        for masters_table, func_reverse_stuff, func_reverse_check, result_id in (
            ("funcToSkill", "mstSkillLv", "mstSkillId", "skillId"),
            (
                "funcToTd",
                "mstTreasureDeviceLv",
                "mstTreasureDeviceId",
                "treaureDeviceId",
            ),
        ):
            master[masters_table] = defaultdict(set)
            for skill_td_lv in master[func_reverse_stuff]:
                for func_id in skill_td_lv["funcId"]:
                    if skill_td_lv[result_id] in master[func_reverse_check]:
                        master[masters_table][func_id].add(skill_td_lv[result_id])

        master["passiveSkillToSvt"] = defaultdict(set)
        for svt in master["mstSvt"]:
            for skill_id in svt["classPassive"]:
                master["passiveSkillToSvt"][skill_id].add(svt["id"])

        master["extraPassiveSkillToSvt"] = defaultdict(set)
        for skill in master["mstSvtPassiveSkill"]:
            master["extraPassiveSkillToSvt"][skill["skillId"]].add(skill["svtId"])

        for masters_table, source_table, lookup_id, result_id in (
            ("activeSkillToSvt", "mstSvtSkill", "skillId", "svtId"),
            ("tdToSvt", "mstSvtTreasureDevice", "treasureDeviceId", "svtId"),
            ("aiActToAiSvt", "mstAi", "aiActId", "id"),
            ("aiActToAiField", "mstAiField", "aiActId", "id"),
        ):
            master[masters_table] = defaultdict(set)
            for item in master[source_table]:
                master[masters_table][item[lookup_id]].add(item[result_id])

        for mstCombine in ("mstCombineSkill", "mstCombineLimit", "mstCombineCostume"):
            master[f"{mstCombine}Item"] = {
                item_id
                for combine in master[mstCombine]
                for item_id in combine["itemIds"]
                if mstCombine != "mstCombineLimit"
                or combine["svtLimit"] != BAD_COMBINE_SVT_LIMIT
            }

        for masters_table, ai_table in (
            ("parentAiSvt", "mstAi"),
            ("parentAiField", "mstAiField"),
        ):
            master[masters_table] = defaultdict(set)
            for ai in master[ai_table]:
                if ai["avals"][0] != 0:
                    master[masters_table][ai["avals"][0]].add(ai["id"])

        master["skillToAiAct"] = defaultdict(set)
        for ai_act in master["mstAiAct"]:
            if len(ai_act["skillVals"]) >= 2:
                master["skillToAiAct"][ai_act["skillVals"][0]].add(ai_act["id"])

        masters[region_name] = Master.parse_obj(master)

    data_loading_time = time.perf_counter() - start_loading_time
    logger.info(f"Loaded game data in {data_loading_time:.2f}s.")
