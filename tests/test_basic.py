from dataclasses import dataclass

import pytest
from httpx import AsyncClient
from redis.asyncio import Redis

from app.core.basic import get_basic_svt
from app.schemas.common import Region

from .utils import get_response_data


test_cases_dict: dict[str, tuple[str, str]] = {
    "servant_NA_collectionNo": ("NA/servant/76", "NA_Mordred"),
    "servant_NA_id": ("NA/servant/100900", "NA_Mordred"),
    "servant_JP_collectionNo": ("JP/servant/256", "JP_Gareth"),
    "servant_JP_id": ("JP/servant/303900", "JP_Gareth"),
    "servant_JP_lang_en": ("JP/servant/208?lang=en", "JP_Sieg_en"),
    "svt_JP_lang_en": ("JP/svt/503800?lang=en", "JP_Sieg_en"),
    "svt_JP_limit_3_face": (
        "JP/svt/9935900",
        "JP_Soul_Eater",
    ),  # This one only has limit=3 so the face URL should use 3 instead of 0
    "svt_JP_limit_costum": (
        "JP/svt/9100101",
        "JP_Girl_Ghost",
    ),  # This one has costume limt=2 so the face URL should use the costume's battleCharaId instead
    "svt_material_td_JP": ("JP/svt/404601", "JP_Liz_td_material"),
    "equip_JP_collectionNo": ("JP/equip/467", "JP_Bitter_Chocolates"),
    "equip_JP_id": ("JP/equip/9805370", "JP_Bitter_Chocolates"),
    "skill_NA_id": ("NA/skill/455350", "NA_Fujino_2nd_skill"),
    "skill_NA_reverse": ("NA/skill/19450?reverse=True", "NA_Fionn_1st_skill_reverse"),
    "NP_JP_id": ("JP/NP/301101", "JP_Fionn_NP"),
    "NP_JP_reverse": ("JP/NP/202901?reverse=True", "JP_Fujino_NP_reverse"),
    "function_NA_id": ("NA/function/433", "NA_function_433"),
    "function_JP_reverse": ("NA/function/298?reverse=True", "NA_function_298_reverse"),
    "buff_NA_id": ("NA/buff/300", "NA_buff_300"),
    "buff_NA_reverse": ("NA/buff/267?reverse=True", "NA_buff_267_reverse"),
    "MC_NA_id": ("NA/MC/110", "NA_MC_LB"),
    "JP_CC_id": ("JP/CC/8400550", "JP_CC_8400550"),
    "JP_CC_collectionNo": ("JP/CC/55", "JP_CC_8400550"),
    "NA_event_id": ("NA/event/80119", "NA_event_Oniland"),
    "JP_war_id": ("JP/war/201", "JP_war_Shinjuku"),
    "NA_quest_id": ("NA/quest/91600701", "NA_Jekyll_Interlude"),
    "JP_quest_phase": ("NA/quest/2000301/1", "NA_Shimousa_quest"),
}


test_cases = [pytest.param(*value, id=key) for key, value in test_cases_dict.items()]


@pytest.mark.asyncio
@pytest.mark.parametrize("query,result", test_cases)
async def test_basic(client: AsyncClient, query: str, result: str) -> None:
    response = await client.get(f"/basic/{query}")
    assert response.status_code == 200
    assert response.json() == get_response_data("test_data_basic", result)


@dataclass
class Case404:
    endpoint: str
    id_: str

    def __str__(self) -> str:
        return f"{self.endpoint}_{self.id_}"


cases_404 = [
    Case404("servant", "0"),
    Case404("servant", "500"),
    Case404("equip", "0"),
    Case404("equip", "3001"),
    Case404("svt", "10098"),
    Case404("skill", "25689"),
    Case404("NP", "900205"),
    Case404("function", "90000"),
    Case404("buff", "765"),
    Case404("MC", "62537"),
    Case404("CC", "8400111"),
    Case404("event", "2313"),
    Case404("war", "42312"),
    Case404("quest", "2134123"),
    Case404("quest", "123412334/2"),
]


pytest_cases_404 = [
    pytest.param(test_case.endpoint, test_case.id_, id=str(test_case))
    for test_case in cases_404
]


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint,item_id", pytest_cases_404)
async def test_404_basic(client: AsyncClient, endpoint: str, item_id: str) -> None:
    response = await client.get(f"/basic/JP/{endpoint}/{item_id}")
    assert response.status_code == 404
    assert response.json()["detail"][-9:] == "not found"


cases_overflow_dict = {
    "quest": "112345678910111213",
    "quest/112345678910111213": "1",
}


cases_overflow = [
    pytest.param(key, value, id=key) for key, value in cases_overflow_dict.items()
]


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint,item_id", cases_overflow)
async def test_int_overflow_basic(
    client: AsyncClient, endpoint: str, item_id: str
) -> None:
    response = await client.get(f"/basic/JP/{endpoint}/{item_id}")
    assert response.status_code == 404
    assert response.json()["detail"][-9:] == "not found"


@dataclass
class BasicSvtFaceCase:
    region: Region
    svt_id: int
    svt_limit: int | None = None
    face_suffix: str = ""


@pytest.mark.asyncio
class TestBasicSpecial:
    async def test_basic_servant_face(self, redis: "Redis[bytes]") -> None:
        basic_face_cases = [
            BasicSvtFaceCase(Region.NA, 303800, None, "NA/Faces/f_3038000.png"),
            BasicSvtFaceCase(Region.NA, 303800, 4, "NA/Faces/f_3038003.png"),
            BasicSvtFaceCase(Region.NA, 303800, 11, "NA/Faces/f_3038300.png"),
            BasicSvtFaceCase(Region.JP, 9100101, None, "JP/Enemys/99402402.png"),
            BasicSvtFaceCase(Region.JP, 9100101, 2, "JP/Enemys/99402402.png"),
            BasicSvtFaceCase(Region.JP, 9935900, None, "JP/Enemys/99359003.png"),
            BasicSvtFaceCase(Region.JP, 404601, None, "JP/Faces/f_4046000.png"),
            BasicSvtFaceCase(Region.JP, 9943860, 2, "JP/Faces/f_99438601.png"),
        ]

        for case in basic_face_cases:
            basic_svt = await get_basic_svt(
                redis, case.region, case.svt_id, case.svt_limit
            )
            assert basic_svt["face"].endswith(case.face_suffix)

    async def test_NA_not_integer(self, client: AsyncClient) -> None:
        response = await client.get("/basic/NA/servant/lkji")
        assert response.status_code == 422

    async def test_func_addState_no_buff(self, client: AsyncClient) -> None:
        response = await client.get("/basic/NA/function/4086")
        assert response.status_code == 200
        assert len(response.json()["buffs"]) == 0

    async def test_skill_reverse_passive(self, client: AsyncClient) -> None:
        response = await client.get("/basic/NA/skill/30650?reverse=True")
        reverse_servants: set[int] = {
            servant["id"] for servant in response.json()["reverse"]["basic"]["servant"]
        }
        assert response.status_code == 200
        assert reverse_servants == {201200, 401800, 601000}

    async def test_JP_English_name(self, client: AsyncClient) -> None:
        response = await client.get("/basic/JP/servant/304300?lang=en")
        assert response.json()["name"] == "Utsumi Erice"

        response = await client.get("/basic/JP/servant/311?lang=en")
        assert response.json()["name"] == "Fairy Knight Tristan"

    async def test_JP_skill_English_name(self, client: AsyncClient) -> None:
        response = await client.get("/basic/JP/skill/991604?lang=en")
        assert response.status_code == 200
        assert response.json()["name"] == "Paradox Ace Killer"

    async def test_JP_CC_English_name(self, client: AsyncClient) -> None:
        response = await client.get("/basic/JP/CC/8400240?lang=en")
        assert response.status_code == 200
        assert response.json()["name"] == "The Holy Night's Aurora"

    async def test_JP_MC_English_name(self, client: AsyncClient) -> None:
        response = await client.get("/basic/JP/MC/60?lang=en")
        assert response.status_code == 200
        assert response.json()["name"] == "Royal Brand"

    async def test_buff_reverse_skillNp(self, client: AsyncClient) -> None:
        response = await client.get(
            "/basic/NA/buff/203?reverse=True&reverseDepth=skillNp"
        )
        f_with_skill = next(
            func
            for func in response.json()["reverse"]["basic"]["function"]
            if func["funcId"] == 641
        )

        assert response.status_code == 200
        assert f_with_skill["reverse"]["basic"]["skill"]

    async def test_function_reverse_servant(self, client: AsyncClient) -> None:
        response = await client.get(
            "/basic/NA/function/102?reverse=True&reverseDepth=servant"
        )
        assert response.status_code == 200
        assert response.json()["reverse"]["basic"]["skill"][0]["reverse"]["basic"][
            "servant"
        ]

    async def test_translation_override(self, client: AsyncClient) -> None:
        response = await client.get("basic/JP/NP/100102?lang=en")
        assert response.status_code == 200
        assert response.json()["name"] == "Excalibur"

    async def test_reverse_extra_passive(self, client: AsyncClient) -> None:
        response = await client.get(
            "basic/JP/skill/940142?reverse=true&reverseData=basic&lang=en"
        )
        reverse_svt_ids = [
            svt["id"] for svt in response.json()["reverse"]["basic"]["servant"]
        ]
        assert reverse_svt_ids == [303800, 1100700]

    async def test_enemy_changelog(self, client: AsyncClient) -> None:
        response = await client.get("basic/NA/quest/phase/latestEnemyData")
        assert response.status_code == 200
