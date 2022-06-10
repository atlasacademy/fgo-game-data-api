from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncConnection

from ....config import Settings
from ....schemas.common import Language, Region
from ....schemas.gameenums import EVENT_TYPE_NAME, NiceSvtVoiceType, NiceVoiceCondType
from ....schemas.nice import AssetURL, NiceEvent, NiceVoiceGroup
from ....schemas.raw import MstGift
from ... import raw
from ...utils import fmt_url, get_translation
from ..bgm import get_nice_bgm_entity_from_raw
from ..item import get_nice_item_from_raw
from ..svt.voice import get_nice_voice_group
from .digging import get_nice_digging
from .lottery import get_nice_lottery
from .mission import get_nice_missions
from .point import get_nice_pointBuff, get_nice_pointGroup
from .reward import get_nice_reward
from .reward_scene import get_nice_event_reward_scene
from .shop import get_nice_shop
from .tower import get_nice_event_tower
from .treasure_box import get_nice_treasure_box
from .utils import GiftData
from .voice_play import get_nice_event_voice_play


settings = Settings()


async def get_nice_event(
    conn: AsyncConnection, region: Region, event_id: int, lang: Language
) -> NiceEvent:
    raw_event = await raw.get_event_entity(conn, event_id)

    base_settings = {"base_url": settings.asset_url, "region": region}

    shop_scripts = {
        shop_script.shopId: shop_script for shop_script in raw_event.mstShopScript
    }

    gift_maps: dict[int, list[MstGift]] = defaultdict(list)
    for gift in raw_event.mstGift:
        gift_maps[gift.id].append(gift)

    item_map = {
        item.id: get_nice_item_from_raw(region, item, lang)
        for item in raw_event.mstItem
    }

    common_consumes = {consume.id: consume for consume in raw_event.mstCommonConsume}

    gift_data = GiftData(raw_event.mstGiftAdd, gift_maps)

    missions = get_nice_missions(
        region,
        raw_event.mstEventMission,
        raw_event.mstEventMissionCondition,
        raw_event.mstEventMissionConditionDetail,
        gift_data,
    )

    nice_bgms = {
        bgm.mstBgm.id: get_nice_bgm_entity_from_raw(region, bgm, lang)
        for bgm in raw_event.mstBgm
    }

    mstVoices = {voice.id: voice for voice in raw_event.mstVoice}
    voice_groups: list[NiceVoiceGroup] = []
    for svt_voice in raw_event.mstSvtVoice:
        subtitle_ids = {
            subtitle.id: subtitle.serif
            for subtitle in raw_event.mstSubtitle
            if subtitle.get_svtId() == svt_voice.id
        }
        costume_ids = {
            costumeMap.id: costumeMap.battleCharaId
            for mstSvtExtra in raw_event.mstSvtExtra
            for limitCount, costumeMap in mstSvtExtra.costumeLimitSvtIdMap.items()
            if mstSvtExtra.svtId == svt_voice.id and limitCount > 10
        }

        voice_groups.append(
            get_nice_voice_group(
                region=region,
                voice=svt_voice,
                costume_ids=costume_ids,
                subtitle_ids=subtitle_ids,
                play_conds=raw_event.mstVoicePlayCond,
                mstVoices=mstVoices,
                mstSvtGroups=raw_event.mstSvtGroup,
                lang=lang,
            )
        )

    known_voice_ids: dict[int, set[str]] = defaultdict(set)
    for gacha_talk in raw_event.mstBoxGachaTalk:
        known_voice_ids[gacha_talk.guideImageId] |= set(gacha_talk.befVoiceIds)
        known_voice_ids[gacha_talk.guideImageId] |= set(gacha_talk.aftVoiceIds)
    for voice_play in raw_event.mstEventVoicePlay:
        known_voice_ids[voice_play.guideImageId] |= set(voice_play.voiceIds)
        known_voice_ids[voice_play.guideImageId] |= set(voice_play.confirmVoiceIds)

    shop_voice_conds = {
        NiceVoiceCondType.eventNoend,
        NiceVoiceCondType.eventEnd,
        NiceVoiceCondType.eventPeriod,
        NiceVoiceCondType.eventShopPurchase,
        NiceVoiceCondType.spacificShopPurchase,
        NiceVoiceCondType.eventMissionAction,
    }

    event_voices: list[NiceVoiceGroup] = []
    for voice_group in voice_groups:
        event_voice_lines = [
            voice_line
            for voice_line in voice_group.voiceLines
            if {
                voice_line_cond.condType for voice_line_cond in voice_line.conds
            }.intersection(shop_voice_conds)
            or known_voice_ids.get(voice_group.svtId, set()).intersection(voice_line.id)
        ]
        if event_voice_lines and voice_group.type != NiceSvtVoiceType.treasureDevice:
            event_voices.append(
                NiceVoiceGroup(
                    svtId=voice_group.svtId,
                    voicePrefix=voice_group.voicePrefix,
                    type=voice_group.type,
                    voiceLines=event_voice_lines,
                )
            )

    nice_event = NiceEvent(
        id=raw_event.mstEvent.id,
        type=EVENT_TYPE_NAME[raw_event.mstEvent.type],
        name=get_translation(lang, raw_event.mstEvent.name),
        originalName=raw_event.mstEvent.name,
        shortName=raw_event.mstEvent.shortName,
        detail=raw_event.mstEvent.detail,
        noticeBanner=fmt_url(
            AssetURL.banner,
            **base_settings,
            banner=f"event_war_{raw_event.mstEvent.noticeBannerId}",
        )
        if raw_event.mstEvent.noticeBannerId != 0
        else None,
        banner=fmt_url(
            AssetURL.banner,
            **base_settings,
            banner=f"event_war_{raw_event.mstEvent.bannerId}",
        )
        if raw_event.mstEvent.bannerId != 0
        else None,
        icon=fmt_url(
            AssetURL.banner,
            **base_settings,
            banner=f"banner_icon_{raw_event.mstEvent.iconId}",
        )
        if raw_event.mstEvent.iconId != 0
        else None,
        bannerPriority=raw_event.mstEvent.bannerPriority,
        noticeAt=raw_event.mstEvent.noticeAt,
        startedAt=raw_event.mstEvent.startedAt,
        endedAt=raw_event.mstEvent.endedAt,
        finishedAt=raw_event.mstEvent.finishedAt,
        materialOpenedAt=raw_event.mstEvent.materialOpenedAt,
        warIds=[war.id for war in raw_event.mstWar],
        shop=[
            get_nice_shop(
                region,
                shop,
                raw_event.mstSetItem,
                shop_scripts,
                item_map,
                raw_event.mstShopRelease,
            )
            for shop in raw_event.mstShop
        ],
        rewards=[
            get_nice_reward(region, reward, event_id, gift_data)
            for reward in raw_event.mstEventReward
        ],
        rewardScenes=[
            get_nice_event_reward_scene(region, reward_scene, nice_bgms)
            for reward_scene in raw_event.mstEventRewardScene
        ],
        pointGroups=[
            get_nice_pointGroup(region, pointGroup)
            for pointGroup in raw_event.mstEventPointGroup
        ],
        pointBuffs=[
            get_nice_pointBuff(region, pointBuff)
            for pointBuff in raw_event.mstEventPointBuff
        ],
        missions=missions,
        towers=[
            get_nice_event_tower(
                region, tower, raw_event.mstEventTowerReward, gift_data
            )
            for tower in raw_event.mstEventTower
        ],
        lotteries=[
            get_nice_lottery(
                region,
                lottery,
                raw_event.mstBoxGachaBase,
                raw_event.mstBoxGachaTalk,
                gift_data,
                item_map,
                raw_event.mstEventRewardScene,
                voice_groups,
            )
            for lottery in raw_event.mstBoxGacha
        ],
        treasureBoxes=[
            get_nice_treasure_box(
                region, box, raw_event.mstTreasureBoxGift, gift_data, common_consumes
            )
            for box in raw_event.mstTreasureBox
        ],
        digging=get_nice_digging(
            region,
            raw_event.mstEventDigging,
            raw_event.mstEventDiggingBlock,
            raw_event.mstEventDiggingReward,
            item_map=item_map,
            gift_data=gift_data,
            common_consumes=common_consumes,
        )
        if raw_event.mstEventDigging
        else None,
        voicePlays=[
            get_nice_event_voice_play(voice_play, voice_groups)
            for voice_play in raw_event.mstEventVoicePlay
        ],
        voices=event_voices,
    )

    return nice_event
