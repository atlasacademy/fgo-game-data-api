import orjson
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio.engine import AsyncConnection

from app.core.nice.enemy import get_enemy_script
from app.core.nice.svt.voice import get_nice_voice_line
from app.data.shop import get_shop_cost_item_id
from app.data.utils import load_master_data
from app.db.helpers import event
from app.schemas.base import HttpUrlAdapter
from app.schemas.common import Language, Region
from app.schemas.nice import ExtraAssetsUrl
from app.schemas.raw import MstSvtVoice, MstVoice

from .utils import clear_drop_data, get_response_data, test_gamedata


test_cases_dict: dict[str, tuple[str, str]] = {
    "servant_NA_collectionNo": ("NA/servant/105", "NA_Billy"),
    "servant_NA_id": ("NA/servant/201000", "NA_Billy"),
    "servant_NA_lore_costume": ("NA/servant/96?lore=True", "NA_Dantes_lore_costume"),
    "servant_JP_collectionNo": ("JP/servant/283", "JP_Elice"),
    "servant_JP_id": ("JP/servant/304300", "JP_Elice"),
    "servant_JP_collection_servant": ("JP/servant/149", "JP_Tiamat"),
    "servant_JP_costume": ("JP/servant/1", "JP_Mash"),
    "servant_JP_multiple_NPs_space_istar": ("JP/servant/268", "JP_Space_Ishtar"),
    "servant_charaGraph_change": ("JP/servant/277", "JP_Ody"),
    "svt_material_td_JP": ("JP/svt/404601", "JP_Liz_td_material"),
    "skill_NA_id": ("NA/skill/454650", "NA_Fujino_1st_skill"),
    "skill_NA_reverse": ("NA/skill/19450?reverse=True", "NA_Fionn_1st_skill_reverse"),
    "skill_NA_reverse_basic": (
        "NA/skill/992154?reverse=true&reverseData=basic",
        "NA_skill_generous_earth_reverse_basic",
    ),
    "skill_JP_dependFunc": ("JP/skill/671650", "JP_Melt_skill_dependFunc"),
    "skill_JP_dependFunc_colon": ("JP/skill/711550", "JP_Yang_Guifei_skill"),
    "skill_JP_SelectAddInfo": ("JP/skill/2189551", "JP_skill_2189551"),
    "NP_JP_id": ("JP/NP/301101", "JP_Fionn_NP"),
    "NP_JP_reverse": ("JP/NP/202901?reverse=True", "JP_Fujino_NP_reverse"),
    "NP_CN_without_svtTd": ("CN/NP/603002", "CN_NP_without_svtTd"),
    "NP_NA_reverse_basic": (
        "NA/NP/100801?reverse=true&reverseData=basic",
        "NA_NP_Siegfried_reverse_basic",
    ),
    "function_NA_id": ("NA/function/400", "NA_function_400"),
    "function_NA_reverse": ("NA/function/298?reverse=True", "NA_function_298_reverse"),
    "function_NA_reverse_basic": (
        "NA/function/300?reverse=true&reverseData=basic",
        "NA_function_300_reverse_basic",
    ),
    "buff_NA_id": ("NA/buff/300", "NA_buff_300"),
    "buff_JP_buff_rate": ("JP/buff/3711", "NA_buff_3711"),
    "buff_NA_reverse": ("NA/buff/267?reverse=True", "NA_buff_267_reverse"),
    "buff_JP_reverse_basic": (
        "JP/buff/search?type=specialInvincible&reverse=true&reverseData=basic&reverseDepth=servant&lang=en",
        "JP_buff_special_invincible_reverse",
    ),
    "buff_convert": ("JP/buff/5326", "JP_buff_convert"),
    "equip_JP_collectionNo": ("JP/equip/683", "JP_Aerial_Drive"),
    "equip_JP_id": ("JP/equip/9402750", "JP_Aerial_Drive"),
    "svt_NA_id": ("NA/svt/9939120", "NA_svt_9939120"),
    "svt_JP_enemy_costume": ("JP/svt/9100101", "JP_svt_9100101"),
    "item_NA_id": ("NA/item/94000201", "NA_item_94000201"),
    "item_exchange_ticket": ("NA/item/15000", "NA_item_15000"),
    "MC_NA_id": ("NA/MC/110", "NA_MC_LB"),
    "MC_JP_costume": ("JP/MC/120?lang=en", "JP_MC_Tropical_Summer"),
    "JP_CC_id": ("JP/CC/8400550", "JP_CC_8400550"),
    "JP_CC_collectionNo": ("JP/CC/55", "JP_CC_8400550"),
    "event_JP_id": ("JP/event/80289", "JP_Guda_5"),
    "event_rerward_NA": ("NA/event/80018", "NA_event_Rashomon"),
    "event_tower_JP": ("NA/event/80088", "NA_event_Setsubun"),
    "event_lottery_NA": ("NA/event/80087", "NA_event_Da_Vinci_rerun"),
    "event_treasureBox_JP": ("JP/event/80331", "JP_Summer_Adventure"),
    "event_digging_JP": ("JP/event/80367", "JP_event_Digging"),
    "event_bulletin_cooltime_JP": ("JP/event/80384", "JP_proto_merlin_summer"),
    "event_recipe_JP": ("JP/event/80391", "JP_tea_recipe"),
    "event_fortification_JP": ("JP/event/80400", "JP_event_fortification"),
    "event_campaign_JP": ("JP/event/71090", "JP_event_campaign"),
    "event_random_mission_JP": ("JP/event/80346", "JP_event_random_mission"),
    "war_NA_id": ("NA/war/203", "NA_war_Shimousa"),
    "war_JP_quest_selection": ("JP/war/8377", "JP_war_quest_selection"),
    "quest_JP_id": ("JP/quest/91103002", "JP_Suzuka_rank_up"),
    "quest_NA_id_phase": ("NA/quest/94020187/1", "NA_87th_floor"),
    "quest_NA_consume_item": ("NA/quest/94032412", "NA_Enma_tei_spa_room"),
    "quest_NA_enemy": ("NA/quest/94034503/1", "NA_CCC_Detour_3"),
    "quest_NA_enemy_cache": ("NA/quest/94034503/1", "NA_CCC_Detour_3"),
    "quest_JP_remapped": ("JP/quest/94060012/1", "JP_remapped_quest"),
    "quest_JP_support_servant": ("JP/quest/94051406/1", "JP_support_servant"),
    "quest_NA_select_0": ("NA/quest/3000109/1", "NA_quest_LB1_select_0"),
    "quest_NA_select_1": ("NA/quest/3000110/1", "NA_quest_LB1_select_1"),
    "quest_JP_2_gift_adds": ("JP/quest/94067702", "JP_Teslafest_quest"),
    "quest_follower_deck_index": ("JP/quest/3000903/3", "JP_LB6_support_deck"),
    "quest_aiNpc": ("JP/quest/94074510/1", "JP_Himiko_AI_NPC"),
    "ai_beni_cq_monkey_NA": ("NA/ai/svt/94032580", "NA_AI_Beni_CQ_monkey"),
    "ai_act_np": ("JP/ai/svt/94074555", "JP_AI_Act_NP"),
    "kh_cq_JP": ("JP/ai/field/90161870", "JP_KH_CQ_taunt"),
    "bgm_NA_with_shop": ("JP/bgm/138?lang=en", "JP_BGM_Shinjuku"),
    "bgm_NA_without_shop": ("NA/bgm/35", "NA_BGM_event_8"),
    "script_NA_2_quests": ("NA/script/9402750110", "NA_Summerfes_script"),
    "script_JP_no_quest": ("NA/script/WarEpilogue108", "JP_WarEpilogue108"),
    "shop_JP": ("JP/shop/13000000", "JP_shop_blue_apple"),
    "shop_set_item": ("NA/shop/6000189", "NA_shop_set_item"),
    "common_release": ("NA/common-release/470211", "NA_release_470211"),
}


test_cases = [pytest.param(*value, id=key) for key, value in test_cases_dict.items()]


@pytest.mark.asyncio
@pytest.mark.parametrize("query,result", test_cases)
async def test_nice(client: AsyncClient, query: str, result: str) -> None:
    response = await client.get(f"/nice/{query}")
    test_data = response.json()
    if "quest" in query and len(query.split("/")) == 4:
        test_data = clear_drop_data(test_data)
    assert response.status_code == 200
    assert test_data == get_response_data("test_data_nice", result)


cases_404_dict = {
    "servant": "500",
    "equip": "3001",
    "svt": "987626",
    "skill": "25689",
    "NP": "900205",
    "function": "90000",
    "buff": "765",
    "item": "941234",
    "MC": "62537",
    "CC": "8400631",
    "event": "12313",
    "war": "98765",
    "quest": "1234567",
    "quest/94025012": "2",
    "ai/svt": "54234",
    "ai/field": "45234",
    "bgm": "31234",
    "mm": "41232",
    "script": "dasdasd",
    "shop": "1238712",
}


cases_404 = [pytest.param(key, value, id=key) for key, value in cases_404_dict.items()]


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint,item_id", cases_404)
async def test_404_nice(client: AsyncClient, endpoint: str, item_id: str) -> None:
    response = await client.get(f"/nice/JP/{endpoint}/{item_id}")
    assert response.status_code == 404
    assert response.json()["detail"][-9:] == "not found"


cases_datavals_dict = {
    "test_dataVals_event_point_up": (
        940004,
        0,
        {"Individuality": 10132, "EventId": 80046, "RateCount": 1000},
    ),
    "test_dataVals_event_drop_up": (
        990098,
        1,
        {"Individuality": 10005, "EventId": 80030, "AddCount": 3},
    ),
    "test_dataVals_event_drop_rate_up": (
        990139,
        2,
        {"Individuality": 10018, "EventId": 80034, "AddCount": 400},
    ),
    "test_dataVals_enemy_encount_rate_up": (
        990315,
        2,
        {"Individuality": 2023, "EventId": 80087, "RateCount": 1000},
    ),
    "test_dataVals_class_drop_up": (990326, 2, {"EventId": 80017, "AddCount": 3}),
    "test_dataVals_enemy_prob_down": (
        960549,
        0,
        {"Individuality": 100, "EventId": 80043, "RateCount": 0},
    ),
    "test_dataVals_servant_friendship_up_rate": (
        990554,
        0,
        {"Individuality": 0, "RateCount": 20},
    ),
    "test_dataVals_servant_friendship_up_add": (
        990199,
        0,
        {"Individuality": 0, "AddCount": 50},
    ),
    "test_dataVals_item_drop_rate_up": (
        992948,
        0,
        {"Individuality": 20042, "EventId": 0, "DropRateCount": 250},
    ),
    "test_dataVals_servant_friendpoint_up_add": (990071, 0, {"AddCount": 75}),
    "test_dataVals_servant_friendpoint_up_dupe_add": (992320, 0, {"AddCount": 10}),
    "test_dataVals_master_exp_up_rate": (990311, 0, {"RateCount": 20}),
    "test_dataVals_master_exp_up_add": (991128, 0, {"AddCount": 50}),
    "test_dataVals_equip_exp_up_rate": (990416, 0, {"RateCount": 100}),
    "test_dataVals_equip_exp_up_add": (990932, 0, {"AddCount": 50}),
    "test_dataVals_qp_drop_up_rate": (990158, 0, {"RateCount": 100}),
    "test_dataVals_qp_drop_up_add": (990665, 0, {"AddCount": 2017}),
    "test_dataVals_subState_Value2": (
        631000,
        1,
        {"Rate": 1000, "Value": 0, "Value2": 1},
    ),
    "test_fkl_transform_": (
        888550,
        0,
        {"Rate": 5000, "Value": 304800, "Target": 0, "SetLimitCount": 3},
    ),
    "test_trailing_comma": (
        966964,
        0,
        {
            "Rate": 5000,
            "Turn": -1,
            "Count": 1,
            "Value": 967006,
            "Value2": 1,
            "ShowState": -1,
        },
    ),
}


cases_datavals = [
    pytest.param(*value, id=key) for key, value in cases_datavals_dict.items()
]


@pytest.mark.asyncio
@pytest.mark.parametrize("skill_id,function_index,parse_result", cases_datavals)
async def test_special_datavals(
    client: AsyncClient,
    skill_id: int,
    function_index: int,
    parse_result: dict[str, int],
) -> None:
    response = await client.get(f"/nice/JP/skill/{skill_id}")
    assert response.status_code == 200
    assert response.json()["functions"][function_index]["svals"][0] == parse_result


@pytest.mark.asyncio
async def test_datavals_default_case_target(client: AsyncClient) -> None:
    response = await client.get("/nice/NA/NP/600701")
    assert response.status_code == 200
    assert response.json()["functions"][0]["svals"][0] == {
        "Rate": 5000,
        "Value": 600710,
        "Target": 0,
    }


@pytest.mark.asyncio
async def test_list_datavals_2_items(client: AsyncClient) -> None:
    response = await client.get("/nice/JP/NP/403401")
    assert response.status_code == 200
    assert response.json()["functions"][0]["svals"][0] == {
        "Rate": 1000,
        "Value": 6000,
        "Target": 0,
        "Correction": 1500,
        "TargetRarityList": [1, 2],
    }


@pytest.mark.asyncio
async def test_list_datavals_1_item(client: AsyncClient) -> None:
    response = await client.get("/nice/JP/NP/304201")
    assert response.status_code == 200
    assert response.json()["functions"][0]["svals"][0] == {
        "Rate": 1000,
        "Value": 3000,
        "Value2": 1000,
        "Target": 1,
        "Correction": 200,
        "TargetList": [2004],
        "ParamAddMaxCount": 10,
    }


@pytest.mark.asyncio
async def test_dataval_add_field(client: AsyncClient) -> None:
    response = await client.get("/nice/JP/NP/2300501")
    assert response.status_code == 200
    assert response.json()["functions"][0]["svals"][0] == {
        "Rate": 1000,
        "Turn": 3,
        "Count": -1,
        "FieldIndividuality": 2829,
        "TakeOverFieldState": 1,
        "RemoveFieldBuffActorDeath": 1,
        "FieldBuffGrantType": 2,
    }


@pytest.mark.asyncio
class TestServantSpecial:
    async def test_NA_not_integer(self, client: AsyncClient) -> None:
        response = await client.get("/nice/NA/servant/lkji")
        assert response.status_code == 422

    async def test_JP_Emiya_all_nps(self, client: AsyncClient) -> None:
        response = await client.get("/nice/JP/servant/11")
        nps = {np["id"] for np in response.json()["noblePhantasms"]}
        assert response.status_code == 200
        assert nps == {200101, 200102, 200198, 200197}

    async def test_skill_reverse_passive(self, client: AsyncClient) -> None:
        response = await client.get("/nice/NA/skill/30650?reverse=True")
        reverse_servants = {
            servant["id"] for servant in response.json()["reverse"]["nice"]["servant"]
        }
        assert response.status_code == 200
        assert reverse_servants == {201200, 401800, 601000}

    async def test_JP_English_name(self, client: AsyncClient) -> None:
        response = await client.get("/nice/JP/servant/304300?lang=en")
        assert response.status_code == 200
        assert response.json()["name"] == "Utsumi Erice"

        response = await client.get("/nice/JP/equip/1296?lang=en")
        assert response.status_code == 200
        assert response.json()["name"] == "Hell's Kitchen"

    async def test_JP_skill_English_name(self, client: AsyncClient) -> None:
        response = await client.get("/nice/JP/skill/991604?lang=en")
        assert response.status_code == 200
        assert response.json()["name"] == "Paradox Ace Killer"

    async def test_JP_CC_English_name(self, client: AsyncClient) -> None:
        response = await client.get("/nice/JP/CC/8400240?lang=en")
        assert response.status_code == 200
        assert response.json()["name"] == "The Holy Night's Aurora"

    async def test_CE_bond_owner(self, client: AsyncClient) -> None:
        for endpoint in ("equip", "svt"):
            yu_bond_ce = await client.get(f"/nice/NA/{endpoint}/9303460")
            assert yu_bond_ce.json()["bondEquipOwner"] == 603500

    async def test_CE_valentine_owner(self, client: AsyncClient) -> None:
        for endpoint in ("equip", "svt"):
            yu_valentine_ce = await client.get(f"/nice/NA/{endpoint}/9807110")
            assert yu_valentine_ce.json()["valentineEquipOwner"] == 603500

    async def test_empty_cv_illustrator_name(self, client: AsyncClient) -> None:
        response = await client.get("/nice/JP/svt/9941330?lore=true")
        assert response.status_code == 200
        assert response.json()["profile"]["cv"] == ""
        assert response.json()["profile"]["illustrator"] == ""

    async def test_buff_reverse_skillNp(self, client: AsyncClient) -> None:
        response = await client.get(
            "/nice/NA/buff/203?reverse=True&reverseDepth=skillNp"
        )
        f_with_skill = next(
            func
            for func in response.json()["reverse"]["nice"]["function"]
            if func["funcId"] == 641
        )

        assert response.status_code == 200
        assert f_with_skill["reverse"]["nice"]["skill"]

    async def test_function_reverse_servant(self, client: AsyncClient) -> None:
        response = await client.get(
            "/nice/NA/function/3411?reverse=True&reverseDepth=servant"
        )
        assert response.status_code == 200
        assert response.json()["reverse"]["nice"]["skill"][0]["reverse"]["nice"][
            "servant"
        ]

    async def test_solomon_cvId(self, client: AsyncClient) -> None:
        response = await client.get("/nice/JP/servant/83?lore=true")
        assert response.status_code == 200
        assert response.json()["profile"]["cv"] == ""

    async def test_voice_play_cond(self, client: AsyncClient) -> None:
        response = await client.get("/nice/JP/servant/261?lore=true")
        voice_line = response.json()["profile"]["voices"][0]["voiceLines"][4]
        assert response.status_code == 200
        assert voice_line["playConds"] == [
            {
                "condGroup": 1,
                "condType": "playerGenderType",
                "targetId": 1,
                "condValue": 0,
                "condValues": [0],
            }
        ]

    async def test_script_svt_SkillRankUp(self, client: AsyncClient) -> None:
        response = await client.get("/nice/JP/servant/285")
        assert response.status_code == 200
        expected = {
            "767650": [],
            "682450": [964647, 964648, 964648, 964648],
            "768550": [964649, 964650, 964650, 964650],
        }
        assert response.json()["script"]["SkillRankUp"] == expected

    async def test_script_svt_svtBuffTurnExtend(self, client: AsyncClient) -> None:
        response = await client.get("/nice/JP/servant/336")
        assert response.status_code == 200
        assert response.json()["script"]["svtBuffTurnExtend"] is True

    async def test_script_STAR_HIGHER_Moriarty(self, client: AsyncClient) -> None:
        response = await client.get("/nice/NA/skill/334552")
        assert response.status_code == 200
        assert response.json()["script"] == {
            "STAR_HIGHER": [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
        }

    async def test_script_NP_Crane(self, client: AsyncClient) -> None:
        response = await client.get("/nice/JP/NP/504601")
        assert response.status_code == 200
        assert response.json()["script"] == {"STAR_HIGHER": [20, 20, 20, 20, 20]}

    async def test_script_followerVals_Be_Graceful(self, client: AsyncClient) -> None:
        response = await client.get("/nice/NA/skill/991370")
        assert response.status_code == 200
        assert response.json()["functions"][0]["followerVals"] == [{"RateCount": 150}]

    async def test_buff_script_relationId(self, client: AsyncClient) -> None:
        response = await client.get("/nice/JP/buff/2585")
        assert response.status_code == 200
        expected = {
            "atkSide": {
                "assassin": {"alterEgo": {"damageRate": 2000, "type": "overwriteForce"}}
            },
            "defSide": {
                "alterEgo": {"assassin": {"damageRate": 500, "type": "overwriteForce"}}
            },
        }
        assert response.json()["script"]["relationId"] == expected

        response_2 = await client.get("/nice/JP/buff/2576")
        assert response_2.status_code == 200
        expected_2 = {
            "atkSide": {},
            "defSide": {
                "alterEgo": {
                    "saber": {"damageRate": 1500, "type": "overwriteForce"},
                    "assassin": {"damageRate": 1500, "type": "overwriteForce"},
                }
            },
        }
        assert response_2.json()["script"]["relationId"] == expected_2

    async def test_buff_DamageRelease(self, client: AsyncClient) -> None:
        response = await client.get("/nice/JP/buff/2935")
        assert response.status_code == 200
        assert response.json()["script"] == {
            "ReleaseText": "睡眠解除",
            "DamageRelease": 1,
        }

    async def test_buff_checkIndvType(self, client: AsyncClient) -> None:
        response = await client.get("/nice/JP/buff/1831")
        assert response.json()["script"] == {"checkIndvType": 1}

    async def test_buff_CheckOpponentBuffTypes(self, client: AsyncClient) -> None:
        response = await client.get("/nice/JP/buff/3313")
        assert response.json()["script"] == {
            "CheckOpponentBuffTypes": [
                "avoidance",
                "invincible",
                "avoidanceIndividuality",
            ]
        }

    async def test_negative_trait(self, client: AsyncClient) -> None:
        response = await client.get("/nice/JP/buff/2966")
        expected = {"id": 4101, "name": "aoeNP", "negative": True}
        assert response.status_code == 200
        assert response.json()["ckOpIndv"][0] == expected

    async def test_ascension_trait(self, client: AsyncClient) -> None:
        response = await client.get("/nice/JP/servant/603700")
        ascension_traits = response.json()["ascensionAdd"]["individuality"]["ascension"]

        zero_ascension = {trait["name"] for trait in ascension_traits["0"]}
        third_ascension = {trait["name"] for trait in ascension_traits["3"]}

        assert response.status_code == 200
        assert "childServant" in zero_ascension
        assert "childServant" not in third_ascension
        assert "levitating" not in zero_ascension
        assert "levitating" in third_ascension

    async def test_servant_change(self, client: AsyncClient) -> None:
        response = await client.get("/nice/NA/servant/184")
        assert response.status_code == 200
        assert response.json()["svtChange"][0]["name"] == "Archer of Inferno"

    async def test_costume_charaFigure_form(self, client: AsyncClient) -> None:
        response = (await client.get("/nice/JP/servant/126")).json()
        assert "costume" in response["extraAssets"]["charaFigureForm"]["1"]
        assert "costume" in response["extraAssets"]["charaFigureForm"]["2"]

    async def test_image_assets(self, client: AsyncClient) -> None:
        response = await client.get("/nice/JP/servant/203200")
        assert response.json()["extraAssets"]["image"]["story"]["0"].endswith(
            "Image/cut084_jnn/cut084_jnn.png"
        )

    async def test_charaGraphEx(self, client: AsyncClient) -> None:
        response = await client.get("/nice/JP/servant/316")
        assert response.json()["extraAssets"]["charaGraphEx"]["ascension"][
            "4"
        ].endswith("JP/CharaGraph/CharaGraphEx/2800100/2800100b@2.png")

    async def test_charaGraphExCostume(self, client: AsyncClient) -> None:
        response = await client.get("/nice/JP/servant/247")
        assert response.json()["extraAssets"]["charaGraphEx"]["costume"][
            "703330"
        ].endswith("JP/CharaGraph/CharaGraphEx/703330/703330a.png")

    async def test_charaFigureMulti(self, client: AsyncClient) -> None:
        response = await client.get("/nice/JP/servant/327")
        assert response.json()["extraAssets"]["charaFigureMulti"]["1"]["ascension"][
            "1"
        ].endswith("JP/CharaFigure/5049900/5049900_merged.png")

    async def test_skillAdd(self, client: AsyncClient) -> None:
        response = await client.get("/nice/JP/skill/900250")
        assert response.json()["skillAdd"] == [
            {
                "priority": 0,
                "releaseConditions": [
                    {
                        "id": 40061904,
                        "priority": 0,
                        "condGroup": 0,
                        "condType": "questClear",
                        "condId": 3001009,
                        "condNum": 0,
                    }
                ],
                "name": "対人理 D",
                "ruby": "たいじんり",
            }
        ]

    async def test_war_banner(self, client: AsyncClient) -> None:
        cases = {
            9050: "event_war_",
            303: "questboard_cap",  # main scenario
            9088: "event_war_",  # main interlude
            1003: "chaldea_category_",  # interlude
            11000: "questboard_cap",  # arc 1
            8372: "chaldea_category_",  # subFolder
        }
        for warId, prefix in cases.items():
            war = await client.get(f"nice/JP/war/{warId}")
            assert war.status_code == 200
            assert prefix in war.json()["banner"]

    async def test_skill_ai_id(self, client: AsyncClient) -> None:
        nice_skill = await client.get("/nice/NA/skill/962219")
        assert nice_skill.json()["aiIds"]["field"] == [94031791]

    async def test_overwrite_script(self, client: AsyncClient) -> None:
        summer_okita = await client.get("/nice/JP/servant/267?lang=en")
        ascensionAdd = summer_okita.json()["ascensionAdd"]

        overWriteServantName = ascensionAdd["overWriteServantName"]
        overWriteTDName = ascensionAdd["overWriteTDName"]
        overWriteTDFileName = ascensionAdd["overWriteTDFileName"]

        assert overWriteServantName["ascension"]["1"] == "Okita J. Souji"
        assert (
            overWriteTDName["ascension"]["1"] == "The Mumyou's Light Radiates at Dawn"
        )
        assert overWriteTDFileName["ascension"]["1"].endswith(
            "JP/Servants/Commands/604000/604010.png"
        )

    async def test_charaGraphName(self, client: AsyncClient) -> None:
        miyu = await client.get("/nice/NA/servant/236")
        for i, image_url in miyu.json()["extraAssets"]["charaGraphName"][
            "ascension"
        ].items():
            assert image_url.endswith(f"NA/CharaGraph/504100/504100name@{i}.png")

    async def test_event_point_buff(self, client: AsyncClient) -> None:
        oniland = await client.get("/nice/NA/event/80119")
        oniland_point_buff = oniland.json()["pointBuffs"][1]
        oniland_point_buff.pop("detail")
        assert oniland_point_buff["icon"].endswith("NA/Items/94030201.png")
        oniland_point_buff.pop("icon")
        assert oniland_point_buff == {
            "id": 94030201,
            "funcIds": [
                2991,
                2992,
                2993,
            ],
            "groupId": 0,
            "eventPoint": 350000,
            "name": "Event Special Attack damage +40% (Total + 40%)",
            "background": "gold",
            "value": 1400,
        }

    async def test_master_mission(self, client: AsyncClient) -> None:
        response = await client.get("/nice/NA/mm/10001")
        assert response.status_code == 200
        data = response.json()
        assert len(data["missions"]) > 0

    async def test_quest_phase_detail_override(self, client: AsyncClient) -> None:
        story_quest = await client.get("nice/JP/quest/94034001/2")
        assert story_quest.json()["consume"] == 0

    async def test_quest_enemy_name_translation(self, client: AsyncClient) -> None:
        LB3_quest_JP = (await client.get("nice/JP/quest/3000305/2?lang=en")).json()
        assert LB3_quest_JP["stages"][0]["enemies"][0]["name"] == "Krichat' A"
        assert LB3_quest_JP["stages"][1]["enemies"][2]["name"] == "Krichat' C"
        heroine_x = (await client.get("nice/JP/quest/94014409/3?lang=en")).json()
        assert heroine_x["stages"][1]["enemies"][0]["name"] == "Heroine X"

    async def test_latest_story_war_banner(self, client: AsyncClient) -> None:
        latest_story_war = await client.get("nice/NA/war/308")
        assert "questboard_cap_closed" in latest_story_war.json()["banner"]

    async def test_enemy_script(self, client: AsyncClient) -> None:
        murasaki_valentine_cq = await client.get("nice/NA/quest/94033599/1")
        first_stage_enemies = murasaki_valentine_cq.json()["stages"][0]["enemies"]
        assert first_stage_enemies[0]["enemyScript"]["call"] == [94033697]
        assert first_stage_enemies[5]["enemyScript"]["leader"] is True

        test_script = {"kill": 3, "changeAttri": 2, "forceDropItem": 1}
        parsed_script = get_enemy_script(test_script).json(exclude_unset=True)
        assert orjson.loads(parsed_script) == {
            "changeAttri": "sky",
            "deathType": "effect",
            "forceDropItem": True,
        }

    async def test_enemy_isAddition_skipped(self, client: AsyncClient) -> None:
        weakness_ear = (await client.get("/nice/NA/quest/94034116/1")).json()
        assert [len(stage["enemies"]) for stage in weakness_ear["stages"]] == [3, 3, 3]

    async def test_field_ai_stage(self, client: AsyncClient) -> None:
        tiamat_battle = await client.get("/nice/NA/quest/1000721/3")
        assert tiamat_battle.json()["stages"][0]["fieldAis"][0] == {
            "day": 0,
            "id": 107050,
        }

    async def test_stage_call(self, client: AsyncClient) -> None:
        lb_beast_iv_final_battle = (
            await client.get("/nice/JP/quest/94065004/1")
        ).json()
        assert lb_beast_iv_final_battle["stages"][0]["call"] == [
            94065063,
            94065062,
            94065064,
            94065065,
            94065066,
            94065067,
            94065069,
            94065068,
        ]
        assert len(lb_beast_iv_final_battle["stages"][0]["enemies"]) == 12

    async def test_get_all_call_shift_enemies(self, client: AsyncClient) -> None:
        ccc_suzuka_1 = await client.get("/nice/NA/quest/94034017/1")
        assert len(ccc_suzuka_1.json()["stages"][0]["enemies"]) == 2
        ccc_suzuka_2 = await client.get("/nice/NA/quest/94034017/2")
        assert len(ccc_suzuka_2.json()["stages"][0]["enemies"]) == 4
        db = await client.get("/nice/NA/quest/94034020/1")
        assert [enemy["npcId"] for enemy in db.json()["stages"][0]["enemies"]] == list(
            range(94034125, 94034133)
        )

    async def test_set_item(self, client: AsyncClient) -> None:
        valentine_2018 = await client.get("/nice/NA/event/80010")
        tamamo_cat_shop = valentine_2018.json()["shop"][79]
        assert tamamo_cat_shop["itemSet"][1] == {
            "id": 8001089,
            "purchaseType": "servant",
            "targetId": 9804500,
            "setNum": 1,
            "gifts": [],
        }

    async def test_enemy_change_class(self, client: AsyncClient) -> None:
        ooku_mirage_room = await client.get("/nice/NA/quest/94037503/1")
        last_enemy = ooku_mirage_room.json()["stages"][2]["enemies"][2]
        assert last_enemy["svt"]["className"] == "saber"

    async def test_shop_script(self, client: AsyncClient) -> None:
        valentine_2020 = await client.get("/nice/NA/event/80233")
        yu_mei_ren_shop = valentine_2020.json()["shop"][229]
        assert yu_mei_ren_shop["scriptName"] == "Modern Return Sweets"
        assert yu_mei_ren_shop["scriptId"] == "9403353120"

    async def test_shop_free(self, client: AsyncClient) -> None:
        waltz_colab = await client.get("/nice/JP/event/80319")
        euryale_costume_shop = waltz_colab.json()["shop"][30]
        assert euryale_costume_shop["cost"]["item"]["id"] == 0

    async def test_quest_script(self, client: AsyncClient) -> None:
        lb2_main_quest = await client.get("/nice/NA/quest/3000202/3")
        scriptIds = [script["scriptId"] for script in lb2_main_quest.json()["scripts"]]
        assert scriptIds == ["0300020230", "0300020231"]

    async def test_quest_message(self, client: AsyncClient) -> None:
        babylonia_reflection_3 = await client.get("/nice/NA/quest/94042403/1")
        idxs = [message["idx"] for message in babylonia_reflection_3.json()["messages"]]
        assert idxs == [0, 1, 2, 3]

    async def test_anni_drop_change(self, client: AsyncClient) -> None:
        anni_drop_change = (await client.get("/nice/NA/quest/93030706/3")).json()
        drops = [
            (drop["type"], drop["objectId"], drop["num"])
            for drop in anni_drop_change["drops"]
        ]
        assert ("item", 1, 20000) in drops

    async def test_transform_enemy(self, client: AsyncClient) -> None:
        transform_enemy = (await client.get("/nice/NA/quest/94050181/2")).json()
        for stage in transform_enemy["stages"]:
            decks = {enemy["deck"] for enemy in stage["enemies"]}
            if stage["wave"] == 3:
                assert "transform" in decks
            else:
                assert "transform" not in decks


@pytest.mark.asyncio
async def test_shop_itemIds_0(na_db_conn: AsyncConnection) -> None:
    assert get_shop_cost_item_id(await event.get_mstShop_by_id(na_db_conn, 1)) == 4
    assert (
        get_shop_cost_item_id(await event.get_mstShop_by_id(na_db_conn, 11000000)) == 3
    )


def test_nice_voice_summon_script() -> None:
    raw_voice = load_master_data(test_gamedata, MstVoice)
    mstVoices = {voice.id: voice for voice in raw_voice}

    raw_svt_voice = load_master_data(test_gamedata, MstSvtVoice)[0]
    nice_voice = get_nice_voice_line(
        Region.JP,
        raw_svt_voice.scriptJson[0],
        raw_svt_voice.id,
        raw_svt_voice.voicePrefix,
        raw_svt_voice.type,
        {},
        {},
        [],
        mstVoices,
        [],
        Language.jp,
    )

    expected = get_response_data("test_data_nice", "svt_voice_summon_script")
    assert orjson.loads(nice_voice.json()) == expected


def test_asset_set_url() -> None:
    assets_url = ExtraAssetsUrl()
    url = HttpUrlAdapter.validate_python("https://example.com")
    costume_ids = {11: 100011, 12: 100012}

    assets_url.set_limit_asset(11, url, costume_ids)
    assets_url.set_limit_asset(12, url, costume_ids)
    assets_url.set_limit_asset(1, url, costume_ids)
    assets_url.set_limit_asset(4, url, costume_ids)

    assert assets_url.model_dump() == {
        "ascension": {2: url, 4: url},
        "costume": {100011: url, 100012: url},
        "cc": None,
        "equip": None,
        "story": None,
    }
