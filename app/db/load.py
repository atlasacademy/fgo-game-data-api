import hashlib
import time
from collections import defaultdict
from typing import Any, Optional, Sequence, Union

import orjson
from pydantic import DirectoryPath
from sqlalchemy import Table
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.sql import text

from ..config import logger
from ..data.buff import get_buff_with_classrelation
from ..data.event import get_event_with_warIds
from ..data.gift import get_gift_with_index
from ..data.item import get_item_with_use
from ..data.script import get_script_path, get_script_text_only
from ..models.raw import (
    TABLES_TO_BE_LOADED,
    AssetStorage,
    ScriptFileList,
    mstBuff,
    mstEvent,
    mstFunc,
    mstFuncGroup,
    mstGift,
    mstItem,
    mstSkillGroupOverwrite,
    mstSkillLv,
    mstSubtitle,
    mstTreasureDeviceLv,
    mstWar,
)
from ..models.rayshift import rayshiftQuest, rayshiftQuestHash
from ..schemas.base import BaseModelORJson
from ..schemas.common import Region
from ..schemas.enums import FUNC_VALS_NOT_BUFF
from ..schemas.gameenums import BuffType, FuncType
from ..schemas.raw import AssetStorageLine, get_subtitle_svtId
from ..schemas.rayshift import QuestDetail, QuestList
from .engine import engines
from .helpers.rayshift import (
    fetch_all_missing_quest_ids,
    fetch_missing_quest_ids,
    insert_rayshift_quest_db_sync,
    insert_rayshift_quest_hash_db_sync,
    insert_rayshift_quest_list,
)


def recreate_table(conn: Connection, table: Table) -> None:  # pragma: no cover
    logger.debug(f"Recreating table {table.name}")
    table.drop(conn, checkfirst=True)
    table.create(conn, checkfirst=True)


def insert_db(conn: Connection, table: Table, db_data: Any) -> None:  # pragma: no cover
    recreate_table(conn, table)
    logger.debug(f"Inserting into {table.name}")
    conn.execute(table.insert(), db_data)


def diff_column_schemas(
    data: list[dict[str, Any]], table: Table
) -> set[str]:  # pragma: no cover
    table_columns = {column.name for column in table.columns}
    return data[0].keys() - table_columns


def remove_unknown_columns(
    data: list[dict[str, Any]], table: Table
) -> list[dict[str, Any]]:  # pragma: no cover
    table_columns = {column.name for column in table.columns}
    return [{k: v for k, v in item.items() if k in table_columns} for item in data]


BUFF_TRIGGERING_SKILLS_VALUE = {
    BuffType.DELAY_FUNCTION,
    BuffType.DEAD_FUNCTION,
    BuffType.BATTLESTART_FUNCTION,
    BuffType.WAVESTART_FUNCTION,
    BuffType.SELFTURNEND_FUNCTION,
    BuffType.DAMAGE_FUNCTION,
    BuffType.COMMANDATTACK_FUNCTION,
    BuffType.DEADATTACK_FUNCTION,
    BuffType.ENTRY_FUNCTION,
    BuffType.REFLECTION_FUNCTION,
    BuffType.ATTACK_FUNCTION,
    BuffType.COMMANDCODEATTACK_FUNCTION,
    BuffType.COMMANDATTACK_BEFORE_FUNCTION,
    BuffType.GUTS_FUNCTION,
    BuffType.COMMANDCODEATTACK_AFTER_FUNCTION,
    BuffType.ATTACK_BEFORE_FUNCTION,
    BuffType.SELFTURNSTART_FUNCTION,
}


def get_Value_from_sval(sval: str) -> int:
    return int(sval.split(",")[3])


BUFF_TRIGGERING_SKILLS_SKILL_ID = {BuffType.NPATTACK_PREV_BUFF}


def get_SkillID_from_sval(sval: str) -> int:
    return int(
        next(val for val in sval.split(",") if "SkillID:" in val).removeprefix(
            "SkillID:"
        )
    )


def load_skill_td_lv(
    conn: Connection, gamedata_path: DirectoryPath
) -> None:  # pragma: no cover
    master_folder = gamedata_path / "master"

    mstBuffId = get_buff_with_classrelation(gamedata_path)

    with open(master_folder / "mstFunc.json", "rb") as fp:
        mstFunc_data = orjson.loads(fp.read())
        mstFuncId = {func["id"]: func for func in mstFunc_data}

    mstFuncGroupId = defaultdict(list)
    with open(master_folder / "mstFuncGroup.json", "rb") as fp:
        mstFuncGroup_data = orjson.loads(fp.read())
        for funcGroup in mstFuncGroup_data:
            mstFuncGroupId[funcGroup["funcId"]].append(funcGroup)

    with open(master_folder / "mstSkillLv.json", "rb") as fp:
        mstSkillLv_data = orjson.loads(fp.read())

    group_overwrite_file = master_folder / "mstSkillGroupOverwrite.json"
    if group_overwrite_file.exists():
        with open(group_overwrite_file, "rb") as fp:
            mstSkillGroupOverwrite_data = orjson.loads(fp.read())
    else:
        mstSkillGroupOverwrite_data = []

    with open(master_folder / "mstTreasureDeviceLv.json", "rb") as fp:
        mstTreasureDeviceLv_data = orjson.loads(fp.read())

    def get_func_entity(func_id: int) -> dict[Any, Any]:
        func_entity = {
            "mstFunc": mstFuncId[func_id],
            "mstFuncGroup": mstFuncGroupId.get(func_id, []),
        }

        if (
            func_entity["mstFunc"]["funcType"] not in FUNC_VALS_NOT_BUFF
            and func_entity["mstFunc"]["vals"]
            and func_entity["mstFunc"]["vals"][0] in mstBuffId
        ):
            func_entity["mstFunc"]["expandedVals"] = [
                {"mstBuff": mstBuffId[func_entity["mstFunc"]["vals"][0]].dict()}
            ]
        else:
            func_entity["mstFunc"]["expandedVals"] = []

        return func_entity

    def get_trigger_skill_ids(entity_lv: dict[str, Any]) -> list[int]:
        skill_ids = set()

        for field_name in ("svals", "svals2", "svals3", "svals4", "svals5"):
            if field_name in entity_lv:
                for func_id, sval in zip(
                    entity_lv["funcId"], entity_lv[field_name], strict=False
                ):
                    if func_id in mstFuncId:
                        func = mstFuncId[func_id]
                        if (
                            func["funcType"]
                            in [FuncType.ADD_STATE, FuncType.ADD_STATE_SHORT]
                            and func["vals"]
                        ):
                            buff_id = func["vals"][0]
                            if buff_id in mstBuffId:
                                buff = mstBuffId[buff_id]
                                if buff.type in BUFF_TRIGGERING_SKILLS_VALUE:
                                    skill_ids.add(get_Value_from_sval(sval))
                                elif buff.type in BUFF_TRIGGERING_SKILLS_SKILL_ID:
                                    skill_ids.add(get_SkillID_from_sval(sval))

        return sorted(skill_ids)

    for skillLv in mstSkillLv_data:
        skillLv["expandedFuncId"] = [
            get_func_entity(func_id)
            for func_id in skillLv["funcId"]
            if func_id in mstFuncId
        ]
        skillLv["relatedSkillIds"] = get_trigger_skill_ids(skillLv)

    for groupOverwrite in mstSkillGroupOverwrite_data:
        groupOverwrite["expandedFuncId"] = [
            get_func_entity(func_id)
            for func_id in groupOverwrite["funcId"]
            if func_id in mstFuncId
        ]

    for treasureDeviceLv in mstTreasureDeviceLv_data:
        treasureDeviceLv["expandedFuncId"] = [
            get_func_entity(func_id)
            for func_id in treasureDeviceLv["funcId"]
            if func_id in mstFuncId
        ]
        treasureDeviceLv["relatedSkillIds"] = get_trigger_skill_ids(treasureDeviceLv)

    load_pydantic_to_db(conn, list(mstBuffId.values()), mstBuff)

    insert_db(conn, mstFunc, mstFunc_data)
    insert_db(conn, mstFuncGroup, mstFuncGroup_data)
    insert_db(conn, mstSkillLv, mstSkillLv_data)
    insert_db(conn, mstSkillGroupOverwrite, mstSkillGroupOverwrite_data)
    insert_db(conn, mstTreasureDeviceLv, mstTreasureDeviceLv_data)


def load_event(
    conn: Connection, gamedata_path: DirectoryPath
) -> None:  # pragma: no cover
    event_war = get_event_with_warIds(gamedata_path)
    load_pydantic_to_db(conn, event_war.mstEvents, mstEvent)

    mstWar_db_data = [orjson.loads(war.json()) for war in event_war.mstWars]
    insert_db(conn, mstWar, mstWar_db_data)


def load_item(
    conn: Connection, gamedata_path: DirectoryPath
) -> None:  # pragma: no cover
    mstItems = get_item_with_use(gamedata_path)
    mstItem_db_data = [item.dict() for item in mstItems]
    insert_db(conn, mstItem, mstItem_db_data)


def load_gift(
    conn: Connection, gamedata_path: DirectoryPath
) -> None:  # pragma: no cover
    mstGifts = get_gift_with_index(gamedata_path)
    insert_db(conn, mstGift, [item.dict() for item in mstGifts])


def load_script_list(
    engine: Engine, region: Region, repo_folder: DirectoryPath
) -> None:  # pragma: no cover
    script_list_file = (
        repo_folder
        / "ScriptActionEncrypt"
        / ScriptFileList.name
        / f"{ScriptFileList.name}.txt"
    )
    db_data: list[dict[str, Union[int, str, None]]] = []

    if script_list_file.exists():
        with open(script_list_file, encoding="utf-8") as fp:
            script_list = [line.strip() for line in fp.readlines()]

        with open(repo_folder / "master" / "mstQuest.json", "rb") as bfp:
            mstQuest = orjson.loads(bfp.read())

        all_quest_ids = {quest["id"]: quest for quest in mstQuest}

        overwrite_script_quest_id: dict[int, list[int]] = defaultdict(list)
        for quest in mstQuest:
            if quest["scriptQuestId"] != 0:
                overwrite_script_quest_id[quest["scriptQuestId"]].append(quest["id"])

        for script in script_list:
            script_name = script.removesuffix(".txt")
            script_path = (
                repo_folder
                / "ScriptActionEncrypt"
                / f"{get_script_path(script_name)}.txt"
            )

            if script_path.exists():
                with open(script_path, "r", encoding="utf-8") as fp:
                    script_data = fp.read()
                    script_text = get_script_text_only(region, script_data)
                    script_sha1 = hashlib.sha1(script_text.encode("utf-8")).hexdigest()
            else:
                script_data = ""
                script_text = ""
                script_sha1 = ""

            quest_ids: list[int] = []
            phase: Optional[int] = None
            scene_type: Optional[int] = None

            if len(script) == 14 and script[0] in ("0", "9"):
                inferred_quest_id = int(script_name[:-2])

                scene_type = int(script_name[-1])
                phase = int(script_name[-2])

                if inferred_quest_id in overwrite_script_quest_id:
                    quest_ids.extend(overwrite_script_quest_id[inferred_quest_id])

                if (
                    inferred_quest_id in all_quest_ids
                    and all_quest_ids[inferred_quest_id]["scriptQuestId"] == 0
                ):
                    quest_ids.append(inferred_quest_id)

            if not quest_ids:
                quest_ids.append(-1)

            for quest_id in quest_ids:
                db_data.append(
                    {
                        "scriptFileName": script_name,
                        "questId": quest_id,
                        "phase": phase,
                        "sceneType": scene_type,
                        "rawScriptSHA1": script_sha1,
                        "rawScript": script_data,
                        "textScript": script_text,
                    }
                )

    with engine.begin() as conn:
        stmt = text("select extname from pg_extension;")
        rows = conn.execute(stmt).fetchall()
        if "pgroonga" not in (row.extname for row in rows):
            conn.execute(text("create extension pgroonga;"))

    with engine.begin() as conn:
        insert_db(conn, ScriptFileList, db_data)


def load_subtitle(
    conn: Connection, region: Region, master_folder: DirectoryPath
) -> None:  # pragma: no cover
    subtitle_json = master_folder / "globalNewMstSubtitle.json"
    if subtitle_json.exists():
        with open(subtitle_json, "rb") as fp:
            globalNewMstSubtitle = orjson.loads(fp.read())

        for subtitle in globalNewMstSubtitle:
            subtitle["svtId"] = get_subtitle_svtId(subtitle["id"])
    else:
        if region == Region.NA:
            logger.warning(f"Can't find file {subtitle_json}.")
        globalNewMstSubtitle = []

    insert_db(conn, mstSubtitle, globalNewMstSubtitle)


def load_pydantic_to_db(
    conn: Connection, pydantic_data: Sequence[BaseModelORJson], db_table: Table
) -> None:  # pragma: no cover
    db_data = [item.dict() for item in pydantic_data]
    insert_db(conn, db_table, db_data)


def load_asset_storage(
    conn: Connection, repo_folder: DirectoryPath
) -> None:  # pragma: no cover
    with open(repo_folder / "AssetStorage.txt", "r", encoding="utf-8") as fp:
        asset_storage = fp.readlines()

    asset_lines: list[AssetStorageLine] = []

    for line in asset_storage:
        if line[0] in ("~", "@"):
            continue
        splitted = line.strip().split(",")
        path_splitted = splitted[4].split("/")
        if len(path_splitted) == 1:
            file_name = path_splitted[0]
            folder = ""
        else:
            file_name = path_splitted[-1]
            folder = "/".join(path_splitted[:-1])
        asset_lines.append(
            AssetStorageLine(
                first=splitted[0],
                required=splitted[1],
                size=int(splitted[2]),
                crc32=int(splitted[3]),
                path=splitted[4],
                folder=folder,
                fileName=file_name,
            )
        )

    load_pydantic_to_db(conn, asset_lines, AssetStorage)


def update_db(region_path: dict[Region, DirectoryPath]) -> None:  # pragma: no cover
    logger.info("Loading db …")
    start_loading_time = time.perf_counter()

    for region, repo_folder in region_path.items():
        logger.info(f"Updating {region} tables …")
        master_folder = repo_folder / "master"
        engine = engines[region]

        with engine.begin() as conn:
            logger.info("Updating parsed skill and td …")
            load_skill_td_lv(conn, repo_folder)

        with engine.begin() as conn:
            logger.info("Updating item …")
            load_item(conn, repo_folder)

        with engine.begin() as conn:
            logger.info("Updating gift …")
            load_gift(conn, repo_folder)

        for table_group in TABLES_TO_BE_LOADED:
            with engine.begin() as conn:
                for table in table_group:
                    table_json = master_folder / f"{table.name}.json"
                    if table_json.exists():
                        with open(table_json, "rb") as fp:
                            data: list[dict[str, Any]] = orjson.loads(fp.read())

                        if data:
                            different_columns = diff_column_schemas(data, table)
                            if different_columns:
                                logger.warning(
                                    f"Found unknown columns: {', '.join(different_columns)} in {table_json}"
                                )
                                data = remove_unknown_columns(data, table)
                    else:
                        data = []

                    logger.debug(f"Updating {table.name} …")
                    insert_db(conn, table, data)

        with engine.begin() as conn:
            logger.info("Updating subtitle …")
            load_subtitle(conn, region, master_folder)

        with engine.begin() as conn:
            logger.info("Updating event …")
            load_event(conn, repo_folder)

        with engine.begin() as conn:
            logger.info("Updated AssetStorage …")
            load_asset_storage(conn, repo_folder)

        logger.info("Updating script list …")
        load_script_list(engine, region, repo_folder)

        with engine.begin() as conn:
            rayshiftQuest.create(conn, checkfirst=True)
            rayshiftQuestHash.create(conn, checkfirst=True)

    db_loading_time = time.perf_counter() - start_loading_time
    logger.info(f"Loaded db in {db_loading_time:.2f}s.")


def load_rayshift_quest_list(region: Region, quest_list: list[QuestList]) -> None:
    with engines[region].begin() as conn:
        rayshiftQuest.create(conn, checkfirst=True)
        insert_rayshift_quest_list(conn, quest_list)


def get_missing_query_ids(
    region: Region, quest_ids: Optional[list[int]] = None
) -> list[int]:
    with engines[region].connect() as conn:
        query_ids = fetch_missing_quest_ids(conn, quest_ids)
    return query_ids


def get_all_missing_query_ids(
    region: Region, quest_ids: Optional[list[int]] = None
) -> list[int]:
    with engines[region].connect() as conn:
        query_ids = fetch_all_missing_quest_ids(conn, quest_ids)
    return query_ids


def load_rayshift_quest_details(
    region: Region, quest_details: dict[int, QuestDetail]
) -> None:
    with engines[region].begin() as conn:
        insert_rayshift_quest_db_sync(conn, quest_details)
        insert_rayshift_quest_hash_db_sync(conn, quest_details)
