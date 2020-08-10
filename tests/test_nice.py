from typing import Dict

import pytest
from fastapi.testclient import TestClient

from app.main import app

from .utils import get_response_data


client = TestClient(app)


test_cases_dict = {
    "servant_NA_collectionNo": ("NA/servant/105", "NA_Billy"),
    "servant_NA_id": ("NA/servant/201000", "NA_Billy"),
    "servant_NA_lore": ("NA/servant/100?lore=True", "NA_Helena_lore"),
    "servant_JP_collectionNo": ("JP/servant/283", "JP_Elice"),
    "servant_JP_id": ("JP/servant/304300", "JP_Elice"),
    "servant_JP_collection_servant": ("JP/servant/149", "JP_Tiamat"),
    "servant_JP_costume": ("JP/servant/1", "JP_Mash"),
    "servant_JP_multiple_NPs_space_istar": ("JP/servant/268", "JP_Space_Ishtar"),
    "skill_NA_id": ("NA/skill/454650", "NA_Fujino_1st_skill"),
    "skill_NA_reverse": ("NA/skill/19450?reverse=True", "NA_Fionn_1st_skill_reverse"),
    "skill_JP_dependFunc": ("JP/skill/671650", "JP_Melt_skill_dependFunc"),
    "skill_JP_dependFunc_colon": ("JP/skill/711550", "JP_Yang_Guifei_skill"),
    "NP_JP_id": ("JP/NP/301101", "JP_Fionn_NP"),
    "NP_JP_reverse": ("JP/NP/202901?reverse=True", "JP_Fujino_NP_reverse"),
    "function_NA_id": ("NA/function/400", "NA_function_400"),
    "function_JP_reverse": ("NA/function/298?reverse=True", "NA_function_298_reverse"),
    "buff_NA_id": ("NA/buff/300", "NA_buff_300"),
    "buff_NA_reverse": ("NA/buff/267?reverse=True", "NA_buff_267_reverse"),
    "equip_JP_collectionNo": ("JP/equip/683", "JP_Aerial_Drive"),
    "equip_JP_id": ("JP/equip/9402750", "JP_Aerial_Drive"),
    "svt_NA_id": ("NA/svt/9939120", "NA_svt_9939120"),
    "item_NA_id": ("NA/item/94000201", "NA_item_94000201"),
    "MC_NA_id": ("NA/MC/110", "NA_MC_LB"),
    "JP_CC_id": ("JP/CC/8400550", "JP_CC_8400550"),
    "quest_NA_id_phase": ("NA/quest/94020187/1", "NA_87th_floor"),
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
    "quest": "1234567",
    "quest/94025012": "2",
}


cases_404 = [pytest.param(key, value, id=key) for key, value in cases_404_dict.items()]


@pytest.mark.parametrize("endpoint,item_id", cases_404)
def test_404_nice(endpoint: str, item_id: str) -> None:
    response = client.get(f"/nice/JP/{endpoint}/{item_id}")
    assert response.status_code == 404
    if endpoint == "quest":
        assert response.json()["detail"] == "Not Found"
    else:
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

    def test_skill_reverse_passive(self) -> None:
        response = client.get("/nice/NA/skill/30650?reverse=True")
        reverse_servants = {
            item["id"] for item in response.json()["reverse"]["nice"]["servant"]
        }
        assert response.status_code == 200
        assert reverse_servants == {201200, 401800, 601000}

    def test_JP_English_name(self) -> None:
        response = client.get("/nice/JP/servant/304300?lang=en")
        assert response.status_code == 200
        assert response.json()["name"] == "Elice Utsumi"

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
            "Target": 0,
            "Correction": 200,
            "TargetList": [2004],
            "ParamAddMaxCount": 10,
        }

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
