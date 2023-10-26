from ....schemas.common import Region
from ....schemas.gameenums import (
    WAR_BOARD_STAGE_SQUARE_TYPE_NAME,
    WAR_BOARD_TREASURE_RARITY_NAME,
    WarBoardStageLayoutType,
)
from ....schemas.nice import (
    NiceWarBoard,
    NiceWarBoardStage,
    NiceWarBoardStageSquare,
    NiceWarBoardTreasure,
)
from ....schemas.raw import (
    MstWarBoard,
    MstWarBoardQuest,
    MstWarBoardStage,
    MstWarBoardStageLayout,
    MstWarBoardTreasure,
)
from ..gift import GiftData, get_nice_gifts


def get_nice_war_board_treasure(
    region: Region, wb_treasure: MstWarBoardTreasure, gift_data: GiftData
) -> NiceWarBoardTreasure:
    return NiceWarBoardTreasure(
        warBoardTreasureId=wb_treasure.id,
        rarity=WAR_BOARD_TREASURE_RARITY_NAME[wb_treasure.rarity],
        gifts=get_nice_gifts(region, wb_treasure.giftId, gift_data),
    )


def get_nice_war_board_stage_square(
    region: Region,
    wb_stage_square: MstWarBoardStageLayout,
    wb_treasures: list[MstWarBoardTreasure],
    gift_data: GiftData,
) -> NiceWarBoardStageSquare:
    return NiceWarBoardStageSquare(
        squareIndex=wb_stage_square.squareIndex,
        type=WAR_BOARD_STAGE_SQUARE_TYPE_NAME[wb_stage_square.type],
        effectId=wb_stage_square.effectId,
        treasures=[
            get_nice_war_board_treasure(region, wb_treasure, gift_data)
            for wb_treasure in wb_treasures
            if wb_stage_square.type == WarBoardStageLayoutType.TREASURE
            and wb_treasure.id == wb_stage_square.effectId
        ],
    )


def get_nice_war_board_stage(
    region: Region,
    wb_stage: MstWarBoardStage,
    wb_quests: list[MstWarBoardQuest],
    wb_stage_squares: list[MstWarBoardStageLayout],
    wb_treasures: list[MstWarBoardTreasure],
    gift_data: GiftData,
) -> NiceWarBoardStage:
    try:
        wb_quest = next(q for q in wb_quests if q.stageId == wb_stage.id)
        questId = wb_quest.questId
        questPhase = wb_quest.questPhase
    except StopIteration:
        questId = 0
        questPhase = 0
    return NiceWarBoardStage(
        warBoardStageId=wb_stage.id,
        boardMessage=wb_stage.boardMessage,
        formationCost=wb_stage.formationCost,
        questId=questId,
        questPhase=questPhase,
        squares=[
            get_nice_war_board_stage_square(
                region, wb_stage_square, wb_treasures, gift_data
            )
            for wb_stage_square in wb_stage_squares
            if wb_stage_square.stageId == wb_stage.id
        ],
    )


def get_nice_war_board(
    region: Region,
    wb: MstWarBoard,
    wb_stages: list[MstWarBoardStage],
    wb_quests: list[MstWarBoardQuest],
    wb_stage_squares: list[MstWarBoardStageLayout],
    wb_treasures: list[MstWarBoardTreasure],
    gift_data: GiftData,
) -> NiceWarBoard:
    return NiceWarBoard(
        warBoardId=wb.id,
        stages=[
            get_nice_war_board_stage(
                region, wb_stage, wb_quests, wb_stage_squares, wb_treasures, gift_data
            )
            for wb_stage in wb_stages
            if wb_stage.warBoardId == wb.id
        ],
    )
