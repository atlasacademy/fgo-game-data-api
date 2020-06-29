from app.data.nice import parse_dataVals
from app.routers.basic import sort_by_collection_no


def test_parse_dataVals_add_state_6_items():
    result = parse_dataVals("[1000,3,3,300,1000,10]", 1)
    assert result == {
        "Rate": 1000,
        "Turn": 3,
        "Count": 3,
        "Value": 300,
        "UseRate": 1000,
        "Value2": 10,
    }


def test_sort_by_collection_no():
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
