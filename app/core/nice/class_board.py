from sqlalchemy.ext.asyncio import AsyncConnection

from ...config import Settings
from ...schemas.common import Language, Region
from ...schemas.enums import get_class_name
from ...schemas.gameenums import (
    CLASS_BOARD_SKILL_TYPE_NAME,
    CLASS_BOARD_SQUARE_FLAG_NAME,
    COND_TYPE_NAME,
    ClassBoardSkillType,
)
from ...schemas.nice import (
    AssetURL,
    NiceClassBoard,
    NiceClassBoardClass,
    NiceClassBoardCommandSpell,
    NiceClassBoardLine,
    NiceClassBoardLock,
    NiceClassBoardSquare,
    NiceFunction,
    NiceSkill,
)
from ...schemas.raw import (
    MstClassBoardBase,
    MstClassBoardClass,
    MstClassBoardCommandSpell,
    MstClassBoardLine,
    MstClassBoardLock,
    MstClassBoardSquare,
    MstItem,
    SkillEntityNoReverse,
)
from .. import raw
from ..utils import fmt_url, get_flags, get_translation
from .func import get_nice_function
from .item import get_nice_item_amount, get_nice_item_from_raw
from .skill import get_nice_skill_from_raw


settings = Settings()


def get_nice_class_board_class(
    class_board_class: MstClassBoardClass,
) -> NiceClassBoardClass:
    return NiceClassBoardClass(
        classId=class_board_class.classId,
        className=get_class_name(class_board_class.classId),
        condType=COND_TYPE_NAME[class_board_class.condType],
        condTargetId=class_board_class.condTargetId,
        condNum=class_board_class.condNum,
    )


async def get_nice_class_board_command_spell(
    conn: AsyncConnection,
    region: Region,
    class_board_css: list[MstClassBoardCommandSpell],
    lang: Language,
) -> NiceClassBoardCommandSpell:
    functions: list[NiceFunction] = []
    for funci, function in enumerate(class_board_css[0].expandedFuncId):
        nice_func = NiceFunction.parse_obj(
            await get_nice_function(
                conn,
                region,
                function,
                lang,
                svals=[
                    cs.svals[funci] for cs in class_board_css if cs.commandSpellId == 1
                ],
            )
        )

        functions.append(nice_func)

    return NiceClassBoardCommandSpell(
        id=class_board_css[0].id,
        commandSpellId=class_board_css[0].commandSpellId,
        name=class_board_css[0].name,
        detail=class_board_css[0].detail,
        functions=functions,
    )


def get_nice_class_board_lock(
    region: Region,
    lock: MstClassBoardLock,
    items_map: dict[int, MstItem],
    lang: Language,
) -> NiceClassBoardLock:
    return NiceClassBoardLock(
        id=lock.id,
        items=get_nice_item_amount(
            [
                get_nice_item_from_raw(region, items_map[item_id], lang)
                for item_id in lock.itemIds
            ],
            lock.itemNums,
        ),
        closedMessage=lock.closedMessage,
        condType=COND_TYPE_NAME[lock.condType],
        condTargetId=lock.condTargetId,
        condNum=lock.condNum,
    )


async def get_nice_class_board_square(
    conn: AsyncConnection,
    region: Region,
    square: MstClassBoardSquare,
    items_map: dict[int, MstItem],
    skills_map: dict[int, SkillEntityNoReverse],
    class_command_spells: list[MstClassBoardCommandSpell],
    class_board_locks: list[MstClassBoardLock],
    lang: Language,
) -> NiceClassBoardSquare:
    if square.skillType == ClassBoardSkillType.PASSIVE:
        skill = await get_nice_skill_from_raw(
            conn, region, skills_map[square.targetId], NiceSkill, lang
        )
    else:
        skill = None

    target_cs = [cs for cs in class_command_spells if cs.id == square.targetId]
    if square.skillType == ClassBoardSkillType.COMMAND_SPELL and target_cs:
        command_spell = await get_nice_class_board_command_spell(
            conn, region, target_cs, lang
        )
    else:
        command_spell = None

    if square.lockId != 0:
        lock = get_nice_class_board_lock(
            region,
            next(lock for lock in class_board_locks if lock.id == square.lockId),
            items_map,
            lang,
        )
    else:
        lock = None

    icon = None
    if square.iconId != 0:
        if square.skillType == ClassBoardSkillType.PASSIVE:
            icon = fmt_url(
                AssetURL.classBoardIcon,
                base_url=settings.asset_url,
                region=region,
                item_id=f"skill_{square.iconId:05d}",
            )
        elif square.skillType == ClassBoardSkillType.COMMAND_SPELL:
            icon = fmt_url(
                AssetURL.classBoardIcon,
                base_url=settings.asset_url,
                region=region,
                item_id=f"cs_{square.iconId:04d}1",
            )

    return NiceClassBoardSquare(
        id=square.id,
        icon=icon,
        items=get_nice_item_amount(
            items=[
                get_nice_item_from_raw(region, items_map[item_id], lang)
                for item_id in square.itemIds
            ],
            amounts=square.itemNums,
        ),
        posX=square.posX,
        posY=square.posY,
        skillType=CLASS_BOARD_SKILL_TYPE_NAME[square.skillType],
        targetSkill=skill,
        upSkillLv=square.upSkillLv,
        targetCommandSpell=command_spell,
        lock=lock,
        flags=get_flags(square.flag, CLASS_BOARD_SQUARE_FLAG_NAME),
        priority=square.flag,
    )


def get_nice_class_board_line(line: MstClassBoardLine) -> NiceClassBoardLine:
    return NiceClassBoardLine(
        id=line.id,
        prevSquareId=line.prevSquareId,
        nextSquareId=line.nextSquareId,
    )


async def get_nice_class_board(
    conn: AsyncConnection, region: Region, class_board_id: int, lang: Language
) -> NiceClassBoard:
    raw_class_board = await raw.get_class_board_entity(conn, class_board_id)

    base_settings = {"base_url": settings.asset_url, "region": region}

    mstClassBoardBase = raw_class_board.mstClassBoardBase
    items_map = {item.id: item for item in raw_class_board.mstItem}
    skills_map = {skill.mstSkill.id: skill for skill in raw_class_board.mstSkill}
    return NiceClassBoard(
        id=mstClassBoardBase.id,
        name=get_translation(lang, mstClassBoardBase.name),
        icon=fmt_url(
            AssetURL.classBoardBg,
            **base_settings,
            item_id=f"ClassIcon{mstClassBoardBase.iconId}",
        ),
        dispItems=[
            get_nice_item_from_raw(region, items_map[itemId], lang)
            for itemId in mstClassBoardBase.dispItemIds
            if itemId in items_map
        ],
        closedMessage=mstClassBoardBase.closedMessage,
        condType=COND_TYPE_NAME[mstClassBoardBase.condType],
        condTargetId=mstClassBoardBase.condTargetId,
        condNum=mstClassBoardBase.condNum,
        parentClassBoardBaseId=mstClassBoardBase.parentClassBoardBaseId or 0,
        classes=[
            get_nice_class_board_class(class_board_class)
            for class_board_class in raw_class_board.mstClassBoardClass
        ],
        squares=[
            await get_nice_class_board_square(
                conn,
                region,
                square,
                items_map,
                skills_map,
                raw_class_board.mstClassBoardCommandSpell,
                raw_class_board.mstClassBoardLock,
                lang,
            )
            for square in raw_class_board.mstClassBoardSquare
        ],
        lines=[
            get_nice_class_board_line(line)
            for line in raw_class_board.mstClassBoardLine
        ],
    )


async def get_all_nice_class_boards(
    conn: AsyncConnection,
    region: Region,
    mstClassBoardBases: list[MstClassBoardBase],
    lang: Language,
) -> list[NiceClassBoard]:  # pragma: no cover
    return [
        await get_nice_class_board(conn, region, mstClassBoard.id, lang)
        for mstClassBoard in mstClassBoardBases
    ]
