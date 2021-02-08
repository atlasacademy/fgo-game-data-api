# pylint: disable=R0201,R0904
from typing import Dict, Tuple

import pytest
from fastapi.testclient import TestClient

from app.core.nice import get_nice_shop
from app.db.base import engines
from app.db.helpers import event
from app.main import app
from app.schemas.common import Region

from .utils import get_response_data


client = TestClient(app)


test_cases_dict: Dict[str, Tuple[str, str]] = {
    "servant_NA_collectionNo": ("NA/servant/105", "NA_Billy"),
    "servant_NA_id": ("NA/servant/201000", "NA_Billy"),
    "servant_NA_lore_costume": ("NA/servant/96?lore=True", "NA_Dantes_lore_costume"),
    "servant_JP_collectionNo": ("JP/servant/283", "JP_Elice"),
    "servant_JP_id": ("JP/servant/304300", "JP_Elice"),
    "servant_JP_collection_servant": ("JP/servant/149", "JP_Tiamat"),
    "servant_JP_costume": ("JP/servant/1", "JP_Mash"),
    "servant_JP_multiple_NPs_space_istar": ("JP/servant/268", "JP_Space_Ishtar"),
    "skill_NA_id": ("NA/skill/454650", "NA_Fujino_1st_skill"),
    "skill_NA_reverse": ("NA/skill/19450?reverse=True", "NA_Fionn_1st_skill_reverse"),
    "skill_NA_reverse_basic": (
        "NA/skill/992154?reverse=true&reverseData=basic",
        "NA_skill_generous_earth_reverse_basic",
    ),
    "skill_JP_dependFunc": ("JP/skill/671650", "JP_Melt_skill_dependFunc"),
    "skill_JP_dependFunc_colon": ("JP/skill/711550", "JP_Yang_Guifei_skill"),
    "NP_JP_id": ("JP/NP/301101", "JP_Fionn_NP"),
    "NP_JP_reverse": ("JP/NP/202901?reverse=True", "JP_Fujino_NP_reverse"),
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
    "buff_NA_reverse": ("NA/buff/267?reverse=True", "NA_buff_267_reverse"),
    "buff_JP_reverse_basic": (
        "JP/buff/search?type=specialInvincible&reverse=true&reverseData=basic&reverseDepth=servant&lang=en",
        "JP_buff_special_invincible_reverse",
    ),
    "equip_JP_collectionNo": ("JP/equip/683", "JP_Aerial_Drive"),
    "equip_JP_id": ("JP/equip/9402750", "JP_Aerial_Drive"),
    "svt_NA_id": ("NA/svt/9939120", "NA_svt_9939120"),
    "item_NA_id": ("NA/item/94000201", "NA_item_94000201"),
    "MC_NA_id": ("NA/MC/110", "NA_MC_LB"),
    "JP_CC_id": ("JP/CC/8400550", "JP_CC_8400550"),
    "JP_CC_collectionNo": ("JP/CC/55", "JP_CC_8400550"),
    "event_JP_id": ("JP/event/80289", "JP_Guda_5"),
    "event_rerward_NA": ("NA/event/80018", "NA_event_Rashomon"),
    "war_NA_id": ("NA/war/203", "NA_war_Shimousa"),
    "quest_JP_id": ("JP/quest/91103002", "JP_Suzuka_rank_up"),
    "quest_NA_id_phase": ("NA/quest/94020187/1", "NA_87th_floor"),
    "quest_NA_consume_item": ("NA/quest/94032412", "NA_Enma_tei_spa_room"),
    "ai_beni_cq_monkey_NA": ("NA/ai/svt/94032580", "NA_AI_Beni_CQ_monkey"),
    "kh_cq_JP": ("JP/ai/field/90161870", "JP_KH_CQ_taunt"),
}


test_cases = [pytest.param(*value, id=key) for key, value in test_cases_dict.items()]


@pytest.mark.parametrize("query,result", test_cases)
def test_nice(query: str, result: str) -> None:
    response = client.get(f"/nice/{query}")
    assert response.status_code == 200
    assert response.json() == get_response_data("test_data_nice", result)


cases_404_dict = {
    "servant": "500",
    "equip": "3001",
    "svt": "987626",
    "skill": "25689",
    "NP": "900205",
    "function": "9000",
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
}


cases_404 = [pytest.param(key, value, id=key) for key, value in cases_404_dict.items()]


@pytest.mark.parametrize("endpoint,item_id", cases_404)
def test_404_nice(endpoint: str, item_id: str) -> None:
    response = client.get(f"/nice/JP/{endpoint}/{item_id}")
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
}


cases_datavals = [
    pytest.param(*value, id=key) for key, value in cases_datavals_dict.items()
]


@pytest.mark.parametrize("skill_id,function_index,parse_result", cases_datavals)
def test_special_datavals(
    skill_id: int, function_index: int, parse_result: Dict[str, int]
) -> None:
    response = client.get(f"/nice/JP/skill/{skill_id}")
    assert response.status_code == 200
    assert response.json()["functions"][function_index]["svals"][0] == parse_result


class TestServantSpecial:
    def test_NA_not_integer(self) -> None:
        response = client.get("/nice/NA/servant/lkji")
        assert response.status_code == 422

    def test_JP_Emiya_all_nps(self) -> None:
        response = client.get("/nice/JP/servant/11")
        nps = {np["id"] for np in response.json()["noblePhantasms"]}
        assert response.status_code == 200
        assert nps == {200101, 200102, 200198, 200197}

    def test_skill_reverse_passive(self) -> None:
        response = client.get("/nice/NA/skill/30650?reverse=True")
        reverse_servants = {
            servant["id"] for servant in response.json()["reverse"]["nice"]["servant"]
        }
        assert response.status_code == 200
        assert reverse_servants == {201200, 401800, 601000}

    def test_JP_English_name(self) -> None:
        response = client.get("/nice/JP/servant/304300?lang=en")
        assert response.status_code == 200
        assert response.json()["name"] == "Elice Utsumi"

        response = client.get("/nice/JP/equip/1296?lang=en")
        assert response.status_code == 200
        assert response.json()["name"] == "Hell's Kitchen"

    def test_JP_skill_English_name(self) -> None:
        response = client.get("/nice/JP/skill/991604?lang=en")
        assert response.status_code == 200
        assert response.json()["name"] == "Paradox Ace Killer"

    def test_JP_CC_English_name(self) -> None:
        response = client.get("/nice/JP/CC/8400240?lang=en")
        assert response.status_code == 200
        assert response.json()["name"] == "The Holy Night's Aurora"

    def test_empty_cv_illustrator_name(self) -> None:
        response = client.get("/nice/JP/svt/9941330?lore=true")
        assert response.status_code == 200
        assert response.json()["profile"]["cv"] == ""
        assert response.json()["profile"]["illustrator"] == ""

    def test_buff_reverse_skillNp(self) -> None:
        response = client.get("/nice/NA/buff/203?reverse=True&reverseDepth=skillNp")
        assert response.status_code == 200
        assert response.json()["reverse"]["nice"]["function"][1]["reverse"]["nice"][
            "skill"
        ]

    def test_function_reverse_servant(self) -> None:
        response = client.get(
            "/nice/NA/function/3411?reverse=True&reverseDepth=servant"
        )
        assert response.status_code == 200
        assert response.json()["reverse"]["nice"]["skill"][0]["reverse"]["nice"][
            "servant"
        ]

    def test_solomon_cvId(self) -> None:
        response = client.get("/nice/JP/servant/83?lore=true")
        assert response.status_code == 200
        assert response.json()["profile"]["cv"] == ""

    def test_datavals_default_case_target(self) -> None:
        response = client.get("/nice/NA/NP/600701")
        assert response.status_code == 200
        assert response.json()["functions"][0]["svals"][0] == {
            "Rate": 5000,
            "Value": 600710,
            "Target": 0,
        }

    def test_list_datavals_2_items(self) -> None:
        response = client.get("/nice/JP/NP/403401")
        assert response.status_code == 200
        assert response.json()["functions"][0]["svals"][0] == {
            "Rate": 1000,
            "Value": 6000,
            "Target": 0,
            "Correction": 1500,
            "TargetRarityList": [1, 2],
        }

    def test_list_datavals_1_item(self) -> None:
        response = client.get("/nice/JP/NP/304201")
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

    def test_script_svt_SkillRankUp(self) -> None:
        response = client.get("/nice/JP/servant/285")
        assert response.status_code == 200
        expected = {
            "767650": [],
            "682450": [964647, 964648, 964648, 964648],
            "768550": [964649, 964650, 964650, 964650],
        }
        assert response.json()["script"]["SkillRankUp"] == expected

    def test_script_STAR_HIGHER_Moriarty(self) -> None:
        response = client.get("/nice/NA/skill/334552")
        assert response.status_code == 200
        assert response.json()["script"] == {
            "STAR_HIGHER": [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
        }

    def test_script_followerVals_Be_Graceful(self) -> None:
        response = client.get("/nice/NA/skill/991370")
        assert response.status_code == 200
        assert response.json()["functions"][0]["followerVals"] == [{"RateCount": 150}]

    def test_buff_script_relationId(self) -> None:
        response = client.get("/nice/JP/buff/2585")
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

        response_2 = client.get("/nice/JP/buff/2576")
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

    def test_buff_DamageRelease(self) -> None:
        response = client.get("/nice/JP/buff/2935")
        assert response.status_code == 200
        assert response.json()["script"] == {"ReleaseText": "睡眠解除", "DamageRelease": 1}

    def test_negative_trait(self) -> None:
        response = client.get("/nice/JP/buff/2966")
        expected = {"id": 4101, "name": "aoeNP", "negative": True}
        assert response.status_code == 200
        assert response.json()["ckOpIndv"][0] == expected

    def test_ascension_trait(self) -> None:
        response = client.get("/nice/JP/servant/603700")
        expected = {
            "ascension": {
                "0": [
                    {"id": 2, "name": "genderFemale"},
                    {"id": 105, "name": "classAssassin"},
                    {"id": 200, "name": "attributeSky"},
                    {"id": 301, "name": "alignmentChaotic"},
                    {"id": 304, "name": "alignmentEvil"},
                    {"id": 1000, "name": "basedOnServant"},
                    {"id": 2000, "name": "divine"},
                    {"id": 2001, "name": "humanoid"},
                    {"id": 2008, "name": "weakToEnumaElish"},
                    {"id": 2009, "name": "riding"},
                    {"id": 2011, "name": "skyOrEarth"},
                    {"id": 2040, "name": "divineOrDaemonOrUndead"},
                    {"id": 2631, "name": "hominidaeServant"},
                    {"id": 2667, "name": "childServant"},
                    {"id": 5000, "name": "canBeInBattle"},
                    {"id": 603700, "name": "unknown"},
                ],
                "1": [],
                "2": [],
                "3": [],
                "4": [],
            },
            "costume": {},
        }
        assert response.status_code == 200
        assert response.json()["ascensionAdd"]["individuality"] == expected

    def test_servant_change(self) -> None:
        response = client.get("/nice/NA/servant/184")
        assert response.status_code == 200
        assert response.json()["svtChange"][0]["name"] == "Archer of Inferno"

    def test_story_charaFigure_form(self) -> None:
        response = client.get("/nice/JP/servant/126").json()
        assert "story" in response["extraAssets"]["charaFigureForm"]["1"]
        assert "story" in response["extraAssets"]["charaFigureForm"]["2"]

    def test_war_banner(self) -> None:
        war_oniland = client.get("/nice/NA/war/9050")
        assert war_oniland.status_code == 200
        assert "event_war_" in war_oniland.json()["banner"]
        war_interlude = client.get("/nice/NA/war/1003")
        assert war_interlude.status_code == 200
        assert "chaldea_category_" in war_interlude.json()["banner"]

    def test_shop_itemIds_0(self) -> None:
        with engines[Region.NA].connect() as conn:
            fp_shop_item = get_nice_shop(Region.NA, event.get_mstShop_by_id(conn, 1))
            assert fp_shop_item.cost.item.name == "Friend Point"

            mp_shop_item = get_nice_shop(
                Region.NA, event.get_mstShop_by_id(conn, 11000000)
            )
            assert mp_shop_item.cost.item.name == "Mana Prism"

    def test_skill_ai_id(self) -> None:
        nice_skill = client.get("/nice/NA/skill/962219").json()
        assert nice_skill["aiIds"]["field"] == [94031791]

    def test_overwrite_script(self) -> None:
        summer_okita = client.get("/nice/JP/servant/267?lang=en").json()
        ascensionAdd = summer_okita["ascensionAdd"]

        overWriteServantName = ascensionAdd["overWriteServantName"]
        overWriteTDName = ascensionAdd["overWriteTDName"]
        overWriteTDFileName = ascensionAdd["overWriteTDFileName"]

        assert overWriteServantName["ascension"]["1"] == "Okita J Souji"
        assert overWriteTDName["ascension"]["1"] == "蒼穹三段突き"
        assert overWriteTDFileName["ascension"]["1"].endswith(
            "JP/Servants/Commands/604000/604010.png"
        )
