from ....schemas.nice import NiceVoiceGroup, NiceVoiceLine


def get_voice_lines(
    voice_groups: list[NiceVoiceGroup], svt_id: int, voice_ids: list[str]
) -> list[NiceVoiceLine]:
    return [
        voice_line
        for voice_group in voice_groups
        for voice_line in voice_group.voiceLines
        if voice_group.svtId == svt_id and set(voice_ids).intersection(voice_line.id)
    ]
