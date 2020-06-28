from pathlib import Path
from typing import Any

import orjson
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
file_path = Path(__file__)


def get_response_data(file_name: str) -> Any:
    with open(file_path.parent / "test_data_Basic" / f"{file_name}.json", "rb") as fp:
        return orjson.loads(fp.read())


class TestServant:
    def test_NA_collectionNo(self):
        response = client.get("/basic/NA/servant/76")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_Mordred")

    def test_NA_id(self):
        response = client.get("/basic/NA/servant/100900")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_Mordred")

    def test_NA_not_integer(self):
        response = client.get("/basic/NA/servant/lkji")
        assert response.status_code == 422

    def test_NA_collectionNo_not_found(self):
        response = client.get("/basic/NA/servant/500")
        assert response.status_code == 404

    def test_JP_collectionNo(self):
        response = client.get("/basic/JP/servant/256")
        assert response.status_code == 200
        assert response.json() == get_response_data("JP_Gareth")

    def test_JP_id(self):
        response = client.get("/basic/JP/servant/303900")
        assert response.status_code == 200
        assert response.json() == get_response_data("JP_Gareth")

    def test_JP_lang_en(self):
        response = client.get("/basic/JP/servant/208?lang=en")
        assert response.status_code == 200
        assert response.json() == get_response_data("JP_Sieg_en")


class TestEquip:
    def test_JP_collectionNo(self):
        response = client.get("/basic/JP/equip/467")
        assert response.status_code == 200
        assert response.json() == get_response_data("JP_Bitter_Chocolates")

    def test_JP_id(self):
        response = client.get("/basic/JP/equip/9805370")
        assert response.status_code == 200
        assert response.json() == get_response_data("JP_Bitter_Chocolates")

    def test_JP_collectionNo_not_found(self):
        response = client.get("/basic/JP/equip/2001")
        assert response.status_code == 404
