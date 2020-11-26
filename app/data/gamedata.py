import time
from collections import defaultdict
from typing import Dict

import orjson

from ..config import Settings, logger
from .common import Region
from .enums import FUNC_VALS_NOT_BUFF, SvtType
from .schemas.raw import Master, is_equip, is_servant


settings = Settings()


masters: Dict[Region, Master] = {}
MASTER_WITH_ID = {
    "mstSvt",
    "mstBuff",
    "mstFunc",
    "mstSkill",
    "mstTreasureDevice",
    "mstItem",
    "mstEquip",
    "mstQuest",
    "mstCommandCode",
    "mstCv",
    "mstIllustrator",
    "mstVoice",
    "mstEvent",
    "mstWar",
    "mstMap",
    "mstSpot",
    "mstBgm",
}
ID_LISTS = {
    "mstSvtVoice",
    "mstClassRelationOverwrite",
    "mstQuestRelease",
    "mstCombineMaterial",
}
MASTER_WITHOUT_ID = {
    "mstSvtExp",
    "mstSvtScript",
    "mstFriendship",
    "mstEquipExp",
    "mstEquipSkill",
    "mstQuestPhase",
    "mstCommandCodeSkill",
    "mstCommandCodeComment",
    "mstSvtGroup",
    "mstClosedMessage",
    "mstConstant",
}
SVT_STUFFS = {
    "mstSvtCard",
    "mstSvtLimit",
    "mstCombineSkill",
    "mstCombineLimit",
    "mstCombineCostume",
    "mstSvtLimitAdd",
    "mstSvtComment",
    "mstSvtCostume",
    "mstSvtChange",
    "mstSvtVoiceRelation",
}
SKILL_STUFFS = {"mstSkillDetail", "mstSvtSkill", "mstSkillLv"}
TD_STUFFS = {"mstTreasureDeviceDetail", "mstSvtTreasureDevice", "mstTreasureDeviceLv"}
region_path = {Region.NA: settings.na_gamedata, Region.JP: settings.jp_gamedata}


def update_gamedata() -> None:
    logger.info("Loading game data …")
    start_loading_time = time.perf_counter()

    for region_name, gamedata in region_path.items():
        master = {}

        for entity in (
            MASTER_WITH_ID
            | MASTER_WITHOUT_ID
            | SVT_STUFFS
            | SKILL_STUFFS
            | TD_STUFFS
            | ID_LISTS
        ):
            with open(gamedata / f"{entity}.json", "rb") as fp:
                master[entity] = orjson.loads(fp.read())

        for entity in MASTER_WITH_ID:
            master[f"{entity}Id"] = {item["id"]: item for item in master[entity]}

        master["mstSvtServantCollectionNo"] = {
            item["collectionNo"]: item["id"]
            for item in master["mstSvt"]
            if is_servant(item["type"]) and item["collectionNo"] != 0
        }

        master["mstSvtEquipCollectionNo"] = {
            item["collectionNo"]: item["id"]
            for item in master["mstSvt"]
            if is_equip(item["type"]) and item["collectionNo"] != 0
        }

        master["mstFriendshipId"] = defaultdict(list)
        master["mstFriendship"] = sorted(
            master["mstFriendship"], key=lambda item: item["rank"]  # type: ignore
        )
        for item in master["mstFriendship"]:
            if item["friendship"] != -1:
                master["mstFriendshipId"][item["id"]].append(item["friendship"])

        master["mstSvtScriptId"] = defaultdict(list)
        for item in master["mstSvtScript"]:
            master["mstSvtScriptId"][item["id"] // 10].append(item)

        master["mstQuestPhaseId"] = defaultdict(dict)
        for item in master["mstQuestPhase"]:
            master["mstQuestPhaseId"][item["questId"]][item["phase"]] = item

        master["buffToFunc"] = defaultdict(set)
        for item in master["mstFunc"]:
            if item["funcType"] not in FUNC_VALS_NOT_BUFF:
                for buff_id in item["vals"]:
                    master["buffToFunc"][buff_id].add(item["id"])

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
            for item in master[func_reverse_stuff]:
                for func_id in item["funcId"]:
                    if item[result_id] in master[func_reverse_check]:
                        master[masters_table][func_id].add(item[result_id])

        master["passiveSkillToSvt"] = defaultdict(set)
        for item in master["mstSvt"]:
            for skill_id in item["classPassive"]:
                master["passiveSkillToSvt"][skill_id].add(item["id"])

        for masters_table, source_table, lookup_id, result_id in (
            ("mstClosedMessageId", "mstClosedMessage", "id", "message"),
            ("mstConstantId", "mstConstant", "name", "value"),
        ):
            master[masters_table] = {
                item[lookup_id]: item[result_id] for item in master[source_table]
            }

        master["mstSvtExp"] = sorted(master["mstSvtExp"], key=lambda item: item["lv"])  # type: ignore
        master["mstCombineMaterial"] = sorted(master["mstCombineMaterial"], key=lambda item: item["lv"])  # type: ignore

        for masters_table, source_table, lookup_id in (
            ("mstClassRelationOverwriteId", "mstClassRelationOverwrite", "id"),
            ("mstCombineCostumeId", "mstCombineCostume", "svtId"),
            ("mstCombineLimitId", "mstCombineLimit", "id"),
            ("mstCombineMaterialId", "mstCombineMaterial", "id"),
            ("mstCombineSkillId", "mstCombineSkill", "id"),
            ("mstQuestReleaseId", "mstQuestRelease", "questId"),
            ("mstSkillDetailId", "mstSkillDetail", "id"),
            ("mstSkillLvId", "mstSkillLv", "skillId"),
            ("mstSvtCardId", "mstSvtCard", "svtId"),
            ("mstSvtChangeId", "mstSvtChange", "svtId"),
            ("mstSvtCommentId", "mstSvtComment", "svtId"),
            ("mstSvtCostumeId", "mstSvtCostume", "svtId"),
            ("mstSvtExpId", "mstSvtExp", "type"),
            ("mstSvtGroupId", "mstSvtGroup", "id"),
            ("mstSvtLimitId", "mstSvtLimit", "svtId"),
            ("mstSvtLimitAddId", "mstSvtLimitAdd", "svtId"),
            ("mstSvtSkillId", "mstSvtSkill", "skillId"),
            ("mstSvtSkillSvtId", "mstSvtSkill", "svtId"),
            ("mstSvtTreasureDeviceId", "mstSvtTreasureDevice", "treasureDeviceId"),
            ("mstSvtTreasureDeviceSvtId", "mstSvtTreasureDevice", "svtId"),
            ("mstSvtVoiceId", "mstSvtVoice", "id"),
            ("mstSvtVoiceRelationId", "mstSvtVoiceRelation", "svtId"),
            ("mstTreasureDeviceDetailId", "mstTreasureDeviceDetail", "id"),
            ("mstTreasureDeviceLvId", "mstTreasureDeviceLv", "treaureDeviceId"),
            ("mstMapWarId", "mstMap", "warId"),
            ("mstSpotWarId", "mstSpot", "warId"),
            ("mstQuestSpotId", "mstQuest", "spotId"),
            ("mstWarEventId", "mstWar", "eventId"),
        ):
            master[masters_table] = defaultdict(list)
            for item in master[source_table]:
                master[masters_table][item[lookup_id]].append(item)

        master["bondEquip"] = {}
        for item in master["mstSvt"]:
            if (
                item["type"] == SvtType.SERVANT_EQUIP
                and item["id"] in master["mstSvtSkillSvtId"]
            ):
                actIndividualities = set()
                for skill in master["mstSvtSkillSvtId"][item["id"]]:
                    mstSkill = master["mstSkillId"].get(skill["skillId"])
                    if mstSkill:
                        actIndividualities.add(tuple(mstSkill["actIndividuality"]))
                if len(actIndividualities) == 1:
                    individualities = actIndividualities.pop()
                    if (
                        len(individualities) == 1
                        and individualities[0] in master["mstSvtId"]
                    ):
                        master["bondEquip"][individualities[0]] = item["id"]

        if region_name == Region.NA:
            with open(gamedata / "globalNewMstSubtitle.json", "rb") as fp:
                globalNewMstSubtitle = orjson.loads(fp.read())
            master["mstSubtitleId"] = defaultdict(list)
            for item in globalNewMstSubtitle:
                svt = item["id"].split("_")[0]
                if not svt.startswith("PLAIN"):
                    master["mstSubtitleId"][int(svt)].append(item)

        masters[region_name] = Master.parse_obj(master)

    data_loading_time = time.perf_counter() - start_loading_time
    logger.info(f"Loaded game data in {data_loading_time:.2f}s.")


update_gamedata()
