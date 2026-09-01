from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, NamedTuple, cast

import orjson
import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncConnection

from app.core.nice.func import parse_dataVals
from app.core.nice.svt.voice import (
    get_nice_subtitles,
    get_subtitle_audio_candidates,
    get_subtitle_audio_urls,
)
from app.core.utils import get_voice_name
from app.data.custom_mappings import Translation
from app.data.script import get_script_path, get_script_text_only, remove_brackets
from app.db.helpers import asset
from app.db.load import get_SkillID_from_sval, get_Value_from_sval
from app.routers.utils import list_string_exclude
from app.schemas.common import Language, Region, ReverseDepth
from app.schemas.gameenums import FuncType, SvtVoiceType
from app.schemas.nice import NiceServant, NiceVoiceSubtitle
from app.schemas.raw import (
    GlobalNewMstSubtitle,
    MstSvtGroup,
    MstSvtVoice,
    MstVoice,
    MstVoicePlayCond,
    ScriptJson,
    ScriptJsonInfo,
    get_subtitle_svtId,
)

from .utils import get_response_data, get_text_data


def test_subtitle_svtId() -> None:
    assert get_subtitle_svtId("PLAINDEMO_99100001") == -1
    assert get_subtitle_svtId("9934820_0_B160") == 9934820


def test_subtitle_voice_id() -> None:
    def voice_id(subtitle_id: str) -> str:
        return GlobalNewMstSubtitle(id=subtitle_id, serif="").get_voice_id()

    assert voice_id("1100200_11_B050") == "B050"
    # The mstVoice key of a xxx1/xxx2 line is xxx0, same as for a voice line info
    assert voice_id("100100_0_B011") == "B010"
    assert voice_id("100100_B050") == "B050"
    assert voice_id("9944030") == ""


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
        id="御主任務 2021年4月 2", face=13, delay=Decimal("0.3"), text="0_A1430", form=0
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


@dataclass
class VoiceData:
    """Stand-in for the voice fields of SvtEntity, see RequiredVoiceData."""

    mstSvtVoice: list[MstSvtVoice] = field(default_factory=list)
    mstVoice: list[MstVoice] = field(default_factory=list)
    mstVoicePlayCond: list[MstVoicePlayCond] = field(default_factory=list)
    mstSvtGroup: list[MstSvtGroup] = field(default_factory=list)
    mstSubtitle: list[GlobalNewMstSubtitle] = field(default_factory=list)


def make_svt_voice(svt_id: int, *voice_ids: str) -> MstSvtVoice:
    """Voice group with one voice line per voice id."""
    return MstSvtVoice(
        id=svt_id,
        voicePrefix=0,
        type=SvtVoiceType.BATTLE,
        scriptJson=[
            ScriptJson(
                infos=[ScriptJsonInfo(id=voice_id, face=0, delay=Decimal("0.0"))]
            )
            for voice_id in voice_ids
        ],
    )


def make_subtitles(*subtitle_ids: str) -> list[GlobalNewMstSubtitle]:
    return [
        GlobalNewMstSubtitle(id=subtitle_id, serif=f"serif {subtitle_id}")
        for subtitle_id in subtitle_ids
    ]


def make_voice(voice_id: str, svtVoiceType: SvtVoiceType) -> MstVoice:
    return MstVoice(
        id=voice_id,
        priority=0,
        svtVoiceType=svtVoiceType,
        name=f"name {voice_id}",
        nameDefault="???",
        condType=0,
        condValue=0,
        voicePlayedValue=0,
        firstPlayPriority=0,
        closedType=1,
        flag=0,
    )


def subtitle_asset_paths(subtitles: list[NiceVoiceSubtitle]) -> list[str]:
    return [subtitle.audioAsset.rsplit("/Audio/", 1)[1] for subtitle in subtitles]


def test_nice_subtitles_all_matched() -> None:
    voice_data = VoiceData(
        mstSvtVoice=[make_svt_voice(100100, "0_B010", "0_B020")],
        mstSubtitle=make_subtitles("100100_0_B010", "100100_0_B020"),
    )
    assert get_nice_subtitles(Region.NA, voice_data) == []


def test_nice_subtitles_none_matched() -> None:
    voice_data = VoiceData(mstSubtitle=make_subtitles("9944030_0_B010"))

    subtitles = get_nice_subtitles(Region.NA, voice_data)

    assert [subtitle.id for subtitle in subtitles] == ["9944030_0_B010"]
    assert subtitles[0].serif == "serif 9944030_0_B010"
    assert subtitles[0].audioAsset.endswith("/Servants_9944030/0_B010.mp3")


def test_nice_subtitles_mixed_keeps_order() -> None:
    voice_data = VoiceData(
        mstSvtVoice=[
            make_svt_voice(100100, "0_B010"),
            make_svt_voice(100100, "0_B030"),
        ],
        mstSubtitle=make_subtitles(
            "100100_0_B010",
            "100100_0_B020",
            "100100_0_B030",
            "100100_0_B040",
        ),
    )

    subtitles = get_nice_subtitles(Region.NA, voice_data)

    assert [subtitle.id for subtitle in subtitles] == [
        "100100_0_B020",
        "100100_0_B040",
    ]


def test_nice_subtitles_other_svt_voice_line_doesnt_match() -> None:
    """The svt id is part of the key: same voice id under another svt isn't a match."""
    voice_data = VoiceData(
        mstSvtVoice=[make_svt_voice(100100, "0_B010")],
        mstSubtitle=make_subtitles("9944030_0_B010"),
    )

    subtitles = get_nice_subtitles(Region.NA, voice_data)

    assert [subtitle.id for subtitle in subtitles] == ["9944030_0_B010"]


def test_nice_subtitles_only_first_info_matches() -> None:
    """A voice line consumes the subtitle of its first info only, like the nice voice line."""
    voice_data = VoiceData(
        mstSvtVoice=[
            MstSvtVoice(
                id=100100,
                voicePrefix=0,
                type=SvtVoiceType.BATTLE,
                scriptJson=[
                    ScriptJson(
                        infos=[
                            ScriptJsonInfo(id="0_B010", face=0, delay=Decimal("0.0")),
                            ScriptJsonInfo(id="0_B011", face=0, delay=Decimal("0.0")),
                        ]
                    )
                ],
            )
        ],
        mstSubtitle=make_subtitles("100100_0_B010", "100100_0_B011"),
    )

    subtitles = get_nice_subtitles(Region.NA, voice_data)

    assert [subtitle.id for subtitle in subtitles] == ["100100_0_B011"]


def test_nice_subtitles_skips_empty_scripts() -> None:
    """A None script or one with no infos makes no voice line, so it consumes nothing."""
    voice_data = VoiceData(
        mstSvtVoice=[
            MstSvtVoice(
                id=100100,
                voicePrefix=0,
                type=SvtVoiceType.BATTLE,
                scriptJson=[None, ScriptJson(infos=[])],
            )
        ],
        mstSubtitle=make_subtitles("100100_0_B010"),
    )

    subtitles = get_nice_subtitles(Region.NA, voice_data)

    assert [subtitle.id for subtitle in subtitles] == ["100100_0_B010"]


def test_nice_subtitles_skips_malformed_ids() -> None:
    voice_data = VoiceData(
        mstSubtitle=make_subtitles(
            "PLAINDEMO_99100001", "9944030", "9944030_0_B010", "_0_B020"
        )
    )

    subtitles = get_nice_subtitles(Region.NA, voice_data)

    assert [subtitle.id for subtitle in subtitles] == ["9944030_0_B010"]


def test_nice_subtitles_empty_table() -> None:
    assert get_nice_subtitles(Region.JP, VoiceData()) == []


def test_nice_subtitles_folder_comes_from_mstVoice() -> None:
    """The letter is ambiguous, the whole voice id isn't.

    B010 is a battle line and B050 a noble phantasm one, and their audio sits in
    different folders. An orphan has no voice group to read mstSvtVoice.type off,
    but mstVoice carries the same type keyed by the voice id.
    """
    voice_data = VoiceData(
        mstVoice=[
            make_voice("B010", SvtVoiceType.BATTLE),
            make_voice("B050", SvtVoiceType.TREASURE_DEVICE),
            make_voice("H190", SvtVoiceType.HOME),
        ],
        mstSubtitle=make_subtitles("100100_0_B010", "100100_11_B050", "100100_0_H190"),
    )

    subtitles = get_nice_subtitles(Region.NA, voice_data)

    assert subtitle_asset_paths(subtitles) == [
        "Servants_100100/0_B010.mp3",
        "NoblePhantasm_100100/11_B050.mp3",
        "ChrVoice_100100/0_H190.mp3",
    ]


def test_nice_subtitles_folder_falls_back_to_battle() -> None:
    """Some subtitle ids have no mstVoice row at all, so there is nothing to read."""
    voice_data = VoiceData(mstSubtitle=make_subtitles("1700100_0_B280"))

    subtitles = get_nice_subtitles(Region.NA, voice_data)

    assert subtitle_asset_paths(subtitles) == ["Servants_1700100/0_B280.mp3"]


def test_nice_subtitles_folder_uses_base_voice_id() -> None:
    """mstVoice is keyed by the xxx0 id, but the file keeps the id the subtitle has."""
    voice_data = VoiceData(
        mstVoice=[make_voice("B050", SvtVoiceType.TREASURE_DEVICE)],
        mstSubtitle=make_subtitles("100100_11_B051"),
    )

    subtitles = get_nice_subtitles(Region.NA, voice_data)

    assert subtitle_asset_paths(subtitles) == ["NoblePhantasm_100100/11_B051.mp3"]


MANIFEST_BASE = "https://manifest.example/NA/Audio"


def manifest(*file_names: str) -> dict[str, str]:
    """What get_audio_urls returns: manifest fileName -> the URL stored with it."""
    return {file_name: f"{MANIFEST_BASE}/{file_name}" for file_name in file_names}


def test_nice_subtitles_audio_url_comes_from_the_manifest() -> None:
    voice_data = VoiceData(
        mstVoice=[make_voice("B010", SvtVoiceType.BATTLE)],
        mstSubtitle=make_subtitles("100100_0_B010"),
    )

    subtitles = get_nice_subtitles(
        Region.NA, voice_data, manifest("Servants_100100/0_B010.mp3")
    )

    assert subtitles[0].audioAsset == f"{MANIFEST_BASE}/Servants_100100/0_B010.mp3"


def test_nice_subtitles_audio_folder_repaired_by_the_manifest() -> None:
    """9941740_0_B050: mstVoice says treasureDevice, the file ships under Servants_."""
    voice_data = VoiceData(
        mstVoice=[make_voice("B050", SvtVoiceType.TREASURE_DEVICE)],
        mstSubtitle=make_subtitles("9941740_0_B050"),
    )

    subtitles = get_nice_subtitles(
        Region.NA, voice_data, manifest("Servants_9941740/0_B050.mp3")
    )

    assert subtitles[0].audioAsset == f"{MANIFEST_BASE}/Servants_9941740/0_B050.mp3"


def test_nice_subtitles_audio_prefers_the_mstVoice_folder() -> None:
    """Both folders ship the file, so the voice type breaks the tie."""
    voice_data = VoiceData(
        mstVoice=[make_voice("B050", SvtVoiceType.TREASURE_DEVICE)],
        mstSubtitle=make_subtitles("100100_11_B050"),
    )

    subtitles = get_nice_subtitles(
        Region.NA,
        voice_data,
        manifest("Servants_100100/11_B050.mp3", "NoblePhantasm_100100/11_B050.mp3"),
    )

    assert (
        subtitles[0].audioAsset == f"{MANIFEST_BASE}/NoblePhantasm_100100/11_B050.mp3"
    )


def test_nice_subtitles_no_audio_when_the_manifest_has_none() -> None:
    """Dantes 0_H1800 is a leftover: its audio 404s under every folder."""
    voice_data = VoiceData(
        mstVoice=[make_voice("H1800", SvtVoiceType.HOME)],
        mstSubtitle=make_subtitles("1100200_0_H1800"),
    )

    subtitles = get_nice_subtitles(Region.NA, voice_data, manifest())

    assert subtitles[0].id == "1100200_0_H1800"
    assert subtitles[0].serif == "serif 1100200_0_H1800"
    assert subtitles[0].audioAsset is None


def test_nice_subtitles_audio_unverified_without_a_manifest() -> None:
    """No manifest data: the guessed URL, exactly as before the manifest existed."""
    voice_data = VoiceData(
        mstVoice=[make_voice("B050", SvtVoiceType.TREASURE_DEVICE)],
        mstSubtitle=make_subtitles("100100_11_B050"),
    )

    subtitles = get_nice_subtitles(Region.NA, voice_data, None)

    assert subtitle_asset_paths(subtitles) == ["NoblePhantasm_100100/11_B050.mp3"]


def test_subtitle_audio_candidates_lists_every_folder() -> None:
    """One name per folder, the one mstVoice points at first."""
    voice_data = VoiceData(
        mstVoice=[make_voice("B050", SvtVoiceType.TREASURE_DEVICE)],
        mstSubtitle=make_subtitles("100100_11_B050"),
    )

    assert get_subtitle_audio_candidates(voice_data) == [
        "NoblePhantasm_100100/11_B050.mp3",
        "Servants_100100/11_B050.mp3",
        "ChrVoice_100100/11_B050.mp3",
    ]


def test_subtitle_audio_candidates_skips_matched_subtitles() -> None:
    """Only orphans are looked up: a matched row is voiced by its voice line."""
    voice_data = VoiceData(
        mstSvtVoice=[make_svt_voice(100100, "0_B010")],
        mstSubtitle=make_subtitles("100100_0_B010"),
    )

    assert get_subtitle_audio_candidates(voice_data) == []


async def test_get_audio_urls_without_names_makes_no_query() -> None:
    """Nothing to verify, no round trip: the connection is never touched."""

    class ExplodingConnection:
        async def execute(self, *_args: Any, **_kwargs: Any) -> Any:
            raise AssertionError("queried the db for an empty name list")

    conn = cast(AsyncConnection, ExplodingConnection())

    assert await asset.get_audio_urls(conn, []) == {}


class ManifestRow(NamedTuple):
    fileName: str
    sourceUrl: str


class CountingConnection:
    """Stands in for AsyncConnection, answering every query with the same rows."""

    def __init__(self, *rows: ManifestRow) -> None:
        self.rows = list(rows)
        self.queries = 0

    async def execute(self, *_args: Any, **_kwargs: Any) -> Any:
        self.queries += 1
        return self

    def __iter__(self) -> Any:
        return iter(self.rows)

    def fetchone(self) -> Any:
        return self.rows[0] if self.rows else None


async def test_subtitle_audio_urls_asks_the_manifest_once() -> None:
    """A loaded manifest answers in one query: no existence check on the happy path."""
    voice_data = VoiceData(
        mstVoice=[make_voice("B050", SvtVoiceType.TREASURE_DEVICE)],
        mstSubtitle=make_subtitles("100100_11_B050"),
    )
    conn = CountingConnection(
        ManifestRow(
            "NoblePhantasm_100100/11_B050.mp3",
            f"{MANIFEST_BASE}/NoblePhantasm_100100/11_B050.mp3",
        )
    )

    audio_urls = await get_subtitle_audio_urls(
        cast(AsyncConnection, conn), Region.NA, voice_data
    )

    assert audio_urls == {
        "NoblePhantasm_100100/11_B050.mp3": (
            f"{MANIFEST_BASE}/NoblePhantasm_100100/11_B050.mp3"
        )
    }
    assert conn.queries == 1


async def test_subtitle_audio_urls_falls_back_when_the_manifest_is_empty() -> None:
    """No rows at all means the manifest isn't loaded, not that the audio is gone."""
    voice_data = VoiceData(mstSubtitle=make_subtitles("100100_11_B050"))
    conn = CountingConnection()

    # TW so a loaded-manifest test elsewhere can't memoise this region as present
    audio_urls = await get_subtitle_audio_urls(
        cast(AsyncConnection, conn), Region.TW, voice_data
    )

    assert audio_urls is None
    assert conn.queries == 2  # the lookup, then the "is it loaded at all" check


async def test_subtitle_audio_urls_skips_the_db_without_orphans() -> None:
    voice_data = VoiceData(
        mstSvtVoice=[make_svt_voice(100100, "0_B010")],
        mstSubtitle=make_subtitles("100100_0_B010"),
    )
    conn = CountingConnection()

    audio_urls = await get_subtitle_audio_urls(
        cast(AsyncConnection, conn), Region.NA, voice_data
    )

    assert audio_urls is None
    assert conn.queries == 0
