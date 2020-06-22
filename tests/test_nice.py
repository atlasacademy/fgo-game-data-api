from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

import orjson
from app.main import app


client = TestClient(app)
file_path = Path(__file__)


def get_response_data(file_name: str) -> Any:
    with open(file_path.parent / "test_data_nice" / f"{file_name}.json", "rb") as fp:
        return orjson.loads(fp.read())


class TestServant:
    def test_NA_collectionNo(self):
        response = client.get("/nice/NA/servant/105")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_Billy")

    def test_NA_id(self):
        response = client.get("/nice/NA/servant/201000")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_Billy")

    def test_NA_lore(self):
        response = client.get("/nice/NA/servant/100?lore=True")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_Helena_lore")

    def test_NA_not_integer(self):
        response = client.get("/nice/NA/servant/lkji")
        assert response.status_code == 422
        assert response.json() == get_response_data("NA_Servant_not_integer")

    def test_NA_collectionNo_not_found(self):
        response = client.get("/nice/NA/servant/500")
        assert response.status_code == 404
        assert response.json() == get_response_data("NA_Servant_not_found")

    def test_JP_collectionNo(self):
        response = client.get("/nice/JP/servant/283")
        assert response.status_code == 200
        assert response.json() == get_response_data("JP_Elice")

    def test_JP_id(self):
        response = client.get("/nice/JP/servant/304300")
        assert response.status_code == 200
        assert response.json() == get_response_data("JP_Elice")

    def test_JP_costume(self):
        response = client.get("/nice/JP/servant/1")
        assert response.status_code == 200
        assert response.json() == get_response_data("JP_Mash")

    def test_JP_id_English(self):
        response = client.get("/nice/JP/servant/304300?lang=en")
        assert response.status_code == 200
        assert response.json() == get_response_data("JP_Elice_EN")

    def test_JP_multiple_NPs_space_istar(self):
        response = client.get("/nice/JP/servant/268")
        assert response.status_code == 200
        assert response.json() == get_response_data("JP_Space_Ishtar")

    def test_JP_string_svals_values(self):
        # See svals TargetRarityList
        response = client.get("/nice/JP/servant/403400?lang=en")
        assert response.status_code == 200
        assert response.json() == get_response_data("JP_Bartholomew")

    def test_JP_datavals_subState_Value2(self):
        response = client.get("/nice/JP/servant/103800")
        assert response.status_code == 200
        assert response.json() == get_response_data("JP_Jason")


class TestEquip:
    def test_JP_collectionNo(self):
        response = client.get("/nice/JP/equip/683")
        assert response.status_code == 200
        assert response.json() == get_response_data("JP_Aerial_Drive")

    def test_JP_id(self):
        response = client.get("/nice/JP/equip/9402750")
        assert response.status_code == 200
        assert response.json() == get_response_data("JP_Aerial_Drive")

    def test_JP_collectionNo_not_found(self):
        response = client.get("/nice/JP/equip/2001")
        assert response.status_code == 404


class TestSvt:
    def test_NA_svt(self):
        response = client.get("/nice/NA/svt/9939120")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_svt_9939120")

    def test_JP_svt_not_found(self):
        response = client.get("/nice/JP/svt/987626")
        assert response.status_code == 404


class TestItem:
    def test_NA_item(self):
        response = client.get("/nice/NA/item/94000201")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_item_94000201")

    def test_JP_item_not_found(self):
        response = client.get("/nice/JP/item/1009")
        assert response.status_code == 404


class TestMC:
    def test_NA_MC(self):
        response = client.get("/nice/NA/MC/110")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_MC_LB")

    def test_JP_MC_not_found(self):
        response = client.get("/nice/JP/MC/8732")
        assert response.status_code == 404


class TestQuestPhase:
    def test_NA_quest(self):
        response = client.get("/nice/NA/quest/94020187/1")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_87th_floor")

    def test_JP_quest_not_found_quest(self):
        response = client.get("/nice/NA/quest/94021187")
        assert response.status_code == 404

    def test_JP_quest_not_found_phase(self):
        response = client.get("/nice/NA/quest/94020187/2")
        assert response.status_code == 404
