from typing import Optional, Union

import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncConnection

from ..config import SecretSettings, Settings
from ..db.helpers.rayshift import get_rayshift_quest_db, insert_rayshift_quest_db
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
secrets = SecretSettings()

QUEST_ENDPOINT = f"{settings.rayshift_api_url}/avalon-data-export/quests"
REGION_ENUM = {Region.JP: 1, Region.NA: 2}


async def get_quest_response(
    region: Region, quest_id: int, phase: int
) -> Optional[QuestResponse]:
    if secrets.rayshift_api_key.get_secret_value() == "":  # pragma: no cover
        return None

    async with httpx.AsyncClient() as client:
        params: dict[str, Union[str, int]] = {
            "apiKey": secrets.rayshift_api_key.get_secret_value(),
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
    conn: AsyncConnection, region: Region, quest_id: int, phase: int
) -> Optional[QuestDetail]:
    db_quest_detail = await get_rayshift_quest_db(conn, quest_id, phase)
    if db_quest_detail:
        return db_quest_detail
    else:
        quest_response = await get_quest_response(region, quest_id, phase)
        if quest_response:
            await insert_rayshift_quest_db(
                conn, quest_id, phase, quest_response.questDetails
            )
            return next(iter(quest_response.questDetails.values()))

        return None


def get_all_quest_lists(region: Region) -> list[QuestList]:
    if secrets.rayshift_api_key.get_secret_value() == "":  # pragma: no cover
        return []

    params: dict[str, Union[str, int]] = {
        "apiKey": secrets.rayshift_api_key.get_secret_value(),
        "region": REGION_ENUM[region],
    }
    r = httpx.get(f"{QUEST_ENDPOINT}/list", params=params)

    return QuestListRayshiftResponse.parse_raw(r.content).response.quests
