import asyncio
import json
import time
from pathlib import Path
from typing import Any, Iterable

from aioredis import Redis
from git import Repo
from pydantic import DirectoryPath
from sqlalchemy.engine import Connection

from app.schemas.gameenums import SvtType

from .config import SecretSettings, Settings, logger, project_root
from .core.basic import (
    get_all_basic_ccs,
    get_all_basic_equips,
    get_all_basic_events,
    get_all_basic_mcs,
    get_all_basic_servants,
    get_all_basic_wars,
)
from .core.nice.bgm import get_all_nice_bgms
from .core.nice.cc import get_all_nice_ccs
from .core.nice.item import get_all_nice_items
from .core.nice.mc import get_all_nice_mcs
from .core.nice.nice import get_nice_equip_model, get_nice_servant_model
from .core.raw import get_all_bgm_entities, get_all_raw_svts_lore
from .core.utils import sort_by_collection_no
from .data.gamedata import update_masters
from .db.engine import engines
from .db.helpers import fetch
from .db.helpers.svt import get_all_equips, get_all_servants
from .db.load import update_db
from .redis.load import load_redis_data
from .routers.utils import list_string
from .schemas.base import BaseModelORJson
from .schemas.common import Language, Region, RepoInfo
from .schemas.enums import ALL_ENUMS, TRAIT_NAME
from .schemas.raw import (
    MstCommandCode,
    MstCv,
    MstEquip,
    MstEvent,
    MstIllustrator,
    MstItem,
    MstSvt,
    MstWar,
)


settings = Settings()
secrets = SecretSettings()
REGION_PATHS = {Region.JP: settings.jp_gamedata, Region.NA: settings.na_gamedata}


export_path = project_root / "export"


def dump_normal(
    base_export_path: Path, file_name: str, data: Any
) -> None:  # pragma: no cover
    with open(base_export_path / f"{file_name}.json", "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False)


def dump_orjson(
    base_export_path: Path, file_name: str, data: Iterable[BaseModelORJson]
) -> None:  # pragma: no cover
    with open(base_export_path / f"{file_name}.json", "w", encoding="utf-8") as fp:
        fp.write(list_string(data))


def dump_svt(
    conn: Connection,
    region: Region,
    base_export_path: Path,
    file_name: str,
    svts: list[MstSvt],
) -> None:  # pragma: no cover
    file_name = "nice_equip" if svts[0].type == SvtType.SERVANT_EQUIP else "nice_equip"

    export_with_lore = "["
    export_without_lore = "["
    export_with_lore_en = "["
    export_without_lore_en = "["

    raw_svts = get_all_raw_svts_lore(conn, svts)
    for raw_svt in raw_svts:
        nice_params = {
            "conn": conn,
            "region": region,
            "item_id": raw_svt.mstSvt.id,
            "lang": Language.jp,
            "lore": True,
            "raw_svt": raw_svt,
        }
        if raw_svt.mstSvt.type == SvtType.SERVANT_EQUIP:
            nice_svt = get_nice_equip_model(**nice_params)  # type: ignore
        else:
            nice_svt = get_nice_servant_model(**nice_params)  # type: ignore
        export_with_lore += nice_svt.json(exclude_unset=True, exclude_none=True)
        export_without_lore += nice_svt.json(
            exclude_unset=True, exclude_none=True, exclude={"profile"}
        )
        export_with_lore += ","
        export_without_lore += ","

        if region == Region.JP:
            nice_params["lang"] = Language.en
            if raw_svt.mstSvt.type == SvtType.SERVANT_EQUIP:
                nice_svt_en = get_nice_equip_model(**nice_params)  # type: ignore
            else:
                nice_svt_en = get_nice_servant_model(**nice_params)  # type: ignore
            export_with_lore_en += nice_svt_en.json(
                exclude_unset=True, exclude_none=True
            )
            export_without_lore_en += nice_svt_en.json(
                exclude_unset=True, exclude_none=True, exclude={"profile"}
            )
            export_with_lore_en += ","
            export_without_lore_en += ","

    export_with_lore = export_with_lore.removesuffix(",") + "]"
    export_without_lore = export_without_lore.removesuffix(",") + "]"
    export_with_lore_en = export_with_lore_en.removesuffix(",") + "]"
    export_without_lore_en = export_without_lore_en.removesuffix(",") + "]"

    out_name = base_export_path / f"{file_name}.json"
    out_lore_name = base_export_path / f"{file_name}_lore.json"

    with open(out_lore_name, "w", encoding="utf-8") as fp:
        fp.write(export_with_lore)
    with open(out_name, "w", encoding="utf-8") as fp:
        fp.write(export_without_lore)

    if region == Region.JP:
        out_name_en = base_export_path / f"{file_name}_lang_en.json"
        out_lore_name_en = base_export_path / f"{file_name}_lore_lang_en.json"

        with open(out_lore_name_en, "w", encoding="utf-8") as fp:
            fp.write(export_with_lore_en)
        with open(out_name_en, "w", encoding="utf-8") as fp:
            fp.write(export_without_lore_en)


async def generate_exports(
    redis: Redis, region_path: dict[Region, DirectoryPath]
) -> None:  # pragma: no cover
    if settings.export_all_nice:
        for region in region_path:
            start_time = time.perf_counter()
            conn = engines[region].connect()
            logger.info(f"Exporting {region} data …")

            all_servants = get_all_servants(conn)
            all_equips = get_all_equips(conn)
            bgms = get_all_bgm_entities(conn)

            mstItems = fetch.get_everything(conn, MstItem)
            mstIllustrators = fetch.get_everything(conn, MstIllustrator)
            mstCvs = fetch.get_everything(conn, MstCv)
            mstEvents = fetch.get_everything(conn, MstEvent)
            mstWars = fetch.get_everything(conn, MstWar)
            mstEquips = fetch.get_everything(conn, MstEquip)
            mstCcs = fetch.get_everything(conn, MstCommandCode)

            all_item_data = get_all_nice_items(region, Language.jp, mstItems)
            all_mc_data = get_all_nice_mcs(conn, region, Language.jp, mstEquips)
            all_cc_data = get_all_nice_ccs(conn, region, Language.jp, mstCcs)
            all_bgm_data = get_all_nice_bgms(conn, region, Language.jp, bgms)

            all_basic_servant_data = sort_by_collection_no(
                await get_all_basic_servants(redis, region, Language.jp, all_servants)
            )
            all_basic_equip_data = sort_by_collection_no(
                await get_all_basic_equips(redis, region, Language.jp, all_equips)
            )
            all_basic_mc_data = get_all_basic_mcs(region, Language.jp, mstEquips)
            all_basic_cc_data = sort_by_collection_no(
                get_all_basic_ccs(region, Language.jp, mstCcs)
            )
            all_basic_event_data = get_all_basic_events(region, Language.jp, mstEvents)
            all_basic_war_data = get_all_basic_wars(Language.jp, mstWars)

            output_files = [
                ("basic_servant", all_basic_servant_data, dump_orjson),
                ("basic_equip", all_basic_equip_data, dump_orjson),
                ("basic_mystic_code", all_basic_mc_data, dump_orjson),
                ("basic_command_code", all_basic_cc_data, dump_orjson),
                ("basic_event", all_basic_event_data, dump_orjson),
                ("basic_war", all_basic_war_data, dump_orjson),
                ("nice_enums", ALL_ENUMS, dump_normal),
                ("nice_trait", TRAIT_NAME, dump_normal),
                ("nice_command_code", all_cc_data, dump_orjson),
                ("nice_item", all_item_data, dump_orjson),
                ("nice_mystic_code", all_mc_data, dump_orjson),
                ("nice_bgm", all_bgm_data, dump_orjson),
                ("nice_illustrator", mstIllustrators, dump_orjson),
                ("nice_cv", mstCvs, dump_orjson),
            ]

            if region == Region.JP:
                all_item_data_en = get_all_nice_items(region, Language.en, mstItems)
                all_bgm_data_en = get_all_nice_bgms(conn, region, Language.en, bgms)
                all_cc_data_en = get_all_nice_ccs(conn, region, Language.en, mstCcs)
                all_mc_data_en = get_all_nice_mcs(conn, region, Language.en, mstEquips)

                all_basic_servant_en = sort_by_collection_no(
                    await get_all_basic_servants(
                        redis, region, Language.en, all_servants
                    )
                )
                all_basic_equip_en = sort_by_collection_no(
                    await get_all_basic_equips(redis, region, Language.en, all_equips)
                )
                all_basic_cc_en = sort_by_collection_no(
                    get_all_basic_ccs(region, Language.en, mstCcs)
                )
                all_basic_mc_en = get_all_basic_mcs(region, Language.en, mstEquips)
                all_basic_event_en = get_all_basic_events(
                    region, Language.en, mstEvents
                )
                all_basic_war_en = get_all_basic_wars(Language.en, mstWars)

                output_files = [
                    ("basic_servant_lang_en", all_basic_servant_en, dump_orjson),
                    ("basic_equip_lang_en", all_basic_equip_en, dump_orjson),
                    ("basic_event_lang_en", all_basic_event_en, dump_orjson),
                    ("basic_war_lang_en", all_basic_war_en, dump_orjson),
                    ("basic_command_code_lang_en", all_basic_cc_en, dump_orjson),
                    ("nice_command_code_lang_en", all_cc_data_en, dump_orjson),
                    ("nice_item_lang_en", all_item_data_en, dump_orjson),
                    ("basic_mystic_code_lang_en", all_basic_mc_en, dump_orjson),
                    ("nice_mystic_code_lang_en", all_mc_data_en, dump_orjson),
                    ("nice_bgm_lang_en", all_bgm_data_en, dump_orjson),
                ] + output_files

            base_export_path = export_path / region.value

            for file_name, data, dump in output_files:
                dump(base_export_path, file_name, data)

            dump_svt(
                conn,
                region,
                base_export_path,
                "nice_servant",
                all_servants,
            )
            dump_svt(
                conn,
                region,
                base_export_path,
                "nice_equip",
                all_equips,
            )

            conn.close()

            run_time = time.perf_counter() - start_time
            logger.info(f"Exported {region} data in {run_time:.2f}s.")


repo_info: dict[Region, RepoInfo] = {}


def update_master_repo_info(region_path: dict[Region, DirectoryPath]) -> None:
    for region, gamedata in region_path.items():
        if (gamedata / ".git").exists():
            repo = Repo(gamedata)
            latest_commit = repo.commit()
            repo_info[region] = RepoInfo(
                hash=latest_commit.hexsha[:6],
                timestamp=latest_commit.committed_date,  # pyright: reportGeneralTypeIssues=false
            )


async def clear_bloom_redis_cache(redis: Redis) -> None:  # pragma: no cover
    # If DEL doesn't work with the redis setup, consider calling bloom instead of redis.
    # https://github.com/valeriansaliou/bloom#can-cache-be-programatically-expired
    # The hash for bucket name "fgo-game-data-api" is "92b89e16"
    if settings.bloom_shard is not None:
        key_count = 0
        async for key in redis.iscan(match=f"bloom:{settings.bloom_shard}:c:*"):
            await redis.delete(key)
            key_count += 1
        logger.info(f"Cleared {key_count} bloom redis keys.")


async def load_and_export(
    redis: Redis, region_path: dict[Region, DirectoryPath]
) -> None:  # pragma: no cover
    if settings.write_postgres_data:
        update_db(region_path)
    if settings.write_redis_data:
        await load_redis_data(redis, region_path)
    update_masters(region_path)
    await generate_exports(redis, region_path)
    update_master_repo_info(region_path)
    await clear_bloom_redis_cache(redis)


async def pull_and_update(
    redis: Redis, region_path: dict[Region, DirectoryPath]
) -> None:  # pragma: no cover
    logger.info(f"Sleeping {settings.github_webhook_sleep} seconds …")
    await asyncio.sleep(settings.github_webhook_sleep)
    if settings.github_webhook_git_pull:
        for gamedata in region_path.values():
            if (gamedata / ".git").exists():
                repo = Repo(gamedata)
                for fetch_info in repo.remotes[0].pull():
                    commit_hash = fetch_info.commit.hexsha[:6]
                    logger.info(f"Updated {fetch_info.ref} to {commit_hash}")
    await load_and_export(redis, region_path)
