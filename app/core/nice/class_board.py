from sqlalchemy.ext.asyncio import AsyncConnection

from ...config import Settings
from ...schemas.common import Language, Region
from ...schemas.enums import CLASS_NAME, SvtClass
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
    NiceSkill,
)
from ...schemas.raw import (
    MstClassBoardBase,
    MstClassBoardClass,
    MstClassBoardLine,
    MstClassBoardLock,
    MstClassBoardSquare,
    MstItem,
    SkillEntityNoReverse,
)
from .. import raw
from ..utils import fmt_url, get_flags
from .item import get_nice_item_amount, get_nice_item_from_raw
from .skill import get_nice_skill_from_raw


settings = Settings()


def get_nice_class_board_class(
    class_board_class: MstClassBoardClass,
) -> NiceClassBoardClass:
    SvtClass.atlasUnmappedClass
    return NiceClassBoardClass(
        classId=class_board_class.classId,
        className=CLASS_NAME.get(
            class_board_class.classId, SvtClass.atlasUnmappedClass
        ),
        condType=COND_TYPE_NAME[class_board_class.condType],
        condTargetId=class_board_class.condTargetId,
        condNum=class_board_class.condNum,
    )


# TODO
# def get_nice_class_board_command_spell()->NiceClassBoardCommandSpell:
#     return NiceClassBoardCommandSpell(
#     )


def get_nice_class_board_lock(
    region: Region,
    lock: MstClassBoardLock,
    items_map: dict[int, MstItem],
    lang: Language,
) -> NiceClassBoardLock:
    return NiceClassBoardLock(
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
    lang: Language,
) -> NiceClassBoardSquare:

    if square.skillType == ClassBoardSkillType.PASSIVE:
        skill = await get_nice_skill_from_raw(
            conn, region, skills_map[square.targetId], NiceSkill, lang
        )
    else:
        skill = None

    return NiceClassBoardSquare(
        id=square.id,
        icon=None,
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
        targetCommandSpell=None,
        lock=None,
        flags=get_flags(square.flag, CLASS_BOARD_SQUARE_FLAG_NAME),
        priority=square.flag,
    )


def get_nice_class_board_line(line: MstClassBoardLine) -> NiceClassBoardLine:
    return NiceClassBoardLine(
        id=line.id,
        prevSquareId=line.id,
        nextSquareId=line.id,
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
        icon=None,
        dispItems=[
            get_nice_item_from_raw(region, items_map[itemId], lang)
            for itemId in mstClassBoardBase.dispItemIds
            if itemId in items_map
        ],
        closedMessage=mstClassBoardBase.closedMessage,
        condType=COND_TYPE_NAME[mstClassBoardBase.condType],
        condTargetId=mstClassBoardBase.condTargetId,
        condNum=mstClassBoardBase.condNum,
        classes=[
            get_nice_class_board_class(class_board_class)
            for class_board_class in raw_class_board.mstClassBoardClass
        ],
        squares=[
            await get_nice_class_board_square(
                conn, region, square, items_map, skills_map, lang
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
