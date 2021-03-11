import time
from typing import Any

import orjson
from pydantic import DirectoryPath
from sqlalchemy import Table
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Connection

from ..config import logger
from ..models.raw import TABLES_TO_BE_LOADED, TABLES_WITH_PK, mstSubtitle
from ..models.rayshift import rayshiftQuest
from ..rayshift.quest import get_all_quest_lists
from ..schemas.common import Region
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


def update_db(region_path: dict[Region, DirectoryPath]) -> None:  # pragma: no cover
    logger.info("Loading db …")
    start_loading_time = time.perf_counter()

    for region, master_folder in region_path.items():
        engine = engines[region]

        for table in TABLES_WITH_PK:
            table_json = master_folder / f"{table.name}.json"
            with engine.begin() as conn:
                # TODO: Check the table schema if it's different and recreate the table if needed
                table.create(conn, checkfirst=True)
                if table_json.exists():
                    with open(table_json, "rb") as fp:
                        id_data: list[dict[str, Any]] = orjson.loads(fp.read())

                    insert_stmt = insert(table)
                    do_update_stmt = insert_stmt.on_conflict_do_update(
                        index_elements=[col for col in table.c if col.primary_key],
                        set_=insert_stmt.excluded,
                    )
                    conn.execute(do_update_stmt, id_data)

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
