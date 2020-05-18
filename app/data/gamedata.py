import json
import logging
import time
from copy import deepcopy
from pathlib import Path
from typing import Dict, Set

from .models.common import Region, Settings
from .models.raw import (
    BuffEntity,
    BuffEntityNoReverse,
    FunctionEntity,
    FunctionEntityNoReverse,
    Master,
    ServantEntity,
    SkillEntity,
    SkillEntityNoReverse,
    SvtType,
    TdEntity,
    TdEntityNoReverse,
)


def is_servant(svt_type: int) -> bool:
    return svt_type in [
        SvtType.NORMAL,
        SvtType.HEROINE,
    ]


def is_equip(svt_type: int) -> bool:
    return svt_type == SvtType.SERVANT_EQUIP


settings = Settings()
logger = logging.getLogger()


masters: Dict[Region, Master] = {}
MASTER_WITH_ID = ["mstSvt", "mstBuff", "mstFunc", "mstSkill", "mstTreasureDevice"]
SVT_STUFFS = ["mstSvtCard"]
SKILL_STUFFS = ["mstSkillDetail", "mstSvtSkill", "mstSkillLv"]
TD_STUFFS = ["mstTreasureDeviceDetail", "mstSvtTreasureDevice", "mstTreasureDeviceLv"]
region_path = [(Region.NA, settings.na_gamedata), (Region.JP, settings.jp_gamedata)]

logger.info("Loading game data ...")
start_loading_time = time.time()

for region_name, gamedata in region_path:
    master = {}
    gamedata_path = Path(gamedata).resolve()
    for entity in MASTER_WITH_ID + SVT_STUFFS + SKILL_STUFFS + TD_STUFFS:
        with open(gamedata_path / f"{entity}.json", "r", encoding="utf-8") as fp:
            master[entity] = json.load(fp)
    for entity in MASTER_WITH_ID:
        master[f"{entity}Id"] = {item["id"]: item for item in master[entity]}
    master["mstSvtServantCollectionNo"] = {
        item["collectionNo"]: item["id"]
        for item in master["mstSvt"]
        if is_servant(item["type"]) and item["collectionNo"] != 0
    }
    master["mstSvtServantName"] = {
        item["name"]: item["id"]
        for item in master["mstSvt"]
        if is_servant(item["type"]) and item["collectionNo"] != 0
    }
    master["mstSvtEquipCollectionNo"] = {
        item["collectionNo"]: item["id"]
        for item in master["mstSvt"]
        if is_equip(item["type"]) and item["collectionNo"] != 0
    }
    for extra_stuff in SKILL_STUFFS + TD_STUFFS + SVT_STUFFS:
        master[f"{extra_stuff}Id"] = {}
        for item in master[extra_stuff]:
            if "Detail" in extra_stuff:
                id_name = "id"
            elif extra_stuff in SKILL_STUFFS:
                id_name = "skillId"
            elif extra_stuff in SVT_STUFFS:
                id_name = "svtId"
            elif extra_stuff == "mstTreasureDeviceLv":
                id_name = "treaureDeviceId"
            elif extra_stuff == "mstSvtTreasureDevice":
                id_name = "treasureDeviceId"
            if item[id_name] in master[f"{extra_stuff}Id"]:
                master[f"{extra_stuff}Id"][item[id_name]].append(item)
            else:
                master[f"{extra_stuff}Id"][item[id_name]] = [item]
    masters[region_name] = Master.parse_obj(master)

data_loading_time = time.time() - start_loading_time
logger.info(f"Loaded the game data in {data_loading_time:.4f} seconds.")


def buff_to_func(region: Region, buff_id: int) -> Set[int]:
    return {item.id for item in masters[region].mstFunc if buff_id in item.vals}


def func_to_skillId(region: Region, func_id: int) -> Set[int]:
    return {
        item.skillId for item in masters[region].mstSkillLv if func_id in item.funcId
    }


def func_to_tdId(region: Region, func_id: int) -> Set[int]:
    return {
        item.treaureDeviceId
        for item in masters[region].mstTreasureDeviceLv
        if func_id in item.funcId
    }


def get_buff_entity_no_reverse(region: Region, buff_id: int) -> BuffEntityNoReverse:
    buff_entity = BuffEntityNoReverse(mstBuff=masters[region].mstBuffId[buff_id])
    return buff_entity


def get_buff_entity(region: Region, buff_id: int, reverse: bool = False) -> BuffEntity:
    buff_entity = BuffEntity.parse_obj(get_buff_entity_no_reverse(region, buff_id))
    if reverse:
        reverseFunctions = buff_to_func(region, buff_id)
        buff_entity.reverseFunctions = [
            get_func_entity(region, item_id, reverse) for item_id in reverseFunctions
        ]
    return buff_entity


def get_func_entity_no_reverse(
    region: Region, func_id: int, expand: bool = False
) -> FunctionEntityNoReverse:
    func_entity = FunctionEntityNoReverse(mstFunc=masters[region].mstFuncId[func_id])
    if expand:
        func_entity.mstFunc = deepcopy(func_entity.mstFunc)
        expandedBuff = []
        for buff_id in func_entity.mstFunc.vals:
            if buff_id in masters[region].mstBuffId:
                expandedBuff.append(get_buff_entity_no_reverse(region, buff_id))
        func_entity.mstFunc.expandedVals = expandedBuff
    return func_entity


def get_func_entity(
    region: Region, func_id: int, reverse: bool = False, expand: bool = False
) -> FunctionEntity:
    func_entity = FunctionEntity.parse_obj(
        get_func_entity_no_reverse(region, func_id, expand)
    )
    if reverse:
        reverseSkillIds = func_to_skillId(region, func_id)
        func_entity.reverseSkills = [
            get_skill_entity(region, item_id, reverse) for item_id in reverseSkillIds
        ]
        reverseTdIds = func_to_tdId(region, func_id)
        func_entity.reverseTds = [
            get_td_entity(region, item_id, reverse) for item_id in reverseTdIds
        ]
    return func_entity


def get_skill_entity_no_reverse(
    region: Region, skill_id: int, expand: bool = False
) -> SkillEntityNoReverse:
    skill_entity = SkillEntityNoReverse(
        mstSkill=masters[region].mstSkillId[skill_id],
        mstSkillDetail=masters[region].mstSkillDetailId.get(skill_id, []),
        mstSvtSkill=masters[region].mstSvtSkillId.get(skill_id, []),
        mstSkillLv=masters[region].mstSkillLvId.get(skill_id, []),
    )

    if expand:
        skill_entity.mstSkillLv = deepcopy(skill_entity.mstSkillLv)
        for skillLv in skill_entity.mstSkillLv:
            expandedFunc = []
            for func_id in skillLv.funcId:
                if func_id in masters[region].mstFuncId:
                    expandedFunc.append(
                        get_func_entity_no_reverse(region, func_id, expand)
                    )
            skillLv.expandedFuncId = expandedFunc
    return skill_entity


def get_skill_entity(
    region: Region, skill_id: int, reverse: bool = False, expand: bool = False
) -> SkillEntity:
    skill_entity = SkillEntity.parse_obj(
        get_skill_entity_no_reverse(region, skill_id, expand)
    )

    if reverse:
        reverseServantIds = {item.svtId for item in skill_entity.mstSvtSkill}
        skill_entity.reverseServants = [
            get_servant_entity(region, item_id) for item_id in reverseServantIds
        ]
    return skill_entity


def get_td_entity_no_reverse(
    region: Region, td_id: int, expand: bool = False
) -> TdEntityNoReverse:
    td_entity = TdEntityNoReverse(
        mstTreasureDevice=masters[region].mstTreasureDeviceId[td_id],
        mstTreasureDeviceDetail=masters[region].mstTreasureDeviceDetailId.get(
            td_id, []
        ),
        mstSvtTreasureDevice=masters[region].mstSvtTreasureDeviceId.get(td_id, []),
        mstTreasureDeviceLv=masters[region].mstTreasureDeviceLvId.get(td_id, []),
    )

    if expand:
        td_entity.mstTreasureDeviceLv = deepcopy(td_entity.mstTreasureDeviceLv)
        for tdLv in td_entity.mstTreasureDeviceLv:
            expandedFunc = []
            for func_id in tdLv.funcId:
                if func_id in masters[region].mstFuncId:
                    expandedFunc.append(
                        get_func_entity_no_reverse(region, func_id, expand)
                    )
            tdLv.expandedFuncId = expandedFunc
    return td_entity


def get_td_entity(
    region: Region, td_id: int, reverse: bool = False, expand: bool = False
) -> TdEntity:
    td_entity = TdEntity.parse_obj(get_td_entity_no_reverse(region, td_id, expand))

    if reverse:
        reverseServantIds = {item.svtId for item in td_entity.mstSvtTreasureDevice}
        td_entity.reverseServants = [
            get_servant_entity(region, item_id) for item_id in reverseServantIds
        ]
    return td_entity


def get_servant_entity(
    region: Region, servant_id: int, expand: bool = False
) -> ServantEntity:
    svt_entity = ServantEntity(mstSvt=masters[region].mstSvtId[servant_id])
    skills = [
        item.skillId for item in masters[region].mstSvtSkill if item.svtId == servant_id
    ]
    svt_entity.mstSkill = [
        get_skill_entity_no_reverse(region, skill, expand) for skill in skills
    ]
    NPs = [
        item.treasureDeviceId
        for item in masters[region].mstSvtTreasureDevice
        if item.svtId == servant_id
    ]
    svt_entity.mstTreasureDevice = [
        get_td_entity_no_reverse(region, td, expand) for td in NPs
    ]
    svt_entity.mstSvtCard = masters[region].mstSvtCardId.get(servant_id, [])
    if expand:
        svt_entity.mstSvt = deepcopy(svt_entity.mstSvt)
        expandedPassive = []
        for passiveSkill in svt_entity.mstSvt.classPassive:
            if passiveSkill in masters[region].mstSkillId:
                expandedPassive.append(
                    get_skill_entity_no_reverse(region, passiveSkill, expand)
                )
        svt_entity.mstSvt.expandedClassPassive = expandedPassive
    return ServantEntity.parse_obj(svt_entity)
