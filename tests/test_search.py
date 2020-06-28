from typing import Set

import pytest
from fastapi.testclient import TestClient
from requests import Response

from app.main import app


client = TestClient(app)


def get_item_list(response: Response, response_type: str) -> Set[int]:
    if response_type == "raw":
        return {item["mstSvt"]["id"] for item in response.json()}
    else:
        return {item["id"] for item in response.json()}


test_cases_dict = {
    "equip_name_NA": ("NA/equip/search?name=Kaleidoscope", {9400340}),
    "equip_name_JP": ("JP/equip/search?name=カレイドスコープ", {9400340}),
    "equip_names_NA": ("NA/equip/search?name=Banquet", {9302550, 9400290}),
    "servant_name_NA": (
        "NA/servant/search?name=Pendragon",
        {100100, 100200, 100300, 102900, 202600, 301900, 302000, 402200, 402700},
    ),
    "servant_name_rarity_class": (
        "NA/servant/search?name=Pendragon&rarity=5&className=saber",
        {100100, 102900},
    ),
    "servant_name_rarity_class_gender": (
        "NA/servant/search?name=Pendragon&rarity=5&className=saber&gender=female",
        {100100},
    ),
    "servant_class_attribute": (
        "NA/servant/search?className=archer&attribute=star",
        {201100, 202200, 203100},
    ),
    "servant_class_trait_rarity_lang": (
        "JP/servant/search?className=rider&trait=king&lang=en&rarity=3",
        {401100, 401500, 403900},
    ),
    "servant_search_Okita_Alter": (
        "NA/servant/search?name=Okita Souji (Alter)",
        {1000700},  # shouldn't return Okita Saber
    ),
    "servant_JP_search_EN_name": ("JP/servant/search?name=Skadi", {503900}),
    "servant_NA_search_Scathach": ("NA/servant/search?name=Scathach", {301300, 602400}),
    "servant_search_Yagyu": ("NA/servant/search?name=Tajima", {103200}),
}

test_cases = [pytest.param(*value, id=key) for key, value in test_cases_dict.items()]


test_not_found_dict = {
    "servant": "NA/servant/search?name=ÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛ",
    "equip": "NA/equip/search?name=Kaleidoscope&rarity=4",
}

not_found_cases = [
    pytest.param(value, id=key) for key, value in test_not_found_dict.items()
]


@pytest.mark.parametrize("response_type", ["basic", "nice", "raw"])
class TestSearch:
    @pytest.mark.parametrize("search_query,result", test_cases)
    def test_search(self, search_query: str, result: Set[int], response_type: str):
        response = client.get(f"/{response_type}/{search_query}")
        result_ids = get_item_list(response, response_type)
        assert response.status_code == 200
        assert result_ids == result

    @pytest.mark.parametrize("query", not_found_cases)
    def test_not_found_any(self, response_type: str, query: str):
        response = client.get(f"/{response_type}/{query}")
        assert response.status_code == 200
        assert response.text == "[]"

    @pytest.mark.parametrize("endpoint", ["servant", "equip"])
    def test_empty_input(self, response_type: str, endpoint: str):
        response = client.get(f"/{response_type}/NA/{endpoint}/search")
        assert response.status_code == 400
