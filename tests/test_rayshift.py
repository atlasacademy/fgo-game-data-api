# pylint: disable=R0201,R0904
from fastapi.testclient import TestClient
from sqlalchemy.sql import delete, select

from app.models.rayshift import rayshiftQuest
from app.db.engine import engines
from app.main import app
from app.schemas.common import Region


client = TestClient(app)


def test_rayshift_uncached_quest() -> None:
    test_quest_id = 94033502
    select_stmt = select(rayshiftQuest).where(rayshiftQuest.c.questId == test_quest_id)

    with engines[Region.NA].begin() as conn:
        delete_stmt = delete(rayshiftQuest).where(
            rayshiftQuest.c.questId == test_quest_id
        )
        conn.execute(delete_stmt)
        assert conn.execute(select_stmt).fetchone() is None

    chaldea_is_delicious = client.get(f"/nice/NA/quest/{test_quest_id}/1").json()
    assert len(chaldea_is_delicious["stages"][0]["enemies"]) == 4

    with engines[Region.NA].begin() as conn:
        assert conn.execute(select_stmt).fetchone()
