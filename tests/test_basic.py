# pylint: disable=R0201
import pytest
from httpx import AsyncClient

from .utils import get_response_data


test_cases_dict: dict[str, tuple[str, str]] = {
    "servant_NA_collectionNo": ("NA/servant/76", "NA_Mordred"),
    "servant_NA_id": ("NA/servant/100900", "NA_Mordred"),
    "servant_JP_collectionNo": ("JP/servant/256", "JP_Gareth"),
    "servant_JP_id": ("JP/servant/303900", "JP_Gareth"),
    "servant_JP_lang_en": ("JP/servant/208?lang=en", "JP_Sieg_en"),
    "svt_JP_lang_en": ("JP/svt/503800?lang=en", "JP_Sieg_en"),
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
}


test_cases = [pytest.param(*value, id=key) for key, value in test_cases_dict.items()]


@pytest.mark.asyncio
@pytest.mark.parametrize("query,result", test_cases)
async def test_basic(client: AsyncClient, query: str, result: str) -> None:
    response = await client.get(f"/basic/{query}")
    assert response.status_code == 200
    assert response.json() == get_response_data("test_data_basic", result)


cases_404_dict = {
    "servant": "500",
    "equip": "3001",
    "svt": "10098",
    "skill": "25689",
    "NP": "900205",
    "function": "9000",
    "buff": "765",
    "MC": "62537",
    "CC": "8400111",
    "event": "2313",
    "war": "42312",
    "quest": "2134123",
}


cases_404 = [pytest.param(key, value, id=key) for key, value in cases_404_dict.items()]


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint,item_id", cases_404)
async def test_404_basic(client: AsyncClient, endpoint: str, item_id: str) -> None:
    response = await client.get(f"/basic/JP/{endpoint}/{item_id}")
    assert response.status_code == 404
    assert response.json()["detail"][-9:] == "not found"


@pytest.mark.asyncio
class TestBasicSpecial:
    async def test_NA_not_integer(self, client: AsyncClient) -> None:
        response = await client.get("/basic/NA/servant/lkji")
        assert response.status_code == 422

    async def test_func_addState_no_buff(self, client: AsyncClient) -> None:
        response = await client.get("/basic/JP/function/4086")
        assert response.status_code == 200

    async def test_skill_reverse_passive(self, client: AsyncClient) -> None:
        response = await client.get("/basic/NA/skill/30650?reverse=True")
        reverse_servants: set[int] = {
            servant["id"] for servant in response.json()["reverse"]["basic"]["servant"]
        }
        assert response.status_code == 200
        assert reverse_servants == {201200, 401800, 601000}

    async def test_JP_English_name(self, client: AsyncClient) -> None:
        response = await client.get("/basic/JP/servant/304300?lang=en")
        assert response.json()["name"] == "Elice Utsumi"

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
        assert response.status_code == 200
        assert response.json()["reverse"]["basic"]["function"][1]["reverse"]["basic"][
            "skill"
        ]

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
