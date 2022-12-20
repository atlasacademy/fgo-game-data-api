import pytest
from httpx import AsyncClient

from app.core.raw import get_quest_ids_in_conds
from app.data.utils import load_master_data
from app.schemas.enums import FUNC_VALS_NOT_BUFF
from app.schemas.raw import MstEventMissionCondition, MstEventMissionConditionDetail

from .utils import get_response_data, test_gamedata


DATA_FOLDER = "test_data_raw"


test_cases_dict: dict[str, tuple[str, str]] = {
    "servant_NA_collectionNo": ("NA/servant/184", "NA_Tomoe"),
    "servant_NA_id": ("NA/servant/202100", "NA_Tomoe"),
    "servant_NA_lore": ("NA/servant/156?lore=True", "NA_Moriarty_lore"),
    "servant_NA_collectionNo_expanded": (
        "NA/servant/200?expand=True",
        "NA_Fujino_expanded",
    ),
    "servant_JP_collectionNo": ("JP/servant/185", "JP_Chiyome"),
    "servant_JP_id": ("JP/servant/602900", "JP_Chiyome"),
    "svtScript_JP": ("JP/svtScript?charaId=10010001&charaId=10010002", "JP_svtScripts"),
    "equip_NA_collectionNo": ("NA/equip/184", "NA_Gentle_affection"),
    "equip_NA_id": ("NA/equip/9401400", "NA_Gentle_affection"),
    "equip_NA_collectionNo_expanded": (
        "NA/equip/375?expand=True",
        "NA_Oni_Mask_expanded",
    ),
    "svt_JP_id": ("NA/svt/9401400", "NA_Gentle_affection"),
    "skill_NA": ("NA/skill/24550", "NA_skill_24550"),
    "skill_NA_reverse": ("NA/skill/446550?reverse=True", "NA_skill_446550_reverse"),
    "skill_NA_expand": ("NA/skill/275551?expand=True", "NA_skill_275551_expand"),
    "skill_NA_reverse_expand": (
        "NA/skill/275551?expand=True&reverse=True",
        "NA_skill_275551_reverse_expand",
    ),
    "skill_JP_reverse_MC": ("JP/skill/980004?reverse=true", "JP_skill_980004_reverse"),
    "NP_NA": ("NA/NP/900101", "NA_NP_900101"),
    "NP_NA_reverse": ("NA/NP/9940531?reverse=True", "NA_NP_9940531_reverse"),
    "NP_NA_expand": ("NA/NP/202401?expand=True", "NA_NP_202401_expand"),
    "NP_NA_reverse_expand": (
        "NA/NP/301202?expand=True&reverse=True",
        "NA_NP_301202_reverse_expand",
    ),
    "function_NA": ("NA/function/433", "NA_function_433"),
    "function_NA_2": ("NA/function/400", "NA_function_400"),
    "function_NA_reverse": ("NA/function/203?reverse=True", "NA_function_203_reverse"),
    "function_NA_expand": ("NA/function/205?expand=True", "NA_function_205_expand"),
    "function_NA_expand_no_buff": (
        "NA/function/433?expand=True",
        "NA_function_433_expand",
    ),
    "function_NA_reverse_expand": (
        "NA/function/300?expand=True&reverse=True",
        "NA_function_300_reverse_expand",
    ),
    "function_NA_unknown_buff_id": ("NA/function/4086", "NA_function_4086"),
    "buff_NA": ("NA/buff/200", "NA_buff_200"),
    "buff_NA_reverse": ("NA/buff/190?reverse=True", "NA_buff_190_reverse"),
    "item_JP": ("JP/item/7103", "JP_item_Lancer_Monument"),
    "MC_NA": ("JP/MC/20", "JP_MC_Plugsuit"),
    "CC_NA": ("NA/CC/8400110", "NA_CC_Fou"),
    "CC_NA_collectionNo": ("NA/CC/11", "NA_CC_Fou"),
    "event_NA": ("NA/event/80090", "NA_KNK_rerun"),
    "war_JP": ("JP/war/201", "JP_war_Shimousa"),
    "quest_NA": ("NA/quest/94026514", "NA_Artoria_rank_up_2"),
    "quest_phase_JP": ("JP/quest/94025012/1", "JP_Meaka_Fudou"),
    "ai_beni_cq_monkey_NA": ("NA/ai/svt/94032580", "NA_AI_Beni_CQ_monkey"),
    "kh_cq_JP": ("JP/ai/field/90161870", "JP_KH_CQ_taunt"),
    "bgm_JP_with_shop": ("JP/bgm/138?lang=en", "JP_BGM_Shinjuku"),
    "bgm_NA_without_shop": ("NA/bgm/33", "NA_BGM_battle_10"),
    "script_NA": ("NA/script/0300030510", "NA_LB3_script"),
    "shop_NA": ("NA/shop/80276219", "shop_valentine_script"),
    "eventAlloutBattle_JP": (
        "JP/eventAlloutBattle?eventId=80363",
        "eventAlloutBattle_JP",
    ),
}


test_cases = [pytest.param(*value, id=key) for key, value in test_cases_dict.items()]


@pytest.mark.asyncio
@pytest.mark.parametrize("query,result", test_cases)
async def test_raw(client: AsyncClient, query: str, result: str) -> None:
    response = await client.get(f"/raw/{query}")
    assert response.status_code == 200
    assert response.json() == get_response_data(DATA_FOLDER, result)


cases_404_dict = {
    "servant": "500",
    "equip": "3001",
    "svt": "9321362",
    "skill": "25689",
    "NP": "900205",
    "function": "90000",
    "buff": "765",
    "item": "941234",
    "MC": "62537",
    "CC": "8400111",
    "event": "12345",
    "war": "205",
    "quest": "1234567",
    "quest/94025012": "2",
    "ai/svt": "2384287349",
    "ai/field": "18738131",
    "bgm": "319028",
    "mm": "312341",
    "script": "faSdanosd",
    "shop": "1238712",
}


cases_404 = [pytest.param(key, value, id=key) for key, value in cases_404_dict.items()]


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint,item_id", cases_404)
async def test_404_raw(client: AsyncClient, endpoint: str, item_id: str) -> None:
    response = await client.get(f"/raw/JP/{endpoint}/{item_id}")
    assert response.status_code == 404
    assert response.json()["detail"][-9:] == "not found"


cases_overflow_dict = {
    "servant": "112345678910111213",
    "equip": "112345678910111213",
    "svt": "112345678910111213",
    "skill": "112345678910111213",
    "NP": "112345678910111213",
    "function": "112345678910111213",
    "buff": "12312312312312312323123",
    "item": "112345678910111213",
    "MC": "112345678910111213",
    "CC": "112345678910111213",
    "event": "112345678910111213",
    "war": "112345678910111213",
    "quest": "112345678910111213",
    "quest/112345678910111213": "1",
    "quest/94025012": "112345678910111213",
    "ai/svt": "112345678910111213",
    "ai/field": "112345678910111213",
    "bgm": "112345678910111213",
    "mm": "112345678910111213",
}


cases_overflow = [
    pytest.param(key, value, id=key) for key, value in cases_overflow_dict.items()
]


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint,item_id", cases_overflow)
async def test_int_overflow_raw(
    client: AsyncClient, endpoint: str, item_id: str
) -> None:
    response = await client.get(f"/raw/JP/{endpoint}/{item_id}")
    assert response.status_code == 404
    assert response.json()["detail"][-9:] == "not found"


cases_immutable_dict = {
    "servant": ("184", "NA_Tomoe"),
    "skill": ("24550", "NA_skill_24550"),
    "NP": ("900101", "NA_NP_900101"),
    "function": ("400", "NA_function_400"),
}


cases_immutable = [
    pytest.param(key, *value, id=key) for key, value in cases_immutable_dict.items()
]


# These are not really needed anymore since raw data uses the Pydantic objects instead of dicts now
@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint,item_id,result", cases_immutable)
async def test_immutable_master(
    client: AsyncClient, endpoint: str, item_id: str, result: str
) -> None:
    await client.get(f"/raw/NA/{endpoint}/{item_id}")
    await client.get(f"/raw/NA/{endpoint}/{item_id}?expand=True")
    response = await client.get(f"/raw/NA/{endpoint}/{item_id}")
    assert response.status_code == 200
    assert response.json() == get_response_data(DATA_FOLDER, result)


@pytest.mark.asyncio
class TestServantSpecial:
    async def test_NA_not_integer(self, client: AsyncClient) -> None:
        response = await client.get("/raw/NA/servant/asdf")
        assert response.status_code == 422

    async def test_skill_reverse_passive(self, client: AsyncClient) -> None:
        response = await client.get("/raw/NA/skill/320650?reverse=True")
        reverse_servants = {
            servant["mstSvt"]["id"]
            for servant in response.json()["reverse"]["raw"]["servant"]
        }
        assert response.status_code == 200
        assert reverse_servants == {500800}

    async def test_no_svtScript(self, client: AsyncClient) -> None:
        response = await client.get("/raw/JP/svtScript")
        assert response.status_code == 200
        assert response.json() == []

    async def test_skill_reverse_CC(self, client: AsyncClient) -> None:
        response = await client.get("/raw/JP/skill/991970?reverse=True")
        reverse_ccs = {
            cc["mstCommandCode"]["id"] for cc in response.json()["reverse"]["raw"]["CC"]
        }
        assert response.status_code == 200
        assert reverse_ccs == {8400500}

    async def test_buff_reverse_skillNp(self, client: AsyncClient) -> None:
        response = await client.get(
            "/raw/NA/buff/202?reverse=True&reverseDepth=skillNp"
        )
        assert response.status_code == 200
        assert response.json()["reverse"]["raw"]["function"][0]["reverse"]["raw"][
            "skill"
        ]

    async def test_function_reverse_servant(self, client: AsyncClient) -> None:
        response = await client.get(
            "/raw/NA/function/3410?reverse=True&reverseDepth=servant"
        )
        assert response.status_code == 200
        assert response.json()["reverse"]["raw"]["skill"][0]["reverse"]["raw"][
            "servant"
        ]

    async def test_buff_reverse_function_vals_actual_buff(
        self, client: AsyncClient
    ) -> None:
        response = await client.get("/raw/NA/buff/101?reverse=True")
        assert response.status_code == 200
        assert {
            function["mstFunc"]["funcType"]
            for function in response.json()["reverse"]["raw"]["function"]
        }.isdisjoint(FUNC_VALS_NOT_BUFF)

    async def test_hyde_voice_id(self, client: AsyncClient) -> None:
        response = await client.get("/raw/NA/servant/600700?lore=true")
        assert response.status_code == 200
        assert any(voice["id"] == 600710 for voice in response.json()["mstSvtVoice"])

    async def test_war_spots_from_multiple_maps(self, client: AsyncClient) -> None:
        response = await client.get("/raw/NA/war/9033")
        assert {spot["warId"] for spot in response.json()["mstSpot"]} == {9033, 9034}

    async def test_scripts_first_run(self, client: AsyncClient) -> None:
        response = await client.get("/raw/JP/quest/94035033/2")
        assert response.json()["scripts"] == ["9403503320"]

    async def test_master_mission(self, client: AsyncClient) -> None:
        response = await client.get("/raw/NA/mm/10001")
        assert response.status_code == 200
        data = response.json()
        assert data.get("mstMasterMission") is not None
        assert len(data["mstEventMission"]) > 0

    async def test_empty_eventAlloutBattle(self, client: AsyncClient) -> None:
        response = await client.get("/raw/JP/eventAlloutBattle")
        assert len(response.json()) == 0


def test_get_quest_id_from_conds() -> None:
    conds = load_master_data(test_gamedata, MstEventMissionCondition)
    cond_details = load_master_data(test_gamedata, MstEventMissionConditionDetail)
    assert get_quest_ids_in_conds(conds, cond_details) == {
        93030306,
        94002213,
        94002214,
        94002215,
        93000613,
        93000107,
        93020207,
        93000208,
        93020210,
        93020306,
        94002109,
    }
