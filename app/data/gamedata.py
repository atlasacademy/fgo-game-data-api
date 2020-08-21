import time
from typing import Any, Dict, List

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
}
ID_LISTS = {"mstSvtVoice", "mstClassRelationOverwrite"}
MASTER_WITHOUT_ID = {
    "mstSvtExp",
    "mstFriendship",
    "mstEquipExp",
    "mstEquipSkill",
    "mstQuestPhase",
    "mstCommandCodeSkill",
    "mstCommandCodeComment",
    "mstSvtGroup",
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

        # master["mstSvtServantName"] = {
        #     item["name"]: item["id"]
        #     for item in master["mstSvt"]
        #     if is_servant(item["type"]) and item["collectionNo"] != 0
        # }

        master["mstSvtEquipCollectionNo"] = {
            item["collectionNo"]: item["id"]
            for item in master["mstSvt"]
            if is_equip(item["type"]) and item["collectionNo"] != 0
        }

        mstSvtExpId: Dict[int, List[int]] = {}
        master["mstSvtExp"] = sorted(master["mstSvtExp"], key=lambda item: item["lv"])
        for item in master["mstSvtExp"]:
            if item["type"] in mstSvtExpId:
                mstSvtExpId[item["type"]].append(item["curve"])
            else:
                mstSvtExpId[item["type"]] = [item["curve"]]
        master["mstSvtExpId"] = mstSvtExpId

        mstFriendshipId: Dict[int, List[int]] = {}
        master["mstFriendship"] = sorted(
            master["mstFriendship"], key=lambda item: item["rank"]
        )
        for item in master["mstFriendship"]:
            if item["friendship"] != -1:
                if item["id"] in mstFriendshipId:
                    mstFriendshipId[item["id"]].append(item["friendship"])
                else:
                    mstFriendshipId[item["id"]] = [item["friendship"]]
        master["mstFriendshipId"] = mstFriendshipId

        mstQuestPhaseId: Dict[int, Dict[int, Any]] = {}
        for item in master["mstQuestPhase"]:
            if item["questId"] in mstQuestPhaseId:
                mstQuestPhaseId[item["questId"]][item["phase"]] = item
            else:
                mstQuestPhaseId[item["questId"]] = {item["phase"]: item}
        master["mstQuestPhaseId"] = mstQuestPhaseId

        master["buffToFunc"] = {}
        for item in master["mstFunc"]:
            if item["funcType"] not in FUNC_VALS_NOT_BUFF:
                for buff_id in item["vals"]:
                    if buff_id in master["buffToFunc"]:
                        master["buffToFunc"][buff_id].add(item["id"])
                    else:
                        master["buffToFunc"][buff_id] = {item["id"]}

        for masters_item, func_reverse_stuff, func_reverse_check, lookup_id in (
            ("funcToSkill", "mstSkillLv", "mstSkillId", "skillId"),
            (
                "funcToTd",
                "mstTreasureDeviceLv",
                "mstTreasureDeviceId",
                "treaureDeviceId",
            ),
        ):
            master[masters_item] = {}
            for item in master[func_reverse_stuff]:
                for func_id in item["funcId"]:
                    if item[lookup_id] in master[func_reverse_check]:
                        if func_id in master[masters_item]:
                            master[masters_item][func_id].add(item[lookup_id])
                        else:
                            master[masters_item][func_id] = {item[lookup_id]}

        master["passiveSkillToSvt"] = {}
        for item in master["mstSvt"]:
            for skill_id in item["classPassive"]:
                if skill_id in master["passiveSkillToSvt"]:
                    master["passiveSkillToSvt"][skill_id].add(item["id"])
                else:
                    master["passiveSkillToSvt"][skill_id] = {item["id"]}

        for svt_extra_stuff, lookup_id in (
            ("mstSvtSkill", "skillId"),
            ("mstSvtTreasureDevice", "treasureDeviceId"),
        ):
            masters_item = f"{svt_extra_stuff}SvtId"
            master[masters_item] = {}
            for item in master[svt_extra_stuff]:
                id_name = "svtId"
                if item["svtId"] in master[masters_item]:
                    master[masters_item][item[id_name]].append(item[lookup_id])
                else:
                    master[masters_item][item[id_name]] = [item[lookup_id]]

        mstSvtGroupId: Dict[int, List[int]] = {}
        for item in master["mstSvtGroup"]:
            groupId = item["id"]
            if groupId in mstSvtGroupId:
                mstSvtGroupId[groupId].append(item["svtId"])
            else:
                mstSvtGroupId[groupId] = [item["svtId"]]
        master["mstSvtGroupId"] = mstSvtGroupId

        for extra_stuff in SKILL_STUFFS | TD_STUFFS | SVT_STUFFS | ID_LISTS:
            masters_item = f"{extra_stuff}Id"
            master[masters_item] = {}
            for item in master[extra_stuff]:
                if (
                    "Detail" in extra_stuff
                    or extra_stuff in {"mstCombineSkill", "mstCombineLimit"} | ID_LISTS
                ):
                    id_name = "id"
                elif extra_stuff in SKILL_STUFFS:
                    id_name = "skillId"
                elif extra_stuff in SVT_STUFFS:
                    id_name = "svtId"
                elif extra_stuff == "mstTreasureDeviceLv":
                    id_name = "treaureDeviceId"
                elif extra_stuff == "mstSvtTreasureDevice":
                    id_name = "treasureDeviceId"
                else:  # pragma: no cover
                    raise ValueError("Can't set id_name")
                if item[id_name] in master[masters_item]:
                    master[masters_item][item[id_name]].append(item)
                else:
                    master[masters_item][item[id_name]] = [item]

        bondEquip = {}
        for item in master["mstSvt"]:
            if (
                item["type"] == SvtType.SERVANT_EQUIP
                and item["id"] in master["mstSvtSkillSvtId"]
            ):
                actIndividualities = set()
                for skill_id in master["mstSvtSkillSvtId"][item["id"]]:
                    mstSkill = master["mstSkillId"][skill_id]
                    actIndividualities.add(tuple(mstSkill["actIndividuality"]))
                if len(actIndividualities) == 1:
                    individualities = actIndividualities.pop()
                    if (
                        len(individualities) == 1
                        and individualities[0] in master["mstSvtId"]
                    ):
                        bondEquip[individualities[0]] = item["id"]

        master["bondEquip"] = bondEquip

        if region_name == Region.NA:
            with open(gamedata / "globalNewMstSubtitle.json", "rb") as fp:
                globalNewMstSubtitle = orjson.loads(fp.read())
            mstSubtitleId: Dict[int, Any] = {}
            for item in globalNewMstSubtitle:
                svt = item["id"].split("_")[0]
                if not svt.startswith("PLAIN"):
                    svtId = int(svt)
                    if svtId in mstSubtitleId:
                        mstSubtitleId[svtId].append(item)
                    else:
                        mstSubtitleId[svtId] = [item]

            master["mstSubtitleId"] = mstSubtitleId

        masters[region_name] = Master.parse_obj(master)

    data_loading_time = time.perf_counter() - start_loading_time
    logger.info(f"Loaded the game data in {data_loading_time:.4f}s.")


update_gamedata()
