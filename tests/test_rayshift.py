# pylint: disable=R0201,R0904
import pytest
from httpx import AsyncClient
from sqlalchemy.sql import and_, delete, select

from app.db.engine import engines
from app.db.load import load_rayshift_quest_list
from app.models.rayshift import rayshiftQuest
from app.rayshift.quest import get_all_quest_lists
from app.schemas.common import Region
from app.schemas.rayshift import QuestList


@pytest.mark.asyncio
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

    with engines[Region.NA].begin() as conn:
        assert conn.execute(select_stmt).fetchone()


def test_rayshift_get_quest_list() -> None:
    quest_list = get_all_quest_lists(Region.NA)
    assert len(quest_list) > 100


@pytest.mark.asyncio
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
            lastUpdated="2021-06-11T08:44:29.838402",
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
