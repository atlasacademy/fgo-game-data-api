from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

import orjson
from app.main import app


client = TestClient(app)
file_path = Path(__file__)


def get_response_data(file_name: str) -> Any:
    with open(file_path.parent / "test_data" / f"{file_name}.json", "rb") as fp:
        return orjson.loads(fp.read())


class TestServant:
    def test_NA_collectionNo(self):
        response = client.get("/raw/NA/servant/184")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_Tomoe")

    def test_NA_id(self):
        response = client.get("/raw/NA/servant/202100")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_Tomoe")

    def test_NA_collectionNo_expanded(self):
        response = client.get("/raw/NA/servant/200?expand=True")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_Fujino_expanded")

    def test_NA_not_integer(self):
        response = client.get("/raw/NA/servant/asdf")
        assert response.status_code == 422
        assert response.json() == get_response_data("NA_Servant_not_integer")

    def test_NA_collectionNo_not_found(self):
        response = client.get("/raw/NA/servant/500")
        assert response.status_code == 404
        assert response.json() == get_response_data("NA_Servant_not_found")

    def test_immutable_master(self):
        client.get("/raw/NA/servant/184")
        client.get("/raw/NA/servant/184?expand=True")
        response = client.get("/raw/NA/servant/184")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_Tomoe")

    def test_JP_collectionNo(self):
        response = client.get("/raw/JP/servant/185")
        assert response.status_code == 200
        assert response.json() == get_response_data("JP_Chiyome")

    def test_JP_id(self):
        response = client.get("/raw/JP/servant/602900")
        assert response.status_code == 200
        assert response.json() == get_response_data("JP_Chiyome")


class TestEquip:
    def test_NA_collectionNo(self):
        response = client.get("/raw/NA/equip/184")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_Gentle_affection")

    def test_NA_id(self):
        response = client.get("/raw/NA/equip/9401400")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_Gentle_affection")

    def test_NA_collectionNo_expanded(self):
        response = client.get("/raw/NA/equip/375?expand=True")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_Oni_Mask_expanded")


class TestSkill:
    def test_NA_skill(self):
        response = client.get("/raw/NA/skill/24550")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_skill_24550")

    def test_NA_skill_reverse(self):
        response = client.get("/raw/NA/skill/446550?reverse=True")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_skill_446550_reverse")

    def test_NA_skill_expand(self):
        response = client.get("/raw/NA/skill/275551?expand=True")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_skill_275551_expand")

    def test_NA_skill_reverse_expand(self):
        response = client.get("/raw/NA/skill/275551?expand=True&reverse=True")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_skill_275551_reverse_expand")

    def test_immutable_master(self):
        client.get("/raw/NA/skill/24550")
        client.get("/raw/NA/skill/24550?expand=True")
        response = client.get("/raw/NA/skill/24550")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_skill_24550")


class TestNP:
    def test_NA_NP(self):
        response = client.get("/raw/NA/NP/900101")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_NP_900101")

    def test_NA_NP_reverse(self):
        response = client.get("/raw/NA/NP/9940531?reverse=True")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_NP_9940531_reverse")

    def test_NA_NP_expand(self):
        response = client.get("/raw/NA/NP/202401?expand=True")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_NP_202401_expand")

    def test_NA_NP_reverse_expand(self):
        response = client.get("/raw/NA/NP/301202?expand=True&reverse=True")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_NP_301202_reverse_expand")

    def test_immutable_master(self):
        client.get("/raw/NA/NP/900101")
        client.get("/raw/NA/NP/900101?expand=True")
        response = client.get("/raw/NA/NP/900101")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_NP_900101")


class TestFunction:
    def test_NA_function(self):
        response = client.get("/raw/NA/function/433")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_function_433")

    def test_NA_function_reverse(self):
        response = client.get("/raw/NA/function/203?reverse=True")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_function_203_reverse")

    def test_NA_function_expand(self):
        response = client.get("/raw/NA/function/205?expand=True")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_function_205_expand")

    def test_NA_function_expand_no_buff(self):
        response = client.get("/raw/NA/function/433?expand=True")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_function_433_expand")

    def test_NA_function_reverse_expand(self):
        response = client.get("/raw/NA/function/300?expand=True&reverse=True")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_function_300_reverse_expand")

    def test_immutable_master(self):
        client.get("/raw/NA/function/400")
        client.get("/raw/NA/function/400?expand=True")
        response = client.get("/raw/NA/function/400")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_function_400")


class TestBuff:
    def test_NA_buff(self):
        response = client.get("/raw/NA/buff/200")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_buff_200")

    def test_NA_buff_reverse(self):
        response = client.get("/raw/NA/buff/190?reverse=True")
        assert response.status_code == 200
        assert response.json() == get_response_data("NA_buff_190_reverse")
