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


class TestEquipSearch:
    def test_search_name(self):
        response = client.get("/nice/NA/equip/search?name=Kaleidoscope")
        assert response.status_code == 200
        assert {item["id"] for item in response.json()} == {9400340}

    def test_search_name_raw(self):
        response = client.get("/raw/JP/equip/search?name=カレイドスコープ")
        assert response.status_code == 200
        assert {item["mstSvt"]["id"] for item in response.json()} == {9400340}

    def test_search_name_rarity(self):
        response = client.get("/nice/NA/equip/search?name=Kaleidoscope&rarity=4")
        assert response.status_code == 200
        assert response.text == "[]"

    def test_search_names(self):
        response = client.get("/nice/NA/equip/search?name=Banquet")
        assert response.status_code == 200
        assert {item["id"] for item in response.json()} == {9302550, 9400290}

    def test_NA_search_no_query(self):
        response = client.get("/nice/NA/equip/search")
        assert response.status_code == 400

    def test_JP_search_no_query(self):
        response = client.get("/raw/JP/equip/search")
        assert response.status_code == 400


class TestServantSearch:
    def test_search_name(self):
        response = client.get("/raw/NA/servant/search?name=Pendragon")
        assert response.status_code == 200
        assert {item["mstSvt"]["id"] for item in response.json()} == {
            100100,
            100200,
            100300,
            102900,
            202600,
            301900,
            302000,
            402200,
            402700,
        }

    def test_search_name_rarity_class(self):
        response = client.get(
            "/nice/NA/servant/search?name=Pendragon&rarity=5&className=saber"
        )
        print({item["id"] for item in response.json()})
        assert response.status_code == 200
        assert {item["id"] for item in response.json()} == {100100, 102900}

    def test_search_name_rarity_class_gender(self):
        response = client.get(
            "/nice/NA/servant/search?name=Pendragon&rarity=5&className=saber&gender=female"
        )
        print({item["id"] for item in response.json()})
        assert response.status_code == 200
        assert {item["id"] for item in response.json()} == {100100}

    def test_search_name_class_attribute(self):
        response = client.get("/nice/NA/servant/search?className=archer&attribute=star")
        print({item["id"] for item in response.json()})
        assert response.status_code == 200
        assert {item["id"] for item in response.json()} == {201100, 202200}

    def test_search_name_class_trait_rarity(self):
        response = client.get(
            "/nice/JP/servant/search?className=rider&trait=king&lang=en&rarity=3"
        )
        print({item["id"] for item in response.json()})
        assert response.status_code == 200
        assert {item["id"] for item in response.json()} == {401100, 401500, 403900}

    def test_NA_search_no_query(self):
        response = client.get("/nice/NA/servant/search")
        assert response.status_code == 400

    def test_JP_search_no_query(self):
        response = client.get("/raw/NA/servant/search")
        assert response.status_code == 400
