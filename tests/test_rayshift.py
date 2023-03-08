from datetime import datetime

import pytest
from httpx import AsyncClient, Client
from sqlalchemy.sql import and_, delete, select

from app.config import Settings
from app.db.engine import engines
from app.db.load import (
    get_all_missing_query_ids,
    get_missing_query_ids,
    load_rayshift_quest_details,
    load_rayshift_quest_list,
)
from app.models.rayshift import rayshiftQuest
from app.rayshift.quest import get_multiple_quests
from app.schemas.common import Region
from app.schemas.rayshift import QuestList


settings = Settings()

doesnt_have_rayshift_api_key = settings.rayshift_api_key.get_secret_value() == ""
skip_reason = "Requires rayshift API key"


@pytest.mark.asyncio
@pytest.mark.skipif(doesnt_have_rayshift_api_key, reason=skip_reason)
async def test_rayshift_uncached_quest(client: AsyncClient) -> None:
    test_quest_id = 94033502
    select_stmt = select(rayshiftQuest).where(rayshiftQuest.c.questId == test_quest_id)

    with engines[Region.NA].begin() as conn:
        delete_stmt = delete(rayshiftQuest).where(
            rayshiftQuest.c.questId == test_quest_id
        )
        conn.execute(delete_stmt)
        assert conn.execute(select_stmt).fetchone() is None

    chaldea_is_delicious = await client.get(f"/nice/NA/quest/{test_quest_id}/1")
    assert len(chaldea_is_delicious.json()["stages"][0]["enemies"]) == 4

    with engines[Region.NA].connect() as conn:
        assert conn.execute(select_stmt).fetchone()


def test_rayshift_missing_ids() -> None:
    query_ids = get_missing_query_ids(Region.NA)
    assert len(query_ids) >= 0

    specific_query_id = get_missing_query_ids(Region.NA, [2000202])
    assert len(specific_query_id) == 1

    query_ids = get_all_missing_query_ids(Region.NA)
    assert len(query_ids) >= 0

    specific_all_query_id = get_all_missing_query_ids(Region.NA, [2000202])
    assert len(specific_all_query_id) >= 0


@pytest.mark.skipif(doesnt_have_rayshift_api_key, reason=skip_reason)
def test_get_rayshift_query_ids() -> None:
    client = Client(follow_redirects=True)
    assert get_multiple_quests(client, Region.NA, []) == {}
    assert 157425 in get_multiple_quests(client, Region.NA, [157425])


@pytest.mark.skipif(doesnt_have_rayshift_api_key, reason=skip_reason)
def test_load_rayshift_quest_details() -> None:
    client = Client(follow_redirects=True)
    query_ids = [157425, 157429]
    quest_details = get_multiple_quests(client, Region.NA, query_ids)
    for query_id in query_ids:
        assert query_id in quest_details

    where_cond = rayshiftQuest.c.queryId.in_(query_ids)
    select_stmt = select(rayshiftQuest).where(where_cond)

    with engines[Region.NA].begin() as conn:
        delete_stmt = delete(rayshiftQuest).where(where_cond)
        conn.execute(delete_stmt)
        assert conn.execute(select_stmt).fetchone() is None

    load_rayshift_quest_details(Region.NA, quest_details)

    with engines[Region.NA].connect() as conn:
        db_data = conn.execute(select_stmt).fetchall()
        assert sorted(row.queryId for row in db_data) == query_ids


@pytest.mark.asyncio
@pytest.mark.skipif(doesnt_have_rayshift_api_key, reason=skip_reason)
async def test_rayshift_load_quest_list(client: AsyncClient) -> None:
    test_quest_id = 1000000
    select_stmt = select(rayshiftQuest).where(rayshiftQuest.c.questId == test_quest_id)

    with engines[Region.NA].begin() as conn:
        delete_stmt = delete(rayshiftQuest).where(
            rayshiftQuest.c.questId == test_quest_id
        )
        conn.execute(delete_stmt)
        assert conn.execute(select_stmt).fetchone() is None

    quest_list = [
        QuestList(
            questId=1000000,
            questPhase=1,
            count=3,
            lastUpdated=datetime(2021, 6, 11, 8, 44, 29, 838402),
            queryIds=[91327, 82122, 77080],
            region=2,
        )
    ]
    load_rayshift_quest_list(Region.NA, quest_list)

    with engines[Region.NA].connect() as conn:
        assert conn.execute(select_stmt).fetchone() is not None

    await client.get(f"/nice/NA/quest/{test_quest_id}/1", timeout=15)

    with engines[Region.NA].connect() as conn:
        inserted_rayshift_cache = select(rayshiftQuest).where(
            and_(
                rayshiftQuest.c.questId == test_quest_id,
                rayshiftQuest.c.phase == 1,
                rayshiftQuest.c.questDetail.isnot(None),
            )
        )
        assert conn.execute(inserted_rayshift_cache).fetchone() is not None
