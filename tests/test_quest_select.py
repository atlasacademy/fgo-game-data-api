import pytest
from httpx import AsyncClient


test_cases_dict: dict[str, tuple[str, str | None, tuple[str] | tuple[str, str]]] = {
    "94040902": (
        "NA/quest/94040902/1",
        "1_0507_69b6dcc",
        ("1_0502_76ecbb5", "1_0507_69b6dcc"),
    ),
    "94040902_1_0502_76ecbb5": (
        "NA/quest/94040902/1?hash=1_0502_76ecbb5",
        "1_0502_76ecbb5",
        ("1_0502_76ecbb5", "1_0507_69b6dcc"),
    ),
    "94040902_1_0507_69b6dcc": (
        "NA/quest/94040902/1?hash=1_0507_69b6dcc",
        "1_0507_69b6dcc",
        ("1_0502_76ecbb5", "1_0507_69b6dcc"),
    ),
    "3000109": ("NA/quest/3000109/1", "1_0835_4c89d6b", ("1_0835_4c89d6b",)),
    "3000109_1_0835_4c89d6b": (
        "NA/quest/3000109/1?hash=1_0835_4c89d6b",
        "1_0835_4c89d6b",
        ("1_0835_4c89d6b",),
    ),
    "3000109_1_0156_c3a1e0f": (
        "NA/quest/3000109/1?hash=1_0156_c3a1e0f",
        None,
        ("1_0835_4c89d6b",),
    ),
    "3000110": ("NA/quest/3000110/1", "1_0156_c3a1e0f", ("1_0156_c3a1e0f",)),
    "3000110_1_0835_4c89d6b": (
        "NA/quest/3000110/1?hash=1_0156_c3a1e0f",
        "1_0156_c3a1e0f",
        ("1_0156_c3a1e0f",),
    ),
    "3000110_1_0156_c3a1e0f": (
        "NA/quest/3000110/1?hash=1_0835_4c89d6b",
        None,
        ("1_0156_c3a1e0f",),
    ),
}


test_cases = [pytest.param(*value, id=key) for key, value in test_cases_dict.items()]


@pytest.mark.asyncio
@pytest.mark.parametrize("query,enemyHash,availableEnemyHashes", test_cases)
async def test_quest_select(
    client: AsyncClient, query: str, enemyHash: str, availableEnemyHashes: tuple[str]
) -> None:
    response = (await client.get(f"/nice/{query}")).json()
    assert response.get("enemyHash") == enemyHash
    assert response.get("availableEnemyHashes") == list(availableEnemyHashes)
