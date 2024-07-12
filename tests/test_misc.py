from decimal import Decimal

import orjson
import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncConnection

from app.core.nice.func import parse_dataVals
from app.core.utils import get_voice_name
from app.data.custom_mappings import Translation
from app.data.script import get_script_path, get_script_text_only, remove_brackets
from app.db.load import get_SkillID_from_sval, get_Value_from_sval
from app.routers.utils import list_string_exclude
from app.schemas.common import Language, Region, ReverseDepth
from app.schemas.gameenums import FuncType
from app.schemas.nice import NiceServant
from app.schemas.raw import ScriptJsonInfo, get_subtitle_svtId

from .utils import get_response_data, get_text_data


def test_subtitle_svtId() -> None:
    assert get_subtitle_svtId("PLAINDEMO_99100001") == -1
    assert get_subtitle_svtId("9934820_0_B160") == 9934820


@pytest.mark.asyncio
async def test_parse_dataVals_add_state_6_items(na_db_conn: AsyncConnection) -> None:
    result = await parse_dataVals(
        na_db_conn, Region.NA, "[1000,3,3,300,1000,10]", FuncType.ADD_STATE, Language.en
    )
    assert result == {
        "Rate": 1000,
        "Turn": 3,
        "Count": 3,
        "Value": 300,
        "UseRate": 1000,
        "Value2": 10,
    }


@pytest.mark.asyncio
async def test_parse_dataVals_unknown_datavals(
    caplog: pytest.LogCaptureFixture, na_db_conn: AsyncConnection
) -> None:
    await parse_dataVals(
        na_db_conn, Region.NA, "[1000,3,3,300]", FuncType.SUB_STATE, Language.en
    )
    assert (
        "Some datavals weren't parsed for func type 2: "
        "[1000,3,3,300] => {'Rate': 1000, 'Value': 3, 'Value2': 3}" in caplog.text
    )


@pytest.mark.asyncio
async def test_parse_dataVals_class_drop_up_rate(na_db_conn: AsyncConnection) -> None:
    result = await parse_dataVals(
        na_db_conn, Region.NA, "[2,400,80017]", FuncType.CLASS_DROP_UP, Language.en
    )
    result = {k: v for k, v in result.items() if "aa" not in k}
    assert result == {
        "EventId": 80017,
        "RateCount": 400,
    }


cases_datavals_fail_dict = {
    "test_dataVals_fail_str_dataVals_no_value": "[HideMiss]",
    "test_dataVals_fail_str_dataVals_str_value": "[HideMiss:123/abc]",
    "test_dataVals_fail_list_str": "[TargetList:123/abc]",
    "test_dataVals_fail_str_not_a_list": "[TargetList:abc]",
    "test_unknown_function_dependFunc": "[5000,DependFuncId1:[9999],DependFuncVals1:[0,5000,Value2:250]]",
}


cases_datavals_fail = [
    pytest.param(value, id=key) for key, value in cases_datavals_fail_dict.items()
]


@pytest.mark.asyncio
@pytest.mark.parametrize("dataVals", cases_datavals_fail)
async def test_parse_datavals_fail_list_str(
    dataVals: str, na_db_conn: AsyncConnection
) -> None:
    with pytest.raises(HTTPException):
        await parse_dataVals(na_db_conn, Region.NA, dataVals, 1, Language.en)


def test_reverseDepth_str_comparison() -> None:
    assert ReverseDepth.function >= "aaaaa"


def test_list_exclude() -> None:
    test_data = NiceServant.parse_obj(
        get_response_data("test_data_nice", "NA_Dantes_lore_costume")
    )
    excluded_keys = {"profile"}
    json_data = list_string_exclude([test_data], exclude=excluded_keys)
    for key in excluded_keys:
        assert key not in orjson.loads(json_data)


def test_voice_lang_en() -> None:
    assert (
        get_voice_name(
            "レベルアップ エスタブリッシュメント",
            Language.en,
            Translation.OVERWRITE_VOICE,
        )
        == "Level Up Establishment"
    )
    assert (
        get_voice_name("エクストラアタック 2", Language.en, Translation.VOICE)
        == "Extra Attack 2"
    )


def test_get_script_path() -> None:
    assert get_script_path("WarEpilogue108") == "01/WarEpilogue108"


def test_parse_script() -> None:
    test_script = get_text_data("test_data_misc", "test_script")
    output = (
        "(Choice) Jeanne! (Jeanne) I was careless... "
        "I never expected to be forced to acknowledge her like this...! (Jeanne Alter)"
    )
    assert get_script_text_only(Region.NA, test_script) == output

    ruby_text = "[line 3]オールトの雲より飛来した、[r][#極限の単独種:ア ル テ ミ ッ ト ・ ワ ン]がね。"
    expected = "オールトの雲より飛来した、極限の単独種アルテミット・ワンがね。"
    assert remove_brackets(Region.JP, ruby_text) == expected

    gender_line = "＠talker\n[&male1:female1] and [&male2:female2]\n[k]"
    expected_gender = "(talker) (Male) male1 and male2 (Female) female1 and female2"
    assert get_script_text_only(Region.NA, gender_line) == expected_gender


def test_TW_odd_voice_id() -> None:
    script_json = ScriptJsonInfo(
        id="御主任務 2021年4月 2", face=13, delay=Decimal(0.3), text="0_A1430", form=0
    )
    assert script_json.get_voice_id() == "御主任務 2021年4月 2"


def test_get_Value_from_sval() -> None:
    assert get_Value_from_sval("1000,3,-1,965198,Value2:1") == 965198


def test_get_SkillID_from_sval() -> None:
    assert (
        get_SkillID_from_sval(
            "1000,3,-1,1,SkillID:961313,SkillLV:1,HideMiss:1,HideNoEffect:1,ShowCardOnly:1"
        )
        == 961313
    )
