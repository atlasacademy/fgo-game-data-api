import time
from collections import defaultdict
from typing import Dict

import orjson

from ..config import Settings, logger
from ..db.base import engines
from ..models.raw import TABLES_TO_BE_LOADED, metadata, mstSubtitle
from ..schemas.common import Region
from ..schemas.enums import FUNC_VALS_NOT_BUFF, CondType, PurchaseType, SvtType
from ..schemas.raw import (
    BAD_COMBINE_SVT_LIMIT,
    Master,
    get_subtitle_svtId,
    is_equip,
    is_servant,
)


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
MASTER_WITHOUT_ID = {
    "mstEquipExp",
    "mstEquipSkill",
    "mstCommandCodeSkill",
    "mstCommandCodeComment",
    "mstClosedMessage",
    "mstConstant",
    "mstClassRelationOverwrite",
    "mstStage",
    "mstGift",
    "mstShop",
    "mstShopRelease",
    "mstAi",
    "mstAiField",
    "mstFuncGroup",
    "mstAiAct",
}
SVT_STUFFS = {
    "mstSvtExp",
    "mstSvtScript",
    "mstFriendship",
    "mstSvtGroup",
    "mstSvtLimit",
    "mstSvtLimitAdd",
    "mstSvtVoiceRelation",
    "mstCombineSkill",
    "mstCombineLimit",
    "mstCombineCostume",
    "mstCombineMaterial",
}
SKILL_STUFFS = {"mstSvtSkill", "mstSkillLv"}
TD_STUFFS = {"mstSvtTreasureDevice", "mstTreasureDeviceLv"}
LATEST_VALENTINE_EVENT = {Region.NA: 80089, Region.JP: 80276}
region_path = {Region.JP: settings.jp_gamedata, Region.NA: settings.na_gamedata}


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
            svt["collectionNo"]: svt["id"]
            for svt in master["mstSvt"]
            if is_servant(svt["type"]) and svt["collectionNo"] != 0
        }

        master["mstSvtEquipCollectionNo"] = {
            svt["collectionNo"]: svt["id"]
            for svt in master["mstSvt"]
            if is_equip(svt["type"]) and svt["collectionNo"] != 0
        }

        master["mstCCCollectionNo"] = {
            cc["collectionNo"]: cc["id"] for cc in master["mstCommandCode"]
        }

        master["mstFriendshipId"] = defaultdict(list)
        master["mstFriendship"] = sorted(
            master["mstFriendship"], key=lambda item: item["rank"]  # type: ignore
        )
        for friendship in master["mstFriendship"]:
            if friendship["friendship"] != -1:
                master["mstFriendshipId"][friendship["id"]].append(
                    friendship["friendship"]
                )

        master["mstSvtScriptId"] = defaultdict(list)
        for svt_script in master["mstSvtScript"]:
            master["mstSvtScriptId"][svt_script["id"] // 10].append(svt_script)

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

        for masters_table, source_table, lookup_id, result_id in (
            ("mstClosedMessageId", "mstClosedMessage", "id", "message"),
            ("mstConstantId", "mstConstant", "name", "value"),
        ):
            master[masters_table] = {
                item[lookup_id]: item[result_id] for item in master[source_table]
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

        master["mstSvtLimitFirst"] = {}
        for svtLimit in master["mstSvtLimit"]:
            if svtLimit["svtId"] not in master["mstSvtLimitFirst"]:
                master["mstSvtLimitFirst"][svtLimit["svtId"]] = svtLimit

        master["mstSvtLimitAddIndividutality"] = defaultdict(list)
        for svtLimitAdd in master["mstSvtLimitAdd"]:
            master["mstSvtLimitAddIndividutality"][svtLimitAdd["svtId"]].extend(
                svtLimitAdd["individuality"]
            )

        master["spotToWarId"] = {}
        for spot in master["mstSpot"]:
            master["spotToWarId"][spot["id"]] = spot["warId"]

        master["mstSvtExp"] = sorted(master["mstSvtExp"], key=lambda item: item["lv"])  # type: ignore
        master["mstCombineMaterial"] = sorted(master["mstCombineMaterial"], key=lambda item: item["lv"])  # type: ignore

        for masters_table, source_table, lookup_id in (
            ("mstClassRelationOverwriteId", "mstClassRelationOverwrite", "id"),
            ("mstCombineMaterialId", "mstCombineMaterial", "id"),
            ("mstSvtExpId", "mstSvtExp", "type"),
            ("mstSvtGroupId", "mstSvtGroup", "id"),
            ("mstSvtGroupSvtId", "mstSvtGroup", "svtId"),
            ("mstSvtSkillSvtId", "mstSvtSkill", "svtId"),
            ("mstSvtVoiceRelationId", "mstSvtVoiceRelation", "svtId"),
            ("mstMapWarId", "mstMap", "warId"),
            ("mstWarEventId", "mstWar", "eventId"),
            ("mstGiftId", "mstGift", "id"),
            ("mstShopEventId", "mstShop", "eventId"),
            ("mstShopReleaseShopId", "mstShopRelease", "shopId"),
            ("mstCommandCodeCommentId", "mstCommandCodeComment", "commandCodeId"),
            ("mstFuncGroupId", "mstFuncGroup", "funcId"),
        ):
            master[masters_table] = defaultdict(list)
            for item in master[source_table]:
                master[masters_table][item[lookup_id]].append(item)

        master["bondEquip"] = {}
        for svt in master["mstSvt"]:
            if (
                svt["type"] == SvtType.SERVANT_EQUIP
                and svt["id"] in master["mstSvtSkillSvtId"]
            ):
                actIndividualities = set()
                for skill in master["mstSvtSkillSvtId"][svt["id"]]:
                    mst_skill = master["mstSkillId"].get(skill["skillId"])
                    if mst_skill:
                        actIndividualities.add(tuple(mst_skill["actIndividuality"]))
                if len(actIndividualities) == 1:
                    individualities = actIndividualities.pop()
                    if (
                        len(individualities) == 1
                        and individualities[0] in master["mstSvtId"]
                    ):
                        master["bondEquip"][individualities[0]] = svt["id"]

        master["valentineEquip"] = defaultdict(list)
        for shop in master["mstShopEventId"][LATEST_VALENTINE_EVENT[region_name]]:
            if shop["purchaseType"] == PurchaseType.SERVANT:
                for shopRelease in master["mstShopReleaseShopId"][shop["id"]]:
                    if shopRelease["condType"] == CondType.SVT_GET:
                        master["valentineEquip"][shopRelease["condValues"][0]].append(
                            shop["targetIds"][0]
                        )
                        break

        masters[region_name] = Master.parse_obj(master)

    data_loading_time = time.perf_counter() - start_loading_time
    logger.info(f"Loaded game data in {data_loading_time:.2f}s.")


def update_db() -> None:  # pragma: no cover
    logger.info("Loading db …")
    start_loading_time = time.perf_counter()
    for region_name, gamedata in region_path.items():
        engine = engines[region_name]

        metadata.drop_all(engine)
        metadata.create_all(engine)

        with engine.connect() as conn:
            for table in TABLES_TO_BE_LOADED:
                with open(gamedata / f"{table.name}.json", "rb") as fp:
                    data = orjson.loads(fp.read())
                conn.execute(table.insert(data))

            if region_name == Region.NA:
                with open(gamedata / "globalNewMstSubtitle.json", "rb") as fp:
                    globalNewMstSubtitle = orjson.loads(fp.read())
                for subtitle in globalNewMstSubtitle:
                    subtitle["svtId"] = get_subtitle_svtId(subtitle["id"])
                conn.execute(mstSubtitle.insert(globalNewMstSubtitle))

    db_loading_time = time.perf_counter() - start_loading_time
    logger.info(f"Loaded db in {db_loading_time:.2f}s.")


if settings.write_postgres_data:  # pragma: no cover
    update_db()


update_gamedata()
