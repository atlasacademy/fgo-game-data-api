# pylint: disable=R0201,R0904
import pytest
from sqlalchemy.sql import delete, select

from app.db.engine import engines
from app.models.rayshift import rayshiftQuest
from app.schemas.common import Region

from .utils import get_response


@pytest.mark.asyncio
async def test_rayshift_uncached_quest() -> None:
    test_quest_id = 94033502
    select_stmt = select(rayshiftQuest).where(rayshiftQuest.c.questId == test_quest_id)

    with engines[Region.NA].begin() as conn:
        delete_stmt = delete(rayshiftQuest).where(
            rayshiftQuest.c.questId == test_quest_id
        )
        conn.execute(delete_stmt)
        assert conn.execute(select_stmt).fetchone() is None

    chaldea_is_delicious = await get_response(f"/nice/NA/quest/{test_quest_id}/1")
    assert len(chaldea_is_delicious.json()["stages"][0]["enemies"]) == 4

    with engines[Region.NA].begin() as conn:
        assert conn.execute(select_stmt).fetchone()
