import pytest
from fastapi import HTTPException

from app.data.common import Language, Region, ReverseDepth
from app.data.enums import FuncType
from app.data.nice import get_nice_servant, parse_dataVals
from app.data.tasks import sort_by_collection_no


def test_parse_dataVals_add_state_6_items() -> None:
    result = parse_dataVals("[1000,3,3,300,1000,10]", FuncType.ADD_STATE, Region.NA)
    assert result == {
        "Rate": 1000,
        "Turn": 3,
        "Count": 3,
        "Value": 300,
        "UseRate": 1000,
        "Value2": 10,
    }


def test_parse_dataVals_class_drop_up_rate() -> None:
    result = parse_dataVals("[2,400,80017]", FuncType.CLASS_DROP_UP, Region.NA)
    result = {k: v for k, v in result.items() if "aa" not in k}
    assert result == {
        "EventId": 80017,
        "RateCount": 400,
    }


def test_parse_datavals_fail() -> None:
    with pytest.raises(HTTPException):
        parse_dataVals("[HideMiss]", 1, Region.NA)


def test_reverseDepth_fail() -> None:
    with pytest.raises(TypeError):
        print(ReverseDepth.function >= 1)  # type: ignore


def test_lru_cache() -> None:
    get_nice_servant(Region.NA, 202900, Language.en)
    get_nice_servant(Region.NA, 202900, Language.en)
    assert get_nice_servant.cache_info().hits == 1


def test_sort_by_collection_no() -> None:
    input_data = [
        {"id": 100100, "collectionNo": 2},
        {"id": 800100, "collectionNo": 1},
        {"id": 202900, "collectionNo": 200},
    ]
    result = sort_by_collection_no(input_data)
    assert result == [
        {"id": 800100, "collectionNo": 1},
        {"id": 100100, "collectionNo": 2},
        {"id": 202900, "collectionNo": 200},
    ]
