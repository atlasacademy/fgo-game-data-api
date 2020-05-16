import json
import logging
import time
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Set

from fastapi import FastAPI, HTTPException, Request
from fuzzywuzzy import fuzz, process
from pydantic import BaseSettings

import utils
from models import ServantEntity, SkillEntity, TdEntity, FunctionEntity, BuffEntity


class Region(str, Enum):
    NA = "NA"
    JP = "JP"


class Settings(BaseSettings):
    na_gamedata: str
    jp_gamedata: str

    class Config:
        env_file = ".env"


logger = logging.getLogger()
settings = Settings()

masters: Dict[str, Dict[str, Any]] = {}
MASTER_WITH_ID = ["mstSvt", "mstBuff", "mstFunc", "mstSkill", "mstTreasureDevice"]
SVT_STUFFS = ["mstSvtCard"]
SKILL_STUFFS = ["mstSkillDetail", "mstSvtSkill", "mstSkillLv"]
TD_STUFFS = ["mstTreasureDeviceDetail", "mstSvtTreasureDevice", "mstTreasureDeviceLv"]
region_path = [(Region.NA, settings.na_gamedata), (Region.JP, settings.jp_gamedata)]

start_loading_time = time.time()
for region_name, gamedata in region_path:
    masters[region_name] = {}
    gamedata_path = Path(gamedata).resolve()
    for entity in MASTER_WITH_ID + SVT_STUFFS + SKILL_STUFFS + TD_STUFFS:
        with open(gamedata_path / f"{entity}.json", "r", encoding="utf-8") as fp:
            masters[region_name][entity] = json.load(fp)
    for entity in MASTER_WITH_ID:
        masters[region_name][f"{entity}Id"] = {
            item["id"]: item for item in masters[region_name][entity]
        }
    masters[region_name]["mstSvtServantCollectionNo"] = {
        item["collectionNo"]: item["id"]
        for item in masters[region_name]["mstSvt"]
        if utils.is_servant(item["type"]) and item["collectionNo"] != 0
    }
    masters[region_name]["mstSvtServantName"] = {
        item["name"]: item["id"]
        for item in masters[region_name]["mstSvt"]
        if utils.is_servant(item["type"]) and item["collectionNo"] != 0
    }
    masters[region_name]["mstSvtEquipCollectionNo"] = {
        item["collectionNo"]: item["id"]
        for item in masters[region_name]["mstSvt"]
        if utils.is_equip(item["type"]) and item["collectionNo"] != 0
    }
    for extra_stuff in SKILL_STUFFS + TD_STUFFS + SVT_STUFFS:
        masters[region_name][f"{extra_stuff}Id"] = {}
        for item in masters[region_name][extra_stuff]:
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
            if item[id_name] in masters[region_name][f"{extra_stuff}Id"]:
                masters[region_name][f"{extra_stuff}Id"][item[id_name]].append(item)
            else:
                masters[region_name][f"{extra_stuff}Id"][item[id_name]] = [item]

data_loading_time = time.time() - start_loading_time
logger.info(f"Loaded the game data in {data_loading_time:.4f} seconds.")


def buff_to_func(region: Region, buff_id: int) -> Set[int]:
    return {
        item["id"] for item in masters[region]["mstFunc"] if buff_id in item["vals"]
    }


def func_to_skillId(region: Region, func_id: int) -> Set[int]:
    return {
        item["skillId"]
        for item in masters[region]["mstSkillLv"]
        if func_id in item["funcId"]
    }


def get_buff_entity(region: Region, buff_id: int, reverse: bool = False) -> Any:
    buff_entity = {"mstBuff": masters[region]["mstBuffId"][buff_id]}
    if reverse:
        reverseFunctions = buff_to_func(region, buff_id)
        buff_entity["reverseFunctions"] = [
            get_func_entity(region, item_id, reverse) for item_id in reverseFunctions
        ]
    return buff_entity


def get_func_entity(
    region: Region, func_id: int, reverse: bool = False, expand: bool = False
) -> Any:
    func_entity = {"mstFunc": masters[region]["mstFuncId"][func_id].copy()}
    if reverse:
        reverseSkillIds = func_to_skillId(region, func_id)
        func_entity["reverseSkills"] = [
            get_skill_entity(region, item_id, reverse) for item_id in reverseSkillIds
        ]
    if expand:
        expandedBuff = []
        for buff_id in func_entity["mstFunc"]["vals"]:
            expandedBuff.append(get_buff_entity(region, buff_id, False))
        func_entity["mstFunc"]["expandedVals"] = expandedBuff
    return func_entity


def get_skill_entity(
    region: Region, skill_id: int, reverse: bool = False, expand: bool = False
) -> Any:
    skill_entity = {"mstSkill": masters[region]["mstSkillId"][skill_id]}
    for skill_extra in SKILL_STUFFS:
        skill_entity[skill_extra] = (
            masters[region][f"{skill_extra}Id"].get(skill_id, []).copy()
        )
    if reverse:
        reverseServantIds = {item["svtId"] for item in skill_entity["mstSvtSkill"]}
        skill_entity["reverseServants"] = [
            get_servant_entity(region, item_id) for item_id in reverseServantIds
        ]
    if expand:
        for skillLv in skill_entity["mstSkillLv"]:
            expandedFunc = []
            for func_id in skillLv["funcId"]:
                expandedFunc.append(get_func_entity(region, func_id, False, expand))
            skillLv["expandedFuncId"] = expandedFunc
    return skill_entity


def get_td_entity(
    region: Region, td_id: int, reverse: bool = False, expand: bool = False
) -> Any:
    td_entity = {"mstTreasureDevice": masters[region]["mstTreasureDeviceId"][td_id]}
    for td_extra in TD_STUFFS:
        td_entity[td_extra] = masters[region][f"{td_extra}Id"].get(td_id, [])
    if reverse:
        reverseServantIds = {
            item["svtId"] for item in td_entity["mstSvtTreasureDevice"]
        }
        td_entity["reverseServants"] = [
            get_servant_entity(region, item_id) for item_id in reverseServantIds
        ]
    if expand:
        for tdLv in td_entity["mstTreasureDeviceLv"]:
            expandedFunc = []
            for func_id in tdLv["funcId"]:
                expandedFunc.append(get_func_entity(region, func_id, False, expand))
            tdLv["expandedFuncId"] = expandedFunc
    return td_entity


def get_servant_entity(region: Region, servant_id: int, expand: bool = False) -> Any:
    svt_entity = {"mstSvt": masters[region]["mstSvtId"][servant_id]}
    skills = [
        item["skillId"]
        for item in masters[region]["mstSvtSkill"]
        if item["svtId"] == servant_id
    ]
    svt_entity["mstSkill"] = [
        get_skill_entity(region, skill, False, expand) for skill in skills
    ]
    NPs = [
        item["treasureDeviceId"]
        for item in masters[region]["mstSvtTreasureDevice"]
        if item["svtId"] == servant_id
    ]
    svt_entity["mstTreasureDevice"] = [
        get_td_entity(region, td, False, expand) for td in NPs
    ]
    for svt_extra in SVT_STUFFS:
        svt_entity[svt_extra] = (
            masters[region][f"{svt_extra}Id"].get(servant_id, []).copy()
        )
    if expand:
        expandedPassive = []
        for passiveSkill in svt_entity["mstSvt"]["classPassive"]:
            expandedPassive.append(
                get_skill_entity(region, passiveSkill, False, expand)
            )
        svt_entity["mstSvt"]["expandedClassPassive"] = expandedPassive
    return svt_entity


app = FastAPI(
    title="FGO Game data API",
    description="Provide raw and processed FGO game data",
    version="0.0.1",
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = int((time.time() - start_time) * 1000)
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Processed in {process_time}ms.")
    return response


@app.get(
    "/raw/{region}/servant/{item_id}",
    tags=["raw"],
    summary="Get servant data",
    response_description="Servant Entity",
    response_model=ServantEntity,
    response_model_exclude_unset=True,
)
async def get_servant(region: Region, item_id: int, expand: bool = False):
    """
    Get servant info from ID

    If the given ID is a servants's collectionNo, the corresponding servant data is returned.
    Otherwise, it will look up the actual ID field. As a result, it can return not servant data.

    - **expand**: Add expanded skill objects to mstSvt.expandedClassPassive
    from the skill IDs in mstSvt.classPassive.
    Expand all other skills and functions as well.
    """
    if item_id in masters[region]["mstSvtServantCollectionNo"]:
        item_id = masters[region]["mstSvtServantCollectionNo"][item_id]
    if item_id in masters[region]["mstSvtId"]:
        return get_servant_entity(region, item_id, expand)
    else:
        raise HTTPException(status_code=404, detail="Servant not found")


@app.get(
    "/raw/{region}/servant/",
    tags=["raw"],
    summary="Find and get servant data",
    response_description="Servant Entity",
    response_model=ServantEntity,
    response_model_exclude_unset=True,
)
async def find_servant(
    region: Region, name: Optional[str] = None, expand: bool = False
):
    """
    Get servant info from ID

    Search the servants' names list for the given name and return the best match.

    - **expand**: Add expanded skill objects to mstSvt.expandedClassPassive
    from the skill IDs in mstSvt.classPassive.
    Expand all other skills and functions as well.
    """
    if name:
        servant_found = process.extract(
            name,
            masters[region]["mstSvtServantName"].keys(),
            scorer=fuzz.token_set_ratio,
        )
        # return servant_found
        items_found = [
            masters[region]["mstSvtServantName"][found[0]]
            for found in servant_found
            if found[1] > 85
        ]
        if len(items_found) >= 1:
            items_found = [
                get_servant_entity(region, item_id, expand) for item_id in items_found
            ]
            items_found = sorted(items_found, key=lambda x: x["mstSvt"]["collectionNo"])
            return items_found[0]
        else:
            raise HTTPException(status_code=404, detail="Servant not found")


@app.get(
    "/raw/{region}/equip/{item_id}",
    tags=["raw"],
    summary="Get CE data",
    response_description="CE entity",
    response_model=ServantEntity,
    response_model_exclude_unset=True,
)
async def get_equip(region: Region, item_id: int, expand: bool = False):
    """
    Get CE info from ID

    If the given ID is a CE's collectionNo, the corresponding CE data is returned.
    Otherwise, it will look up the actual ID field. As a result, it can return not CE data.

    - **expand**: Add expanded skill objects to mstSvt.expandedClassPassive
    from the skill IDs in mstSvt.classPassive.
    Expand all other skills and functions as well.
    """
    if item_id in masters[region]["mstSvtEquipCollectionNo"]:
        item_id = masters[region]["mstSvtEquipCollectionNo"][item_id]
    if item_id in masters[region]["mstSvtId"]:
        return get_servant_entity(region, item_id, expand)
    else:
        raise HTTPException(status_code=404, detail="Equip not found")


@app.get(
    "/raw/{region}/skill/{item_id}",
    tags=["raw"],
    summary="Get skill data",
    response_description="Skill entity",
    response_model=SkillEntity,
    response_model_exclude_unset=True,
)
async def get_skill(
    region: Region, item_id: int, reverse: bool = False, expand: bool = False
):
    """
    Get the skill data from the given ID

    - **reverse**: Reverse lookup the servants that have this skill
    and return the reverse skill objects.
    - **expand**: Add expanded function objects to mstSkillLv.expandedFuncId
    from the function IDs in mstSkillLv.funcId.
    """
    if item_id in masters[region]["mstSkillId"]:
        return get_skill_entity(region, item_id, reverse, expand)
    else:
        raise HTTPException(status_code=404, detail="Skill not found")


@app.get(
    "/raw/{region}/NP/{item_id}",
    tags=["raw"],
    summary="Get NP data",
    response_description="NP entity",
    response_model=TdEntity,
    response_model_exclude_unset=True,
)
async def get_td(
    region: Region, item_id: int, reverse: bool = False, expand: bool = False
):
    """
    Get the NP data from the given ID

    - **reverse**: Reverse lookup the servants that have this NP
    and return the reversed servant objects.
    - **expand**: Add expanded function objects to mstTreasureDeviceLv.expandedFuncId
    from the function IDs in mstTreasureDeviceLv.funcId.
    """
    if item_id in masters[region]["mstTreasureDeviceId"]:
        return get_td_entity(region, item_id, reverse, expand)
    else:
        raise HTTPException(status_code=404, detail="NP not found")


@app.get(
    "/raw/{region}/function/{item_id}",
    tags=["raw"],
    summary="Get function data",
    response_description="Function entity",
    response_model=FunctionEntity,
    response_model_exclude_unset=True,
)
async def get_function(
    region: Region, item_id: int, reverse: bool = False, expand: bool = False
):
    """
    Get the function data from the given ID

    - **reverse**: Reverse lookup the skills that have this function
    and return the reversed skill objects.
    Will search recursively and return all entities in path: func -> skill -> servant.
    - **expand**: Add buff objects to mstFunc.expandedVals
    from the buff IDs in mstFunc.vals.
    """
    if item_id in masters[region]["mstFuncId"]:
        return get_func_entity(region, item_id, reverse, expand)
    else:
        raise HTTPException(status_code=404, detail="Function not found")


@app.get(
    "/raw/{region}/buff/{item_id}",
    tags=["raw"],
    summary="Get buff data",
    response_description="Buff entity",
    response_model=BuffEntity,
    response_model_exclude_unset=True,
)
async def get_buff(region: Region, item_id: int, reverse: bool = False):
    """
    Get the buff data from the given ID

    - **reverse**: Reverse lookup the functions that have this buff
    and return the reversed function objects.
    Will search recursively and return all entities in path: buff -> func -> skill -> servant.
    """
    if item_id in masters[region]["mstBuffId"]:
        return get_buff_entity(region, item_id, reverse)
    else:
        raise HTTPException(status_code=404, detail="Buff not found")
