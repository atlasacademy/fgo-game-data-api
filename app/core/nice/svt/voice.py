from typing import Iterator, Mapping, NamedTuple, Optional, Protocol

from sqlalchemy.ext.asyncio import AsyncConnection

from ....config import Settings
from ....data.custom_mappings import Translation
from ....db.helpers import asset
from ....schemas.common import Language, Region
from ....schemas.gameenums import (
    COND_TYPE_NAME,
    VOICE_COND_NAME,
    VOICE_TYPE_NAME,
    NiceVoiceCondType,
    SvtVoiceType,
    VoiceCondType,
)
from ....schemas.nice import (
    AssetURL,
    NiceVoiceCond,
    NiceVoiceGroup,
    NiceVoiceLine,
    NiceVoicePlayCond,
    NiceVoiceSubtitle,
)
from ....schemas.raw import (
    GlobalNewMstSubtitle,
    MstSvtGroup,
    MstSvtVoice,
    MstVoice,
    MstVoicePlayCond,
    ScriptJson,
    ScriptJsonCond,
)
from ...utils import get_voice_name, nullable_to_string
from ..base_script import get_nice_script_link

settings = Settings()


AUDIO_FOLDER_PREFIXES = ("Servants_", "NoblePhantasm_", "ChrVoice_")


def get_voice_folder(voice_type: int) -> str:
    if voice_type == SvtVoiceType.BATTLE:
        return "Servants_"
    elif voice_type == SvtVoiceType.TREASURE_DEVICE:
        return "NoblePhantasm_"
    else:
        return "ChrVoice_"


def get_voice_url(region: Region, svt_id: int, voice_type: int, voice_id: str) -> str:
    folder = get_voice_folder(voice_type) + str(svt_id)
    return AssetURL.audio.format(
        base_url=settings.asset_url, region=region, folder=folder, id=voice_id
    )


def get_audio_candidates(svt_id: int, voice_type: int, voice_id: str) -> list[str]:
    """Asset manifest file names a voice line could have, the typed folder first.

    The manifest says which files exist but not which line they belong to,
    so the folder mstVoice points at is tried before the other two.
    """
    preferred = f"{get_voice_folder(voice_type)}{svt_id}/{voice_id}.mp3"
    return [preferred] + [
        name
        for prefix in AUDIO_FOLDER_PREFIXES
        if (name := f"{prefix}{svt_id}/{voice_id}.mp3") != preferred
    ]


def get_voice_scripts(voice: MstSvtVoice) -> list[ScriptJson]:
    """Scripts of a voice group that turn into a voice line."""
    return [
        script for script in voice.scriptJson if script is not None and script.infos
    ]


def get_script_subtitle_id(svt_id: int, script: ScriptJson) -> str:
    """mstSubtitle key of a voice line: the svt id and the id of its first info."""
    return f"{svt_id}_{script.infos[0].id}"


def get_nice_play_cond(playCond: MstVoicePlayCond) -> NiceVoicePlayCond:
    return NiceVoicePlayCond(
        condGroup=playCond.condGroup,
        condType=COND_TYPE_NAME[playCond.condType],
        targetId=playCond.targetId,
        condValue=playCond.condValues[0] if playCond.condValues else 0,
        condValues=playCond.condValues,
    )


def get_nice_voice_cond(
    cond: ScriptJsonCond, costume_ids: dict[int, int], mstSvtGroups: list[MstSvtGroup]
) -> NiceVoiceCond:
    cond_value = (
        costume_ids[cond.value]
        if cond.condType == VoiceCondType.COSTUME and cond.value in costume_ids
        else cond.value
    )

    cond_value_list = (
        [group.svtId for group in mstSvtGroups if group.id == cond.value]
        if cond.condType == VoiceCondType.SVT_GROUP
        else []
    )

    voice_cond = NiceVoiceCond(
        condType=VOICE_COND_NAME.get(cond.condType, NiceVoiceCondType.unknown),
        eventId=cond.eventId,
        value=cond_value,
        valueList=cond_value_list,
    )

    return voice_cond


def get_nice_voice_line(
    region: Region,
    script: ScriptJson,
    svt_id: int,
    voice_prefix: int,
    voice_type: int,
    costume_ids: dict[int, int],
    subtitle_ids: dict[str, str],
    play_conds: list[MstVoicePlayCond],
    mstVoices: dict[str, MstVoice],
    mstSvtGroups: list[MstSvtGroup],
    lang: Language,
) -> NiceVoiceLine:
    first_voice = script.infos[0]
    voice_id = first_voice.get_voice_id()

    voice_line = NiceVoiceLine(
        overwriteName=get_voice_name(
            nullable_to_string(script.overwriteName), lang, Translation.OVERWRITE_VOICE
        ),
        id=[info.id for info in script.infos],
        audioAssets=[
            get_voice_url(region, svt_id, voice_type, info.id) for info in script.infos
        ],
        delay=[info.delay for info in script.infos],
        face=[info.face for info in script.infos],
        form=[info.form for info in script.infos],
        text=[nullable_to_string(info.text) for info in script.infos],
        conds=[
            get_nice_voice_cond(info, costume_ids, mstSvtGroups)
            for info in (script.conds if script.conds is not None else [])
        ],
        playConds=[
            get_nice_play_cond(play_cond)
            for play_cond in play_conds
            if play_cond.svtId == svt_id
            and play_cond.voiceId == voice_id
            and play_cond.voicePrefix in (-1, voice_prefix)
        ],
        subtitle=subtitle_ids.get(get_script_subtitle_id(svt_id, script), ""),
    )

    if script.summonScript is not None and script.summonScript != "":
        voice_line.summonScript = get_nice_script_link(region, script.summonScript)

    if voice_id in mstVoices:
        mstVoice = mstVoices[voice_id]
        voice_line.name = get_voice_name(mstVoice.name, lang, Translation.VOICE)
        voice_line.condType = COND_TYPE_NAME[mstVoice.condType]
        voice_line.condValue = mstVoice.condValue
        voice_line.priority = mstVoice.priority
        voice_line.svtVoiceType = VOICE_TYPE_NAME[mstVoice.svtVoiceType]

    return voice_line


def get_nice_voice_group(
    region: Region,
    voice: MstSvtVoice,
    costume_ids: dict[int, int],
    subtitle_ids: dict[str, str],
    play_conds: list[MstVoicePlayCond],
    mstVoices: dict[str, MstVoice],
    mstSvtGroups: list[MstSvtGroup],
    lang: Language,
) -> NiceVoiceGroup:
    return NiceVoiceGroup(
        svtId=voice.id,
        voicePrefix=voice.voicePrefix,
        type=VOICE_TYPE_NAME[voice.type],
        voiceLines=[
            get_nice_voice_line(
                region,
                script,
                voice.id,
                voice.voicePrefix,
                voice.type,
                costume_ids,
                subtitle_ids,
                play_conds,
                mstVoices,
                mstSvtGroups,
                lang,
            )
            for script in get_voice_scripts(voice)
        ],
    )


class RequiredVoiceData(Protocol):
    mstSvtVoice: list[MstSvtVoice]
    mstVoice: list[MstVoice]
    mstVoicePlayCond: list[MstVoicePlayCond]
    mstSvtGroup: list[MstSvtGroup]
    mstSubtitle: list[GlobalNewMstSubtitle]


def get_nice_voice(
    region: Region,
    voice_data: RequiredVoiceData,
    costume_ids: dict[int, int],
    lang: Language,
) -> list[NiceVoiceGroup]:
    subtitle_ids = {subtitle.id: subtitle.serif for subtitle in voice_data.mstSubtitle}
    mstVoices = {voice.id: voice for voice in voice_data.mstVoice}

    return [
        get_nice_voice_group(
            region,
            voice,
            costume_ids,
            subtitle_ids,
            voice_data.mstVoicePlayCond,
            mstVoices,
            voice_data.mstSvtGroup,
            lang,
        )
        for voice in voice_data.mstSvtVoice
    ]


def pick_audio_asset(
    svt_id: int,
    voice_type: int,
    voice_id: str,
    audio_urls: Mapping[str, str],
) -> Optional[str]:
    """The manifest's URL for a voice line, None when it lists no audio for it."""
    for candidate in get_audio_candidates(svt_id, voice_type, voice_id):
        if candidate in audio_urls:
            return audio_urls[candidate]

    return None


class OrphanSubtitle(NamedTuple):
    """A subtitle with no voice line, and what names its audio file could have."""

    subtitle: GlobalNewMstSubtitle
    svt_id: int
    voice_type: int
    voice_id: str


def iter_orphan_subtitles(
    voice_data: RequiredVoiceData,
) -> Iterator[OrphanSubtitle]:
    """Subtitles that don't belong to any voice line.

    Story enemies usually have no mstVoice or mstSvtVoice rows at all,
    so their battle dialogue is only present in mstSubtitle
    and would otherwise never show up in the nice data.

    Both the audio lookup and the nice models walk this,
    so the orphan rule can't drift between them.
    """
    # Only NA and KR ship subtitle data, so everywhere else there is nothing to match
    if not voice_data.mstSubtitle:
        return

    voice_line_ids = {
        get_script_subtitle_id(voice.id, script)
        for voice in voice_data.mstSvtVoice
        for script in get_voice_scripts(voice)
    }
    mstVoices = {voice.id: voice for voice in voice_data.mstVoice}

    for subtitle in voice_data.mstSubtitle:
        if subtitle.id in voice_line_ids or "_" not in subtitle.id:
            continue

        svt_id = subtitle.get_svtId()
        if svt_id == -1:
            continue

        # An orphan has no voice group, so there's no mstSvtVoice.type to read,
        # but mstVoice keys on the voice id and carries the same type:
        # B010 is battle while B050 is treasureDevice, so the letter alone
        # would be ambiguous where the whole id isn't.
        mstVoice = mstVoices.get(subtitle.get_voice_id())

        yield OrphanSubtitle(
            subtitle=subtitle,
            svt_id=svt_id,
            voice_type=mstVoice.svtVoiceType if mstVoice else SvtVoiceType.BATTLE,
            voice_id=subtitle.id.split("_", 1)[1],
        )


def get_subtitle_audio_candidates(voice_data: RequiredVoiceData) -> list[str]:
    """Every manifest file name this svt's orphan subtitles could point at."""
    return [
        candidate
        for orphan in iter_orphan_subtitles(voice_data)
        for candidate in get_audio_candidates(
            orphan.svt_id, orphan.voice_type, orphan.voice_id
        )
    ]


async def get_subtitle_audio_urls(
    conn: AsyncConnection, voice_data: RequiredVoiceData
) -> dict[str, str]:
    """Manifest URLs for this svt's orphan subtitles.

    An empty result means the manifest lists no audio for any of them, which is
    the ordinary answer for leftover rows whose files were removed from the
    game. get_audio_urls skips the query when there is nothing to look up.
    """
    return await asset.get_audio_urls(conn, get_subtitle_audio_candidates(voice_data))


def get_nice_subtitles(
    voice_data: RequiredVoiceData, audio_urls: Mapping[str, str]
) -> list[NiceVoiceSubtitle]:
    """Nice models for the subtitles that no voice line covers."""
    return [
        NiceVoiceSubtitle(
            id=orphan.subtitle.id,
            serif=orphan.subtitle.serif,
            audioAsset=pick_audio_asset(
                orphan.svt_id, orphan.voice_type, orphan.voice_id, audio_urls
            ),
        )
        for orphan in iter_orphan_subtitles(voice_data)
    ]
