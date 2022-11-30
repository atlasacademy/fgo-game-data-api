import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Union

import aiofiles
import httpx
import orjson
from fastapi.concurrency import run_in_threadpool
from git import Repo  # type: ignore
from pydantic import DirectoryPath
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

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
from .core.nice.event.event import get_nice_event
from .core.nice.event.shop import get_nice_shops_from_raw
from .core.nice.item import get_all_nice_items
from .core.nice.mc import get_all_nice_mcs
from .core.nice.mm import get_all_nice_mms
from .core.nice.nice import get_nice_equip_model, get_nice_servant_model
from .core.nice.war import get_nice_war
from .core.raw import get_all_bgm_entities, get_servant_entity
from .core.utils import get_translation
from .data.extra import get_extra_svt_data
from .db.engine import engines
from .db.helpers import fetch
from .db.helpers.svt import get_all_equips
from .db.load import load_pydantic_to_db, update_db
from .models.raw import mstSvtExtra
from .redis import Redis
from .redis.helpers.repo_version import get_repo_version, set_repo_version
from .redis.load import load_redis_data, load_svt_extra_redis
from .routers.utils import list_string
from .schemas.base import BaseModelORJson
from .schemas.common import Language, Region, RepoInfo
from .schemas.enums import ALL_ENUMS, TRAIT_NAME
from .schemas.gameenums import SvtType
from .schemas.nice import NiceEquip, NiceServant
from .schemas.raw import (
    AssetStorageLine,
    BgmEntity,
    MstCommandCode,
    MstCv,
    MstEquip,
    MstEvent,
    MstIllustrator,
    MstItem,
    MstMasterMission,
    MstShop,
    MstSvt,
    MstWar,
    ServantEntity,
)


settings = Settings()


async def dump_normal(
    export_path: Path, file_name: str, data: Any
) -> None:  # pragma: no cover
    async with aiofiles.open(export_path / f"{file_name}.json", "wb") as fp:
        await fp.write(orjson.dumps(data, option=orjson.OPT_NON_STR_KEYS))


async def dump_orjson(
    export_path: Path, file_name: str, data: Iterable[BaseModelORJson]
) -> None:  # pragma: no cover
    async with aiofiles.open(
        export_path / f"{file_name}.json", "w", encoding="utf-8"
    ) as fp:
        await fp.write(list_string(data))


@dataclass
class ExportUtil:
    conn: AsyncConnection
    redis: Redis
    region: Region
    export_path: Path
    lang: Language = Language.jp

    def append_file_name(self, file_name: str) -> str:  # pragma: no cover
        if self.lang == Language.en:
            return file_name + "_lang_en"
        return file_name

    async def dump_orjson(
        self, file_name: str, data: Iterable[BaseModelORJson]
    ) -> None:  # pragma: no cover
        await dump_orjson(self.export_path, self.append_file_name(file_name), data)


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
    util: ExportUtil, file_name: str, svts: list[MstSvt]
) -> None:  # pragma: no cover
    conn = util.conn
    region = util.region
    export_path = util.export_path

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

    out_name = export_path / f"{file_name}.json"
    out_lore_name = export_path / f"{file_name}_lore.json"

    async with aiofiles.open(out_lore_name, "w", encoding="utf-8") as fp:
        await fp.write("[" + ",".join(with_lore) + "]")
    async with aiofiles.open(out_name, "w", encoding="utf-8") as fp:
        await fp.write("[" + ",".join(without_lore) + "]")

    if region == Region.JP:
        out_name_en = export_path / f"{file_name}_lang_en.json"
        out_lore_name_en = export_path / f"{file_name}_lore_lang_en.json"

        async with aiofiles.open(out_lore_name_en, "w", encoding="utf-8") as fp:
            await fp.write("[" + ",".join(with_lore_en) + "]")
        async with aiofiles.open(out_name_en, "w", encoding="utf-8") as fp:
            await fp.write("[" + ",".join(without_lore_en) + "]")


async def dump_nice_items(
    util: ExportUtil, items: list[MstItem]
) -> None:  # pragma: no cover
    all_item_data = get_all_nice_items(util.region, util.lang, items)
    await util.dump_orjson("nice_item", all_item_data)


async def dump_nice_ccs(
    util: ExportUtil, ccs: list[MstCommandCode]
) -> None:  # pragma: no cover
    all_cc_data = await get_all_nice_ccs(util.conn, util.region, util.lang, ccs)
    await util.dump_orjson("nice_command_code", all_cc_data)


async def dump_nice_mcs(
    util: ExportUtil, mcs: list[MstEquip]
) -> None:  # pragma: no cover
    all_mc_data = await get_all_nice_mcs(util.conn, util.region, util.lang, mcs)
    await util.dump_orjson("nice_mystic_code", all_mc_data)


async def dump_nice_bgms(
    util: ExportUtil, bgms: list[BgmEntity]
) -> None:  # pragma: no cover
    all_bgm_data = get_all_nice_bgms(util.region, util.lang, bgms)
    await util.dump_orjson("nice_bgm", all_bgm_data)


async def dump_nice_mms(
    util: ExportUtil, mms: list[MstMasterMission]
) -> None:  # pragma: no cover
    all_mm_data = await get_all_nice_mms(util.conn, util.region, mms, util.lang)
    await util.dump_orjson("nice_master_mission", all_mm_data)


async def dump_nice_wars(
    util: ExportUtil, wars: list[MstWar]
) -> None:  # pragma: no cover
    all_war_data = [
        await get_nice_war(util.conn, util.region, war.id, util.lang) for war in wars
    ]
    await util.dump_orjson("nice_war", all_war_data)


async def dump_nice_events(
    util: ExportUtil, events: list[MstEvent]
) -> None:  # pragma: no cover
    all_event_data = [
        await get_nice_event(util.conn, util.region, event.id, util.lang)
        for event in events
    ]
    await util.dump_orjson("nice_event", all_event_data)


async def dump_nice_shops(
    util: ExportUtil, shops: list[MstShop]
) -> None:  # pragma: no cover
    all_shop_data = await get_nice_shops_from_raw(
        util.conn, util.region, shops, util.lang
    )
    await util.dump_orjson("nice_shop", all_shop_data)


async def dump_illustrators(
    util: ExportUtil, illustrators: list[MstIllustrator]
) -> None:  # pragma: no cover
    if util.region == Region.JP and util.lang == Language.en:
        mstIllustrators_en: list[MstIllustrator] = []
        for illustrator in illustrators:
            illustrator_en = illustrator.copy()
            illustrator_en.name = get_translation(Language.en, illustrator_en.name)
            mstIllustrators_en.append(illustrator_en)
        await util.dump_orjson("nice_illustrator", mstIllustrators_en)
    else:
        await util.dump_orjson("nice_illustrator", illustrators)


async def dump_cvs(util: ExportUtil, cvs: list[MstCv]) -> None:  # pragma: no cover
    if util.region == Region.JP and util.lang == Language.en:
        mstCvs_en: list[MstCv] = []
        for cv in cvs:
            cv_en = cv.copy()
            cv_en.name = get_translation(Language.en, cv_en.name)
            mstCvs_en.append(cv_en)
        await util.dump_orjson("nice_cv", mstCvs_en)
    else:
        await util.dump_orjson("nice_cv", cvs)


async def dump_basic_servants(
    util: ExportUtil, file_name: str, svts: list[MstSvt]
) -> None:  # pragma: no cover
    all_basic_servant_data = sorted(
        await get_all_basic_servants(util.redis, util.region, util.lang, svts),
        key=lambda x: x.collectionNo,
    )
    await util.dump_orjson(file_name, all_basic_servant_data)


async def dump_basic_equips(
    util: ExportUtil, equips: list[MstSvt]
) -> None:  # pragma: no cover
    all_basic_equip_data = sorted(
        await get_all_basic_equips(util.redis, util.region, util.lang, equips),
        key=lambda x: x.collectionNo,
    )
    await util.dump_orjson("basic_equip", all_basic_equip_data)


async def dump_basic_mcs(
    util: ExportUtil, mcs: list[MstEquip]
) -> None:  # pragma: no cover
    all_basic_mc_data = get_all_basic_mcs(util.region, util.lang, mcs)
    await util.dump_orjson("basic_mystic_code", all_basic_mc_data)


async def dump_basic_ccs(
    util: ExportUtil, ccs: list[MstCommandCode]
) -> None:  # pragma: no cover
    all_basic_cc_data = sorted(
        get_all_basic_ccs(util.region, util.lang, ccs), key=lambda x: x.collectionNo
    )
    await util.dump_orjson("basic_command_code", all_basic_cc_data)


async def dump_basic_events(
    util: ExportUtil, events: list[MstEvent]
) -> None:  # pragma: no cover
    all_basic_event_data = get_all_basic_events(util.lang, events)
    await util.dump_orjson("basic_event", all_basic_event_data)


async def dump_basic_wars(
    util: ExportUtil, wars: list[MstWar]
) -> None:  # pragma: no cover
    all_basic_war_data = get_all_basic_wars(util.lang, wars)
    await util.dump_orjson("basic_war", all_basic_war_data)


async def generate_exports(
    redis: Redis,
    region_path: dict[Region, DirectoryPath],
    async_engines: dict[Region, AsyncEngine],
) -> None:  # pragma: no cover
    if settings.export_all_nice:
        for region in region_path:
            start_time = time.perf_counter()
            export_path = project_root / "export" / region.value

            async with async_engines[region].connect() as conn:
                logger.info(f"Exporting {region} data …")

                util = ExportUtil(conn, redis, region, export_path)

                all_svts = await fetch.get_everything(conn, MstSvt)
                all_servants = [
                    svt for svt in all_svts if svt.collectionNo != 0 and svt.isServant()
                ]
                await dump_basic_servants(util, "basic_servant", all_servants)

                all_equips = await get_all_equips(conn)
                await dump_basic_equips(util, all_equips)

                mstCcs = await fetch.get_everything(conn, MstCommandCode)
                await dump_basic_ccs(util, mstCcs)

                mstWars = await fetch.get_everything(conn, MstWar)
                await dump_basic_wars(util, mstWars)

                mstEvents = await fetch.get_everything(conn, MstEvent)
                await dump_basic_events(util, mstEvents)

                mstEquips = await fetch.get_everything(conn, MstEquip)
                await dump_basic_mcs(util, mstEquips)

                await dump_normal(export_path, "nice_trait", TRAIT_NAME)
                await dump_normal(export_path, "nice_enums", ALL_ENUMS)

                mstIllustrators = await fetch.get_everything(conn, MstIllustrator)
                await dump_illustrators(util, mstIllustrators)

                mstCvs = await fetch.get_everything(conn, MstCv)
                await dump_cvs(util, mstCvs)

                bgms = await get_all_bgm_entities(conn)
                mstItems = await fetch.get_everything(conn, MstItem)
                mstMasterMissions = await fetch.get_everything(conn, MstMasterMission)
                mstShops = await fetch.get_all(conn, MstShop, 0)

                asset_storage = await fetch.get_everything(conn, AssetStorageLine)
                await util.dump_orjson("asset_storage", asset_storage)

                await dump_basic_servants(util, "basic_svt", all_svts)

                await dump_nice_items(util, mstItems)
                await dump_nice_mcs(util, mstEquips)
                await dump_nice_ccs(util, mstCcs)
                await dump_nice_mms(util, mstMasterMissions)
                await dump_nice_bgms(util, bgms)
                await dump_nice_shops(util, mstShops)

                util_en = ExportUtil(conn, redis, region, export_path, Language.en)
                if region == Region.JP:
                    await dump_basic_servants(util_en, "basic_servant", all_servants)
                    await dump_basic_equips(util_en, all_equips)
                    await dump_basic_ccs(util_en, mstCcs)
                    await dump_basic_wars(util_en, mstWars)
                    await dump_basic_events(util_en, mstEvents)
                    await dump_basic_mcs(util_en, mstEquips)

                    await dump_illustrators(util_en, mstIllustrators)
                    await dump_cvs(util_en, mstCvs)

                    await dump_basic_servants(util_en, "basic_svt", all_svts)
                    await dump_nice_items(util_en, mstItems)
                    await dump_nice_mcs(util_en, mstEquips)
                    await dump_nice_ccs(util_en, mstCcs)
                    await dump_nice_bgms(util_en, bgms)

                await dump_svt(util, "nice_servant", all_servants)
                await dump_svt(util, "nice_equip", all_equips)

                await dump_nice_wars(util, mstWars)
                await dump_nice_events(util, mstEvents)

                if region == Region.JP:
                    await dump_nice_wars(util_en, mstWars)
                    await dump_nice_events(util_en, mstEvents)

            repo_info = await get_repo_version(redis, region)
            if repo_info is not None:
                await dump_normal(export_path, "info", repo_info.dict())

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


async def clear_redis_cache(
    redis: Redis, region_path: dict[Region, DirectoryPath]
) -> None:  # pragma: no cover
    key_count = 0

    for region in region_path:
        key_pattern = f"{settings.redis_prefix}:cache:{region.value}*"
        async for key in redis.scan_iter(match=key_pattern):
            await redis.delete(key)
            key_count += 1

    async for key in redis.scan_iter(match=f"{settings.redis_prefix}:cache::*"):
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
        await clear_redis_cache(redis, region_path)
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


async def report_webhooks(
    region_path: dict[Region, DirectoryPath]
) -> None:  # pragma: no cover
    async with httpx.AsyncClient() as client:
        for index, url in enumerate(settings.webhooks):
            try:
                await client.post(url, json={"regions": list(region_path.keys())})
            except Exception:  # pylint: disable=broad-except
                logger.exception(f"Failed to report webhook {index}")


async def pull_and_update(
    region_path: dict[Region, DirectoryPath],
    async_engines: dict[Region, AsyncEngine],
    redis: Redis,
) -> None:  # pragma: no cover
    await run_in_threadpool(lambda: update_data_repo(region_path))
    await load_and_export(redis, region_path, async_engines)
    await report_webhooks(region_path)
