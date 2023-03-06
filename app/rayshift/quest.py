import time
from typing import Optional, Union

import httpx
from fastapi import HTTPException
from httpx import Client
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncConnection

from ..config import Settings, logger
from ..db.helpers.rayshift import (
    get_rayshift_quest_db,
    insert_rayshift_quest_db,
    insert_rayshift_quest_hash_db,
)
from ..schemas.common import Region
from ..schemas.rayshift import (
    BaseRayshiftResponse,
    QuestDetail,
    QuestList,
    QuestListRayshiftResponse,
    QuestRayshiftResponse,
    QuestResponse,
)


settings = Settings()

NO_API_KEY = settings.rayshift_api_key.get_secret_value() == ""
QUEST_ENDPOINT = f"{settings.rayshift_api_url}/avalon-data-export/quests"
REGION_ENUM = {Region.JP: 1, Region.NA: 2}


async def get_quest_response(
    region: Region, quest_id: int, phase: int
) -> Optional[QuestResponse]:
    if NO_API_KEY or region not in REGION_ENUM:  # pragma: no cover
        return None

    async with httpx.AsyncClient(follow_redirects=True) as client:
        params: dict[str, Union[str, int]] = {
            "apiKey": settings.rayshift_api_key.get_secret_value(),
            "region": REGION_ENUM[region],
            "questId": quest_id,
            "questPhase": phase,
        }
        try:
            r = await client.get(f"{QUEST_ENDPOINT}/get", params=params)
        except httpx.RequestError:  # pragma: no cover
            return None
        if r.status_code == httpx.codes.OK:
            return QuestRayshiftResponse.parse_raw(r.content).response
        elif r.status_code == httpx.codes.TOO_MANY_REQUESTS:  # pragma: no cover
            rate_limit = BaseRayshiftResponse.parse_raw(r.content)
            wait_seconds = rate_limit.wait if rate_limit.wait else 60
            raise HTTPException(
                status_code=r.status_code,
                detail=f"Please wait {wait_seconds} seconds until you make the next quest request",
            )
        else:
            return None


async def get_quest_detail(
    conn: AsyncConnection,
    region: Region,
    quest_id: int,
    phase: int,
    questSelect: int | None = None,
    questHash: str | None = None,
) -> Optional[QuestDetail]:
    db_quest_detail = await get_rayshift_quest_db(
        conn, quest_id, phase, questSelect, questHash
    )
    if db_quest_detail:
        return db_quest_detail
    else:
        quest_response = await get_quest_response(region, quest_id, phase)
        if quest_response and quest_response.questDetails:
            await insert_rayshift_quest_db(conn, quest_response.questDetails)
            await insert_rayshift_quest_hash_db(conn, quest_response.questDetails)
            quest_detail = next(iter(quest_response.questDetails.values()))
            if (
                questSelect is not None and quest_detail.questSelect != questSelect
            ):  # pragma: no cover
                return None
            return quest_detail

        return None


def get_multiple_quests(
    client: Client, region: Region, query_ids: list[int]
) -> dict[int, QuestDetail]:
    if NO_API_KEY or region not in REGION_ENUM:  # pragma: no cover
        return {}

    params: dict[str, Union[str, int, list[int]]] = {
        "apiKey": settings.rayshift_api_key.get_secret_value(),
        "region": REGION_ENUM[region],
    }
    if len(query_ids) == 0:
        return {}
    elif len(query_ids) == 1:
        params["id"] = query_ids[0]
    else:
        params["ids"] = query_ids

    r = client.get(f"{QUEST_ENDPOINT}/get", params=params)
    if r.status_code == httpx.codes.TOO_MANY_REQUESTS:  # pragma: no cover
        sleep_time = r.json().get("wait", 10)
        logger.info(f"Sleeping {sleep_time} seconds for RayShift API")
        time.sleep(sleep_time)
        r = client.get(f"{QUEST_ENDPOINT}/get", params=params)

    try:
        return QuestRayshiftResponse.parse_raw(r.content).response.questDetails
    except ValidationError:  # pragma: no cover
        return {}


def get_all_quest_lists(
    client: Client, region: Region
) -> list[QuestList]:  # pragma: no cover
    if NO_API_KEY or region not in REGION_ENUM:
        return []

    params: dict[str, Union[str, int]] = {
        "apiKey": settings.rayshift_api_key.get_secret_value(),
        "region": REGION_ENUM[region],
    }
    r = client.get(f"{QUEST_ENDPOINT}/list", params=params, follow_redirects=True)
    if r.status_code != httpx.codes.OK:
        return []

    return QuestListRayshiftResponse.parse_raw(r.content).response.quests
