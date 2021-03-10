from sqlalchemy.engine import Connection

from ...schemas.common import Language, Region
from ...schemas.nice import (
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
from ...schemas.rayshift import DeckSvt, QuestDetail, UserSvt
from ..basic import get_basic_servant
from ..utils import get_traits_list
from .skill import MultipleNiceSkills, get_multiple_nice_skills
from .td import MultipleNiceTds, get_multiple_nice_tds


def get_enemy_misc(svt: UserSvt) -> EnemyMisc:
    return EnemyMisc(
        displayType=svt.displayType,
        npcSvtType=svt.npcSvtType,
        passiveSkill=svt.passiveSkill,
        equipTargetId1=svt.equipTargetId1,
        equipTargetIds=svt.equipTargetIds,
        npcSvtClassId=svt.npcSvtClassId,
        overwriteSvtId=svt.overwriteSvtId,
        userCommandCodeIds=svt.userCommandCodeIds,
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


def npc_id_to_user_svt_id(
    npc_ids: list[int], npc_id_to_deck: dict[int, DeckSvt]
) -> list[int]:
    return [npc_id_to_deck[npc_id].userSvtId for npc_id in npc_ids]


def get_enemy_script(
    deck_svt: DeckSvt,
    npc_id_to_deck: dict[int, DeckSvt],
) -> EnemyScript:
    enemy_script = EnemyScript()

    if "leader" in deck_svt.enemyScript:
        enemy_script.leader = deck_svt.enemyScript["leader"] == 1
    if "call" in deck_svt.enemyScript:
        enemy_script.call = npc_id_to_user_svt_id(
            deck_svt.enemyScript["call"], npc_id_to_deck
        )
    if "shift" in deck_svt.enemyScript:
        enemy_script.shift = npc_id_to_user_svt_id(
            deck_svt.enemyScript["shift"], npc_id_to_deck
        )

    return enemy_script


def get_enemy_skills(svt: UserSvt, all_skills: MultipleNiceSkills) -> EnemySkill:
    return EnemySkill(
        skillId1=svt.skillId1,
        skillId2=svt.skillId2,
        skillId3=svt.skillId3,
        skill1=all_skills.get((svt.skillId1, svt.svtId), None),
        skill2=all_skills.get((svt.skillId2, svt.svtId), None),
        skill3=all_skills.get((svt.skillId3, svt.svtId), None),
        skillLv1=svt.skillLv1,
        skillLv2=svt.skillLv2,
        skillLv3=svt.skillLv3,
    )


def get_enemy_passive(svt: UserSvt, all_skills: MultipleNiceSkills) -> EnemyPassive:
    return EnemyPassive(
        classPassive=[
            all_skills[(skill_id, svt.svtId)] for skill_id in svt.classPassive
        ],
        addPassive=[all_skills[(skill_id, svt.svtId)] for skill_id in svt.addPassive],
    )


def get_enemy_td(svt: UserSvt, all_nps: MultipleNiceTds) -> EnemyTd:
    return EnemyTd(
        noblePhantasm=all_nps[(svt.treasureDeviceId, svt.svtId)],
        noblePhantasmLv=svt.treasureDeviceLv,
        noblePhantasmLv1=svt.treasureDeviceLv1,
    )


def get_quest_enemy(
    region: Region,
    svt: UserSvt,
    all_enemy_skills: MultipleNiceSkills,
    all_enemy_tds: MultipleNiceTds,
    user_svt_id_to_deck: dict[int, DeckSvt],
    npc_id_to_deck: dict[int, DeckSvt],
    lang: Language = Language.jp,
) -> QuestEnemy:
    """Turns raw quest enemy data into nice quest enemy data.

    `user_svt_id_to_deck` and `npc_id_to_deck` are convienent mappings
    used to get the relevant DectSvt data.

    Args:
        `region`: Region
        `svt`: Input UserSvt to generate nice data
        `all_enemy_skills`: All enemy skills mapping
        `all_enemy_tds`: All enemy NPs mapping
        `user_svt_id_to_deck`: Mapping of userSvtId to DeckSvt
        `npc_id_to_deck`: Mapping of npcId to DeckSvt
        `lang`: Language

    Returns:
        Nice Quest Enemy
    """

    deck_svt = user_svt_id_to_deck[svt.id]
    basic_svt = get_basic_servant(region, svt.svtId, lang)

    return QuestEnemy(
        id=svt.id,
        name=deck_svt.name,
        svt=basic_svt,
        lv=svt.lv,
        exp=svt.exp,
        atk=svt.atk,
        hp=svt.hp,
        adjustAtk=svt.adjustAtk,
        adjustHp=svt.adjustHp,
        deathRate=svt.deathRate,
        criticalRate=svt.criticalRate,
        recover=svt.recover,
        chargeTurn=svt.chargeTurn,
        traits=get_traits_list(svt.individuality),
        skills=get_enemy_skills(svt, all_enemy_skills),
        classPassive=get_enemy_passive(svt, all_enemy_skills),
        noblePhantasm=get_enemy_td(svt, all_enemy_tds),
        serverMod=get_enemy_server_mod(svt),
        ai=get_enemy_ai(svt),
        enemyScript=get_enemy_script(deck_svt, npc_id_to_deck),
        limit=get_enemy_limit(svt),
        misc=get_enemy_misc(svt),
    )


def get_quest_enemies(
    conn: Connection,
    region: Region,
    quest_detail: QuestDetail,
    lang: Language = Language.jp,
) -> list[list[QuestEnemy]]:
    user_svt_id_deck: dict[int, DeckSvt] = {}
    for deck in [
        *quest_detail.enemyDeck,
        quest_detail.transformDeck,
        *quest_detail.callDeck,
        *quest_detail.shiftDeck,
    ]:
        for deck_svt in deck.svts:
            user_svt_id_deck[deck_svt.userSvtId] = deck_svt

    npc_id_deck = {svt.npcId: svt for svt in user_svt_id_deck.values()}

    user_svt_id = {svt.id: svt for svt in quest_detail.userSvt}

    all_skills: set[tuple[int, int]] = set()
    all_tds: set[tuple[int, int]] = set()
    for user_svt in quest_detail.userSvt:
        all_tds.add((user_svt.treasureDeviceId, user_svt.svtId))
        for skill_id in [
            user_svt.skillId1,
            user_svt.skillId2,
            user_svt.skillId3,
            *user_svt.classPassive,
            *user_svt.addPassive,
        ]:
            if skill_id != 0:
                all_skills.add((skill_id, user_svt.svtId))

    # Get all skills and NPs data at once to avoid calling the DB a lot of times
    all_nice_skills = get_multiple_nice_skills(conn, region, all_skills, lang)
    all_nice_tds = get_multiple_nice_tds(conn, region, all_tds)

    out_enemies: list[list[QuestEnemy]] = []
    for enemy_deck in quest_detail.enemyDeck:
        stage_enemies = enemy_deck.svts
        for deck_svt in enemy_deck.svts:
            for more_svt_type in ("shift", "call"):
                if more_svt_type in deck_svt.enemyScript:
                    stage_enemies += [
                        npc_id_deck[npc_id]
                        for npc_id in deck_svt.enemyScript[more_svt_type]
                    ]

        stage_nice_enemies: list[QuestEnemy] = []
        for deck_svt in stage_enemies:
            nice_enemy = get_quest_enemy(
                region,
                user_svt_id[deck_svt.userSvtId],
                all_nice_skills,
                all_nice_tds,
                user_svt_id_deck,
                npc_id_deck,
                lang,
            )
            stage_nice_enemies.append(nice_enemy)

        out_enemies.append(stage_nice_enemies)

    return out_enemies
