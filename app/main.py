import json
import logging
import time
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

from fastapi import FastAPI, HTTPException, Request
from fuzzywuzzy import fuzz, process
from pydantic import BaseSettings

import utils


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
MASTER_WITH_ID = ["mstSvt", "mstBuff", "mstFunc", "mstSkill"]
# MASTER_WITHOUT_ID = ["mstSkillLv", "mstSvtSkill", "mstSkillDetail"]
SKILL_STUFFS = ["mstSkillDetail", "mstSvtSkill", "mstSkillLv"]
region_path = [(Region.NA, settings.na_gamedata), (Region.JP, settings.jp_gamedata)]

start_loading_time = time.time()
for region_name, gamedata in region_path:
    masters[region_name] = {}
    gamedata_path = Path(gamedata).resolve()
    for entity in MASTER_WITH_ID + SKILL_STUFFS:
        with open(gamedata_path / f"{entity}.json", "r", encoding="utf-8") as fp:
            masters[region_name][entity] = json.load(fp)
    for entity in MASTER_WITH_ID:
        masters[region_name][f"{entity}Id"] = {
            item["id"]: item for item in masters[region_name][entity]
        }
    masters[region_name]["mstSvtServantCollectionNo"] = {
        item["collectionNo"]: item
        for item in masters[region_name]["mstSvt"]
        if utils.is_servant(item["type"])
    }
    masters[region_name]["mstSvtServantName"] = {
        item["name"]: item
        for item in masters[region_name]["mstSvtServantCollectionNo"].values()
    }
    masters[region_name]["mstSvtEquipCollectionNo"] = {
        item["collectionNo"]: item
        for item in masters[region_name]["mstSvt"]
        if utils.is_equip(item["type"])
    }
    for skill_stuff in SKILL_STUFFS:
        masters[region_name][f"{skill_stuff}Id"] = {}
        for item in masters[region_name][skill_stuff]:
            if skill_stuff == "mstSkillDetail":
                id_name = "id"
            else:
                id_name = "skillId"
            if item[id_name] in masters[region_name][f"{skill_stuff}Id"]:
                masters[region_name][f"{skill_stuff}Id"][item[id_name]].append(item)
            else:
                masters[region_name][f"{skill_stuff}Id"][item[id_name]] = [item]

data_loading_time = time.time() - start_loading_time
logger.info(f"Loaded the game data in {data_loading_time:.4f} seconds.")


def buff_to_func(region: Region, buff_id: int) -> Sequence[int]:
    return [
        item["id"] for item in masters[region]["mstFunc"] if buff_id in item["vals"]
    ]


def func_to_skillId(region: Region, func_id: int) -> Sequence[int]:
    return list(
        {
            item["skillId"]
            for item in masters[region]["mstSkillLv"]
            if func_id in item["funcId"]
        }
    )


def get_buff_entity(region: Region, buff_id: int, reverse: bool = False) -> Any:
    buff_item = {"mstBuff": masters[region]["mstBuffId"][buff_id]}
    if reverse:
        reverseFunctions = buff_to_func(region, buff_id)
        buff_item["reverseFunctions"] = [
            get_func_entity(region, item_id, reverse) for item_id in reverseFunctions
        ]
    return buff_item


def get_func_entity(region: Region, func_id: int, reverse: bool = False) -> Any:
    func_entity = {"mstFunc": masters[region]["mstFuncId"][func_id]}
    if reverse:
        reverseSkillIds = func_to_skillId(region, func_id)
        func_entity["reverseSkills"] = [
            get_skill_entity(region, item_id, reverse) for item_id in reverseSkillIds
        ]
    return func_entity


def get_skill_entity(region: Region, skill_id: int, reverse: bool = False) -> Any:
    skill_entity = {"mstSkill": masters[region]["mstSkillId"][skill_id]}
    for skill_extra in SKILL_STUFFS:
        skill_entity[skill_extra] = masters[region][f"{skill_extra}Id"].get(
            skill_id, []
        )
    if reverse:
        reverseServantIds = [item["svtId"] for item in skill_entity["mstSvtSkill"]]
        skill_entity["reverseServants"] = [
            get_servant_entity(region, item_id) for item_id in reverseServantIds
        ]
    return skill_entity


def get_servant_entity(region: Region, servant_id: int) -> Any:
    servant_entity = {"mstSvt": masters[region]["mstSvtId"][servant_id])}
    return servant_entity


app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Processed in {process_time:.4f} seconds.")
    return response


@app.get("/{region}/servant/{item_id}")
async def get_servant(region: Region, item_id: int):
    if item_id in masters[region]["mstSvtServantCollectionNo"]:
        return masters[region]["mstSvtServantCollectionNo"][item_id]
    elif item_id in masters[region]["mstSvtId"]:
        return get_servant_entity(region, item_id)
    else:
        raise HTTPException(status_code=404, detail="Servant not found")


@app.get("/{region}/servant/")
async def find_servant(region: Region, name: Optional[str] = None):
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
            items_found = sorted(items_found, key=lambda x: x["collectionNo"])
            return items_found[0]
        else:
            raise HTTPException(status_code=404, detail="Servant not found")


@app.get("/{region}/equip/{item_id}")
async def get_equip(region: Region, item_id: int):
    if item_id in masters[region]["mstSvtEquipCollectionNo"]:
        return masters[region]["mstSvtEquipCollectionNo"][item_id]
    elif item_id in masters[region]["mstSvtId"]:
        return get_servant_entity(region, item_id)
    else:
        raise HTTPException(status_code=404, detail="Equip not found")


@app.get("/{region}/skill/{item_id}")
async def get_skill(region: Region, item_id: int, reverse: bool = False):
    if item_id in masters[region]["mstSkillId"]:
        return get_skill_entity(region, item_id, reverse)
    else:
        raise HTTPException(status_code=404, detail="Skill not found")


@app.get("/{region}/function/{item_id}")
async def get_function(region: Region, item_id: int, reverse: bool = False):
    if item_id in masters[region]["mstFuncId"]:
        return get_func_entity(region, item_id, reverse)
    else:
        raise HTTPException(status_code=404, detail="Function not found")


@app.get("/{region}/buff/{item_id}")
async def get_buff(region: Region, item_id: int, reverse: bool = False):
    if item_id in masters[region]["mstBuffId"]:
        return get_buff_entity(region, item_id, reverse)
    else:
        raise HTTPException(status_code=404, detail="Buff not found")
