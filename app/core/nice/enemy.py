from dataclasses import dataclass
from typing import Any

from aioredis import Redis
from sqlalchemy.engine import Connection

from ...data.custom_mappings import Translation
from ...schemas.common import Language, Region
from ...schemas.enums import ATTRIBUTE_NAME, CLASS_NAME, ENEMY_DEATH_TYPE_NAME
from ...schemas.nice import (
    DeckType,
    EnemyAi,
    EnemyLimit,
    EnemyMisc,
    EnemyPassive,
    EnemyScript,
    EnemyServerMod,
    EnemySkill,
    EnemyTd,
    QuestEnemy,
)
from ...schemas.rayshift import Deck, DeckSvt, QuestDetail, UserSvt
from ..basic import get_basic_servant
from ..utils import get_traits_list, get_translation
from .skill import MultipleNiceSkills, SkillSvt, get_multiple_nice_skills
from .td import MultipleNiceTds, TdSvt, get_multiple_nice_tds


def get_enemy_misc(svt: UserSvt) -> EnemyMisc:
    return EnemyMisc(
        displayType=svt.displayType,
        npcSvtType=svt.npcSvtType,
        passiveSkill=svt.passiveSkill,
        equipTargetId1=svt.equipTargetId1,
        equipTargetIds=svt.equipTargetIds,
        npcSvtClassId=svt.npcSvtClassId,
        overwriteSvtId=svt.overwriteSvtId,
        userCommandCodeIds=svt.userCommandCodeIds if svt.userCommandCodeIds else [],
        commandCardParam=svt.commandCardParam,
        status=svt.status,
    )


def get_enemy_limit(svt: UserSvt) -> EnemyLimit:
    return EnemyLimit(
        limitCount=svt.limitCount,
        imageLimitCount=svt.imageLimitCount,
        dispLimitCount=svt.dispLimitCount,
        commandCardLimitCount=svt.commandCardLimitCount,
        iconLimitCount=svt.iconLimitCount,
        portraitLimitCount=svt.portraitLimitCount,
        battleVoice=svt.battleVoice,
        exceedCount=svt.exceedCount,
    )


def get_enemy_server_mod(svt: UserSvt) -> EnemyServerMod:
    return EnemyServerMod(
        tdRate=svt.tdRate,
        tdAttackRate=svt.tdAttackRate,
        starRate=svt.starRate,
    )


def get_enemy_ai(svt: UserSvt) -> EnemyAi:
    return EnemyAi(
        aiId=svt.aiId,
        actPriority=svt.actPriority,
        maxActNum=svt.maxActNum,
    )


def get_enemy_script(enemyScript: dict[str, Any]) -> EnemyScript:
    enemy_script: dict[str, Any] = {}

    as_is_script_keys = [
        "raid",
        "superBoss",
        "hpBarType",
        "scale",
        "svtVoiceId",
        "treasureDeviceVoiceId",
        "billBoardGroup",
        "deadChangePos",
        "shiftPosition",
        "entryIndex",
        "treasureDeviceName",
        "treasureDeviceRuby",
        "npCharge",
        "call",
        "shift",
        "change",
        "skillShift",
        "missionTargetSkillShift",
    ]
    for script_key in as_is_script_keys:
        if script_key in enemyScript:
            enemy_script[script_key] = enemyScript[script_key]

    bool_script_keys = [
        "leader",
        "appear",
        "multiTargetCore",
        "multiTargetUp",
        "multiTargetUnder",
        "startPos",
        "noVoice",
        "npInfoEnable",
        "NoSkipDead",
    ]
    for script_key in bool_script_keys:
        if script_key in enemyScript:
            enemy_script[script_key] = enemyScript[script_key] == 1

    if "kill" in enemyScript:
        enemy_script["deathType"] = ENEMY_DEATH_TYPE_NAME[enemyScript["kill"]]

    if "shiftClear" in enemyScript:
        trait_ids = [
            trait_id for trait_id in enemyScript["shiftClear"] if trait_id != 0
        ]
        enemy_script["shiftClear"] = get_traits_list(trait_ids)

    if "changeAttri" in enemyScript:
        enemy_script["changeAttri"] = ATTRIBUTE_NAME[enemyScript["changeAttri"]]

    if "forceDropItem" in enemyScript:
        enemy_script["forceDropItem"] = "forceDropItem" in enemyScript

    return EnemyScript.parse_obj(enemy_script)


def get_enemy_skills(svt: UserSvt, all_skills: MultipleNiceSkills) -> EnemySkill:
    return EnemySkill(
        skillId1=svt.skillId1,
        skillId2=svt.skillId2,
        skillId3=svt.skillId3,
        skill1=all_skills.get(SkillSvt(svt.skillId1, svt.svtId), None),
        skill2=all_skills.get(SkillSvt(svt.skillId2, svt.svtId), None),
        skill3=all_skills.get(SkillSvt(svt.skillId3, svt.svtId), None),
        skillLv1=svt.skillLv1,
        skillLv2=svt.skillLv2,
        skillLv3=svt.skillLv3,
    )


def get_enemy_passive(svt: UserSvt, all_skills: MultipleNiceSkills) -> EnemyPassive:
    return EnemyPassive(
        classPassive=[
            all_skills[SkillSvt(skill_id, svt.svtId)]
            for skill_id in svt.classPassive
            if SkillSvt(skill_id, svt.svtId) in all_skills
        ],
        addPassive=[
            all_skills[SkillSvt(skill_id, svt.svtId)]
            for skill_id in svt.addPassive
            if SkillSvt(skill_id, svt.svtId) in all_skills
        ]
        if svt.addPassive
        else [],
    )


def get_enemy_td(svt: UserSvt, all_nps: MultipleNiceTds) -> EnemyTd:
    return EnemyTd(
        noblePhantasmId=svt.treasureDeviceId,
        noblePhantasm=all_nps.get(TdSvt(svt.treasureDeviceId, svt.svtId), None),
        noblePhantasmLv=svt.treasureDeviceLv,
        noblePhantasmLv1=svt.treasureDeviceLv1,
    )


@dataclass
class EnemyDeckInfo:
    deckType: DeckType
    deck: DeckSvt

    def __hash__(self) -> int:
        return hash((self.deckType, self.deck.id))


async def get_quest_enemy(
    redis: Redis,
    region: Region,
    deck_svt_info: EnemyDeckInfo,
    user_svt: UserSvt,
    all_enemy_skills: MultipleNiceSkills,
    all_enemy_tds: MultipleNiceTds,
    lang: Language = Language.jp,
) -> QuestEnemy:
    deck_svt = deck_svt_info.deck
    basic_svt = await get_basic_servant(
        redis, region, user_svt.svtId, user_svt.limitCount, lang
    )

    if user_svt.npcSvtClassId != 0:
        basic_svt.className = CLASS_NAME[user_svt.npcSvtClassId]
    if (
        deck_svt.enemyScript and "changeAttri" in deck_svt.enemyScript
    ):  # pragma: no cover
        basic_svt.attribute = ATTRIBUTE_NAME[deck_svt.enemyScript["changeAttri"]]

    return QuestEnemy(
        deck=deck_svt_info.deckType,
        userSvtId=user_svt.id,
        uniqueId=deck_svt.uniqueId,
        npcId=deck_svt.npcId,
        name=get_translation(lang, deck_svt.name, Translation.ENEMY),
        svt=basic_svt,
        lv=user_svt.lv,
        exp=user_svt.exp,
        atk=user_svt.atk,
        hp=user_svt.hp,
        adjustAtk=user_svt.adjustAtk,
        adjustHp=user_svt.adjustHp,
        deathRate=user_svt.deathRate,
        criticalRate=user_svt.criticalRate,
        recover=user_svt.recover,
        chargeTurn=user_svt.chargeTurn,
        traits=get_traits_list(user_svt.individuality),
        skills=get_enemy_skills(user_svt, all_enemy_skills),
        classPassive=get_enemy_passive(user_svt, all_enemy_skills),
        noblePhantasm=get_enemy_td(user_svt, all_enemy_tds),
        serverMod=get_enemy_server_mod(user_svt),
        ai=get_enemy_ai(user_svt),
        enemyScript=get_enemy_script(
            deck_svt.enemyScript if deck_svt.enemyScript else {}
        ),
        limit=get_enemy_limit(user_svt),
        misc=get_enemy_misc(user_svt),
    )


def get_extra_decks(
    deck_svts: list[EnemyDeckInfo], npc_id_map: dict[DeckType, dict[int, DeckSvt]]
) -> list[EnemyDeckInfo]:
    extra_decks: list[EnemyDeckInfo] = []

    for deck_type, deck_key in (
        (DeckType.CALL, "call"),
        (DeckType.SHIFT, "shift"),
        (DeckType.CHANGE, "change"),
        (DeckType.SKILL_SHIFT, "skillShift"),
        (DeckType.MISSION_TARGET_SKILL_SHIFT, "missionTargetSkillShift"),
    ):
        for enemy in deck_svts:
            if enemy.deck.enemyScript and deck_key in enemy.deck.enemyScript:
                for npc_id in enemy.deck.enemyScript[deck_key]:
                    deck_info = EnemyDeckInfo(deck_type, npc_id_map[deck_type][npc_id])
                    if deck_info not in extra_decks:
                        extra_decks.append(deck_info)

    return extra_decks


def get_enemies_in_stage(
    enemy_deck_svts: list[EnemyDeckInfo], npc_id_map: dict[DeckType, dict[int, DeckSvt]]
) -> list[EnemyDeckInfo]:
    stage_enemies = [
        deck_info
        for deck_info in enemy_deck_svts
        if not deck_info.deck.infoScript
        or "isAddition" not in deck_info.deck.infoScript
    ]

    # For faster added checks. A quest can have hundreds of enemies but only at most 5 break bars
    added_npc_decks = set(stage_enemies)

    to_be_added_decks = get_extra_decks(stage_enemies, npc_id_map)

    while to_be_added_decks:
        stage_enemies += to_be_added_decks
        added_npc_decks |= set(to_be_added_decks)
        to_be_added_decks = [
            deck
            for deck in get_extra_decks(stage_enemies, npc_id_map)
            if deck not in added_npc_decks
        ]

    return stage_enemies


async def get_quest_enemies(
    conn: Connection,
    redis: Redis,
    region: Region,
    quest_detail: QuestDetail,
    lang: Language = Language.jp,
) -> list[list[QuestEnemy]]:
    npc_id_map: dict[DeckType, dict[int, DeckSvt]] = {}
    DECK_LIST: list[tuple[list[Deck], DeckType]] = [
        (quest_detail.enemyDeck, DeckType.ENEMY),
        (quest_detail.callDeck, DeckType.CALL),
        (quest_detail.shiftDeck, DeckType.SHIFT),
        (quest_detail.shiftDeck, DeckType.CHANGE),
        (quest_detail.shiftDeck, DeckType.SKILL_SHIFT),
        (quest_detail.shiftDeck, DeckType.MISSION_TARGET_SKILL_SHIFT),
    ]
    for decks, deck_type in DECK_LIST:
        npc_id_map[deck_type] = {
            deck_svt.npcId: deck_svt for deck in decks for deck_svt in deck.svts
        }

    user_svt_id = {svt.id: svt for svt in quest_detail.userSvt}

    all_skill_ids: set[SkillSvt] = set()
    all_td_ids: set[TdSvt] = set()
    for user_svt in quest_detail.userSvt:
        if user_svt.treasureDeviceId != 0:
            all_td_ids.add(TdSvt(user_svt.treasureDeviceId, user_svt.svtId))
        for skill_id in [
            user_svt.skillId1,
            user_svt.skillId2,
            user_svt.skillId3,
            *user_svt.classPassive,
            *(user_svt.addPassive if user_svt.addPassive else []),
        ]:
            if skill_id != 0:
                all_skill_ids.add(SkillSvt(skill_id, user_svt.svtId))

    # Get all skills and NPs data at once to avoid calling the DB a lot of times
    all_skills = get_multiple_nice_skills(conn, region, all_skill_ids, lang)
    all_tds = get_multiple_nice_tds(conn, region, all_td_ids, lang)

    out_enemies: list[list[QuestEnemy]] = []
    for enemy_deck in quest_detail.enemyDeck:
        enemy_decks = [
            EnemyDeckInfo(DeckType.ENEMY, enemy)
            for enemy in sorted(enemy_deck.svts, key=lambda enemy: enemy.id)
            if not enemy.infoScript or "isAddition" not in enemy.infoScript
        ]
        enemy_decks += [
            EnemyDeckInfo(DeckType.TRANSFORM, enemy)
            for enemy in quest_detail.transformDeck.svts
            if not enemy.infoScript or "isAddition" not in enemy.infoScript
        ]

        stage_nice_enemies: list[QuestEnemy] = []
        for deck_svt_info in get_enemies_in_stage(enemy_decks, npc_id_map):
            nice_enemy = await get_quest_enemy(
                redis=redis,
                region=region,
                deck_svt_info=deck_svt_info,
                user_svt=user_svt_id[deck_svt_info.deck.userSvtId],
                all_enemy_skills=all_skills,
                all_enemy_tds=all_tds,
                lang=lang,
            )
            stage_nice_enemies.append(nice_enemy)

        out_enemies.append(stage_nice_enemies)

    return out_enemies
