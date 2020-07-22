import time
from typing import Any, Dict, List

import orjson

from ..config import Settings, logger
from .common import Region
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
}
MASTER_WITHOUT_ID = {
    "mstSvtExp",
    "mstFriendship",
    "mstEquipExp",
    "mstEquipSkill",
    "mstQuestPhase",
    "mstCommandCodeSkill",
    "mstCommandCodeComment",
}
SVT_STUFFS = {
    "mstSvtCard",
    "mstSvtLimit",
    "mstCombineSkill",
    "mstCombineLimit",
    "mstSvtLimitAdd",
    "mstSvtComment",
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
            MASTER_WITH_ID | MASTER_WITHOUT_ID | SVT_STUFFS | SKILL_STUFFS | TD_STUFFS
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

        for extra_stuff in SKILL_STUFFS | TD_STUFFS | SVT_STUFFS:
            master[f"{extra_stuff}Id"] = {}
            for item in master[extra_stuff]:
                if "Detail" in extra_stuff:
                    id_name = "id"
                elif extra_stuff in {"mstCombineSkill", "mstCombineLimit"}:
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
                if item[id_name] in master[f"{extra_stuff}Id"]:
                    master[f"{extra_stuff}Id"][item[id_name]].append(item)
                else:
                    master[f"{extra_stuff}Id"][item[id_name]] = [item]
        masters[region_name] = Master.parse_obj(master)

    data_loading_time = time.perf_counter() - start_loading_time
    logger.info(f"Loaded the game data in {data_loading_time:.4f}s.")


update_gamedata()
