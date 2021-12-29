import asyncio
import time
from pathlib import Path
from typing import Any, Iterable, Union

import aiofiles
import orjson
from aioredis import Redis
from fastapi.concurrency import run_in_threadpool
from git import Repo  # type: ignore
from pydantic import DirectoryPath
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from .core.nice.event import get_nice_event
from .core.nice.war import get_nice_war

from .config import Settings, logger, project_root
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
from .core.nice.mm import get_all_nice_mms
from .core.nice.nice import get_nice_equip_model, get_nice_servant_model
from .core.raw import get_all_bgm_entities, get_servant_entity
from .core.utils import get_translation, sort_by_collection_no
from .data.extra import get_extra_svt_data
from .db.engine import engines
from .db.helpers import fetch
from .db.helpers.svt import get_all_equips, get_all_servants
from .db.load import load_pydantic_to_db, update_db
from .models.raw import mstSvtExtra
from .redis.helpers.repo_version import set_repo_version
from .redis.load import load_redis_data, load_svt_extra_redis
from .routers.utils import list_string
from .schemas.base import BaseModelORJson
from .schemas.common import Language, Region, RepoInfo
from .schemas.enums import ALL_ENUMS, TRAIT_NAME
from .schemas.gameenums import SvtType
from .schemas.nice import NiceEquip, NiceServant
from .schemas.raw import (
    MstCommandCode,
    MstCv,
    MstEquip,
    MstEvent,
    MstIllustrator,
    MstItem,
    MstMasterMission,
    MstSvt,
    MstWar,
    ServantEntity,
)


settings = Settings()


export_path = project_root / "export"


async def dump_normal(
    base_export_path: Path, file_name: str, data: Any
) -> None:  # pragma: no cover
    async with aiofiles.open(base_export_path / f"{file_name}.json", "wb") as fp:
        await fp.write(orjson.dumps(data, option=orjson.OPT_NON_STR_KEYS))


async def dump_orjson(
    base_export_path: Path, file_name: str, data: Iterable[BaseModelORJson]
) -> None:  # pragma: no cover
    async with aiofiles.open(
        base_export_path / f"{file_name}.json", "w", encoding="utf-8"
    ) as fp:
        await fp.write(list_string(data))


async def get_nice_svt(
    conn: AsyncConnection,
    region: Region,
    lang: Language,
    lore: bool,
    raw_svt: ServantEntity,
) -> Union[NiceServant, NiceEquip]:  # pragma: no cover
    if raw_svt.mstSvt.type == SvtType.SERVANT_EQUIP:
        return await get_nice_equip_model(
            conn=conn,
            region=region,
            item_id=raw_svt.mstSvt.id,
            lang=lang,
            lore=True,
            raw_svt=raw_svt,
        )
    else:
        return await get_nice_servant_model(
            conn=conn,
            region=region,
            item_id=raw_svt.mstSvt.id,
            lang=lang,
            lore=lore,
            raw_svt=raw_svt,
        )


async def dump_svt(
    conn: AsyncConnection,
    region: Region,
    base_export_path: Path,
    file_name: str,
    svts: list[MstSvt],
) -> None:  # pragma: no cover
    with_lore: list[str] = []
    without_lore: list[str] = []
    with_lore_en: list[str] = []
    without_lore_en: list[str] = []

    for svt in svts:
        raw_svt = await get_servant_entity(
            conn, svt.id, expand=True, lore=True, mstSvt=svt
        )

        nice_svt = await get_nice_svt(conn, region, Language.jp, True, raw_svt)
        with_lore.append(nice_svt.json(exclude_unset=True, exclude_none=True))
        without_lore.append(
            nice_svt.json(exclude={"profile"}, exclude_unset=True, exclude_none=True)
        )

        if region == Region.JP:
            nice_svt_en = await get_nice_svt(conn, region, Language.en, True, raw_svt)
            with_lore_en.append(nice_svt_en.json(exclude_unset=True, exclude_none=True))
            without_lore_en.append(
                nice_svt_en.json(
                    exclude={"profile"}, exclude_unset=True, exclude_none=True
                )
            )

    out_name = base_export_path / f"{file_name}.json"
    out_lore_name = base_export_path / f"{file_name}_lore.json"

    async with aiofiles.open(out_lore_name, "w", encoding="utf-8") as fp:
        await fp.write("[" + ",".join(with_lore) + "]")
    async with aiofiles.open(out_name, "w", encoding="utf-8") as fp:
        await fp.write("[" + ",".join(without_lore) + "]")

    if region == Region.JP:
        out_name_en = base_export_path / f"{file_name}_lang_en.json"
        out_lore_name_en = base_export_path / f"{file_name}_lore_lang_en.json"

        async with aiofiles.open(out_lore_name_en, "w", encoding="utf-8") as fp:
            await fp.write("[" + ",".join(with_lore_en) + "]")
        async with aiofiles.open(out_name_en, "w", encoding="utf-8") as fp:
            await fp.write("[" + ",".join(without_lore_en) + "]")


async def generate_exports(
    redis: Redis,
    region_path: dict[Region, DirectoryPath],
    async_engines: dict[Region, AsyncEngine],
) -> None:  # pragma: no cover
    if settings.export_all_nice:
        for region in region_path:
            start_time = time.perf_counter()
            async with async_engines[region].connect() as conn:
                logger.info(f"Exporting {region} data …")

                all_servants = await get_all_servants(conn)
                all_equips = await get_all_equips(conn)
                bgms = await get_all_bgm_entities(conn)

                mstItems = await fetch.get_everything(conn, MstItem)
                mstIllustrators = await fetch.get_everything(conn, MstIllustrator)
                mstCvs = await fetch.get_everything(conn, MstCv)
                mstEvents = await fetch.get_everything(conn, MstEvent)
                mstWars = await fetch.get_everything(conn, MstWar)
                mstEquips = await fetch.get_everything(conn, MstEquip)
                mstCcs = await fetch.get_everything(conn, MstCommandCode)
                mstMasterMissions = await fetch.get_everything(conn, MstMasterMission)

                all_item_data = get_all_nice_items(region, Language.jp, mstItems)
                all_mc_data = await get_all_nice_mcs(
                    conn, region, Language.jp, mstEquips
                )
                all_cc_data = await get_all_nice_ccs(conn, region, Language.jp, mstCcs)
                all_bgm_data = get_all_nice_bgms(region, Language.jp, bgms)
                all_mm_data = await get_all_nice_mms(
                    conn, mstMasterMissions, Language.jp
                )
                all_event_data = [
                    await get_nice_event(conn, region, event.id, Language.jp)
                    for event in mstEvents
                ]
                all_war_data = [
                    await get_nice_war(conn, region, war.id, Language.jp)
                    for war in mstWars
                ]

                all_basic_servant_data = sort_by_collection_no(
                    await get_all_basic_servants(
                        redis, region, Language.jp, all_servants
                    )
                )
                all_basic_equip_data = sort_by_collection_no(
                    await get_all_basic_equips(redis, region, Language.jp, all_equips)
                )
                all_basic_mc_data = get_all_basic_mcs(region, Language.jp, mstEquips)
                all_basic_cc_data = sort_by_collection_no(
                    get_all_basic_ccs(region, Language.jp, mstCcs)
                )
                all_basic_event_data = get_all_basic_events(Language.jp, mstEvents)
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
                    ("nice_master_mission", all_mm_data, dump_orjson),
                    ("nice_bgm", all_bgm_data, dump_orjson),
                    ("nice_illustrator", mstIllustrators, dump_orjson),
                    ("nice_cv", mstCvs, dump_orjson),
                    ("nice_event", all_event_data, dump_orjson),
                    ("nice_war", all_war_data, dump_orjson),
                ]

                if region == Region.JP:
                    all_item_data_en = get_all_nice_items(region, Language.en, mstItems)
                    all_bgm_data_en = get_all_nice_bgms(region, Language.en, bgms)
                    all_cc_data_en = await get_all_nice_ccs(
                        conn, region, Language.en, mstCcs
                    )
                    all_mc_data_en = await get_all_nice_mcs(
                        conn, region, Language.en, mstEquips
                    )
                    all_event_data_en = [
                        await get_nice_event(conn, region, event.id, Language.en)
                        for event in mstEvents
                    ]
                    all_war_data_en = [
                        await get_nice_war(conn, region, war.id, Language.en)
                        for war in mstWars
                    ]

                    all_basic_servant_en = sort_by_collection_no(
                        await get_all_basic_servants(
                            redis, region, Language.en, all_servants
                        )
                    )
                    all_basic_equip_en = sort_by_collection_no(
                        await get_all_basic_equips(
                            redis, region, Language.en, all_equips
                        )
                    )
                    all_basic_cc_en = sort_by_collection_no(
                        get_all_basic_ccs(region, Language.en, mstCcs)
                    )
                    all_basic_mc_en = get_all_basic_mcs(region, Language.en, mstEquips)
                    all_basic_event_en = get_all_basic_events(Language.en, mstEvents)
                    all_basic_war_en = get_all_basic_wars(Language.en, mstWars)

                    mstIllustrators_en: list[MstIllustrator] = []
                    for illustrator in mstIllustrators:
                        illustrator_en = illustrator.copy()
                        illustrator_en.name = get_translation(
                            Language.en, illustrator_en.name
                        )
                        mstIllustrators_en.append(illustrator_en)

                    mstCvs_en: list[MstCv] = []
                    for cv in mstCvs:
                        cv_en = cv.copy()
                        cv_en.name = get_translation(Language.en, cv_en.name)
                        mstCvs_en.append(cv_en)

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
                        ("nice_illustrator_lang_en", mstIllustrators_en, dump_orjson),
                        ("nice_cv_lang_en", mstCvs_en, dump_orjson),
                        ("nice_event_lang_en", all_event_data_en, dump_orjson),
                        ("nice_war_lang_en", all_war_data_en, dump_orjson),
                    ] + output_files

                base_export_path = export_path / region.value

                for file_name, data, dump in output_files:
                    await dump(base_export_path, file_name, data)

                await dump_svt(
                    conn, region, base_export_path, "nice_servant", all_servants
                )
                await dump_svt(conn, region, base_export_path, "nice_equip", all_equips)

            run_time = time.perf_counter() - start_time
            logger.info(f"Exported {region} data in {run_time:.2f}s.")


async def update_master_repo_info(
    redis: Redis, region_path: dict[Region, DirectoryPath]
) -> None:
    for region, gamedata in region_path.items():
        if (gamedata / ".git").exists():
            repo = Repo(gamedata)
            latest_commit = repo.commit()
            repo_info = RepoInfo(
                hash=latest_commit.hexsha[:6],
                timestamp=latest_commit.committed_date,  # pyright: reportGeneralTypeIssues=false
            )
            await set_repo_version(redis, region, repo_info)


async def clear_bloom_redis_cache(redis: Redis) -> None:  # pragma: no cover
    key_count = 0
    async for key in redis.scan_iter(match=f"{settings.redis_prefix}:cache*"):
        await redis.delete(key)
        key_count += 1
    logger.info(f"Cleared {key_count} cache redis keys.")


async def load_svt_extra(
    redis: Redis, region_path: dict[Region, DirectoryPath]
) -> None:  # pragma: no cover
    logger.info("Loading extra svt data …")
    start_loading_time = time.perf_counter()

    for region, gamedata_path in region_path.items():
        svtExtras = get_extra_svt_data(region, gamedata_path)
        if settings.write_postgres_data:
            with engines[region].begin() as conn:
                load_pydantic_to_db(conn, svtExtras, mstSvtExtra)
        if settings.write_redis_data:
            await load_svt_extra_redis(redis, region, svtExtras)

    extra_loading_time = time.perf_counter() - start_loading_time
    logger.info(f"Loaded extra svt data in {extra_loading_time:.2f}s.")


async def load_and_export(
    redis: Redis,
    region_path: dict[Region, DirectoryPath],
    async_engines: dict[Region, AsyncEngine],
) -> None:  # pragma: no cover
    if settings.write_postgres_data:
        update_db(region_path)
    if settings.write_redis_data:
        await load_redis_data(redis, region_path)
    if settings.write_postgres_data or settings.write_redis_data:
        await load_svt_extra(redis, region_path)
    await update_master_repo_info(redis, region_path)
    if settings.clear_redis_cache:
        await clear_bloom_redis_cache(redis)
    await generate_exports(redis, region_path, async_engines)


def update_data_repo(
    region_path: dict[Region, DirectoryPath]
) -> None:  # pragma: no cover
    if settings.github_webhook_git_pull:
        for gamedata in region_path.values():
            if (gamedata / ".git").exists():
                repo = Repo(gamedata)
                for fetch_info in repo.remotes[0].pull():
                    commit_hash = fetch_info.commit.hexsha[:6]
                    logger.info(f"Updated {fetch_info.ref} to {commit_hash}")


async def pull_and_update(
    region_path: dict[Region, DirectoryPath],
    async_engines: dict[Region, AsyncEngine],
    redis: Redis,
) -> None:  # pragma: no cover
    logger.info(f"Sleeping {settings.github_webhook_sleep} seconds …")
    await asyncio.sleep(settings.github_webhook_sleep)
    await run_in_threadpool(lambda: update_data_repo(region_path))
    await load_and_export(redis, region_path, async_engines)
