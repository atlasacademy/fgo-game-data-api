import time
from collections import defaultdict
from typing import Any

import orjson
from pydantic import DirectoryPath
from sqlalchemy import Table
from sqlalchemy.engine import Connection

from ..config import logger
from ..models.raw import (
    TABLES_TO_BE_LOADED,
    mstSkillLv,
    mstSubtitle,
    mstTreasureDeviceLv,
)
from ..models.rayshift import rayshiftQuest
from ..rayshift.quest import get_all_quest_lists
from ..schemas.common import Region
from ..schemas.enums import FUNC_VALS_NOT_BUFF
from ..schemas.raw import get_subtitle_svtId
from .engine import engines
from .helpers.rayshift import insert_rayshift_quest_list


def recreate_table(conn: Connection, table: Table) -> None:  # pragma: no cover
    table.drop(conn, checkfirst=True)
    table.create(conn, checkfirst=True)


def check_known_columns(
    data: list[dict[str, Any]], table: Table
) -> bool:  # pragma: no cover
    table_columns = {column.name for column in table.columns}
    return set(data[0].keys()).issubset(table_columns)


def remove_unknown_columns(
    data: list[dict[str, Any]], table: Table
) -> list[dict[str, Any]]:  # pragma: no cover
    table_columns = {column.name for column in table.columns}
    return [{k: v for k, v in item.items() if k in table_columns} for item in data]


def load_skill_td_lv(conn: Connection, master_folder: DirectoryPath) -> None:
    with open(master_folder / "mstBuff.json", "rb") as fp:
        mstBuff = {buff["id"]: buff for buff in orjson.loads(fp.read())}

    with open(master_folder / "mstFunc.json", "rb") as fp:
        mstFunc = {func["id"]: func for func in orjson.loads(fp.read())}

    mstFuncGroup = defaultdict(list)
    with open(master_folder / "mstFuncGroup.json", "rb") as fp:
        for funcGroup in orjson.loads(fp.read()):
            mstFuncGroup[funcGroup["funcId"]].append(funcGroup)

    with open(master_folder / "mstSkillLv.json", "rb") as fp:
        mstSkillLv_data = orjson.loads(fp.read())

    with open(master_folder / "mstTreasureDeviceLv.json", "rb") as fp:
        mstTreasureDeviceLv_data = orjson.loads(fp.read())

    def get_func_entity(func_id: int) -> dict[Any, Any]:
        func_entity = {
            "mstFunc": mstFunc[func_id],
            "mstFuncGroup": mstFuncGroup.get(func_id, []),
        }

        if (
            func_entity["mstFunc"]["funcType"] not in FUNC_VALS_NOT_BUFF
            and func_entity["mstFunc"]["vals"]
            and func_entity["mstFunc"]["vals"][0] in mstBuff
        ):
            func_entity["mstFunc"]["expandedVals"] = [
                {"mstBuff": mstBuff[func_entity["mstFunc"]["vals"][0]]}
            ]
        else:
            func_entity["mstFunc"]["expandedVals"] = []

        return func_entity

    for skillLv in mstSkillLv_data:
        skillLv["expandedFuncId"] = [
            get_func_entity(func_id)
            for func_id in skillLv["funcId"]
            if func_id in mstFunc
        ]

    recreate_table(conn, mstSkillLv)
    conn.execute(mstSkillLv.insert(), mstSkillLv_data)

    for treasureDeviceLv in mstTreasureDeviceLv_data:
        treasureDeviceLv["expandedFuncId"] = [
            get_func_entity(func_id)
            for func_id in treasureDeviceLv["funcId"]
            if func_id in mstFunc
        ]

    recreate_table(conn, mstTreasureDeviceLv)
    conn.execute(mstTreasureDeviceLv.insert(), mstTreasureDeviceLv_data)


def update_db(region_path: dict[Region, DirectoryPath]) -> None:  # pragma: no cover
    logger.info("Loading db …")
    start_loading_time = time.perf_counter()

    for region, master_folder in region_path.items():
        engine = engines[region]

        for table in TABLES_TO_BE_LOADED:
            table_json = master_folder / f"{table.name}.json"
            if table_json.exists():
                with open(table_json, "rb") as fp:
                    data: list[dict[str, Any]] = orjson.loads(fp.read())

                if len(data) > 0 and not check_known_columns(data, table):
                    logger.warning(f"Found unknown columns in {table_json}")
                    data = remove_unknown_columns(data, table)
            else:
                logger.warning(f"Can't find file {table_json}.")
                data = []

            with engine.begin() as conn:
                recreate_table(conn, table)
                conn.execute(table.insert(), data)

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

        with engine.begin() as conn:
            recreate_table(conn, mstSubtitle)
            conn.execute(mstSubtitle.insert(), globalNewMstSubtitle)

        with engine.begin() as conn:
            load_skill_td_lv(conn, master_folder)

        with engine.begin() as conn:
            rayshiftQuest.create(conn, checkfirst=True)

    db_loading_time = time.perf_counter() - start_loading_time
    logger.info(f"Loaded db in {db_loading_time:.2f}s.")


def load_rayshift_quest_list(region: Region) -> None:
    print(f"Loading {region} rayshift data cache …")
    start_loading_time = time.perf_counter()

    quest_list = get_all_quest_lists(region)

    print(f"Inserting {region} rayshift data cache into db …")
    with engines[region].begin() as conn:
        rayshiftQuest.create(conn, checkfirst=True)
        insert_rayshift_quest_list(conn, quest_list)

    rayshift_load_time = time.perf_counter() - start_loading_time
    print(f"Loaded {region} rayshift {rayshift_load_time:.2f}s.")
