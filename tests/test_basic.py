import pytest
from fastapi.testclient import TestClient

from app.main import app

from .utils import get_response_data


client = TestClient(app)


test_cases_dict = {
    "servant_NA_collectionNo": ("NA/servant/76", "NA_Mordred"),
    "servant_NA_id": ("NA/servant/100900", "NA_Mordred"),
    "servant_JP_collectionNo": ("JP/servant/256", "JP_Gareth"),
    "servant_JP_id": ("JP/servant/303900", "JP_Gareth"),
    "servant_JP_lang_en": ("JP/servant/208?lang=en", "JP_Sieg_en"),
    "equip_JP_collectionNo": ("JP/equip/467", "JP_Bitter_Chocolates"),
    "equip_JP_id": ("JP/equip/9805370", "JP_Bitter_Chocolates"),
}


test_cases = [pytest.param(*value, id=key) for key, value in test_cases_dict.items()]


@pytest.mark.parametrize("query,result", test_cases)
def test_basic(query: str, result: str):
    response = client.get(f"/basic/{query}")
    assert response.status_code == 200
    assert response.json() == get_response_data("test_data_basic", result)


class TestServantSpecial:
    def test_NA_not_integer(self):
        response = client.get("/basic/NA/servant/lkji")
        assert response.status_code == 422

    def test_NA_collectionNo_not_found(self):
        response = client.get("/basic/NA/servant/500")
        assert response.status_code == 404


class TestEquipSpecial:
    def test_JP_collectionNo_not_found(self):
        response = client.get("/basic/JP/equip/2001")
        assert response.status_code == 404
