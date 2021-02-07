import time
from typing import Dict

import orjson
from pydantic import DirectoryPath
from sqlalchemy import Table
from sqlalchemy.engine import Engine
from sqlalchemy.sql import text

from ..config import logger
from ..models.raw import TABLES_TO_BE_LOADED, mstSubtitle, mstSvtVoice
from ..schemas.common import Region
from ..schemas.raw import get_subtitle_svtId
from .base import engines


def recreate_table(engine: Engine, table: Table) -> None:  # pragma: no cover
    table.drop(engine, checkfirst=True)
    table.create(engine, checkfirst=True)


def update_db(region_path: Dict[Region, DirectoryPath]) -> None:  # pragma: no cover
    logger.info("Loading db …")
    start_loading_time = time.perf_counter()
    for region_name, gamedata in region_path.items():
        engine = engines[region_name]

        with engine.connect() as conn:
            for table in TABLES_TO_BE_LOADED:
                table_json = gamedata / f"{table.name}.json"
                if table_json.exists():
                    with open(table_json, "rb") as fp:
                        data = orjson.loads(fp.read())
                    recreate_table(engine, table)
                    conn.execute(table.insert(data))

                    if table is mstSvtVoice:
                        conn.execute(text('DROP INDEX IF EXISTS "mstSvtVoiceGIN"'))
                        conn.execute(
                            text(
                                'CREATE INDEX "mstSvtVoiceGIN" ON "mstSvtVoice" '
                                'USING gin("scriptJson" jsonb_path_ops)'
                            )
                        )

            recreate_table(engine, mstSubtitle)
            subtitle_json = gamedata / "globalNewMstSubtitle.json"
            if subtitle_json.exists():
                with open(subtitle_json, "rb") as fp:
                    globalNewMstSubtitle = orjson.loads(fp.read())
                for subtitle in globalNewMstSubtitle:
                    subtitle["svtId"] = get_subtitle_svtId(subtitle["id"])
                conn.execute(mstSubtitle.insert(globalNewMstSubtitle))

    db_loading_time = time.perf_counter() - start_loading_time
    logger.info(f"Loaded db in {db_loading_time:.2f}s.")
