from enum import IntEnum


class SvtType(IntEnum):
    NORMAL = 1
    HEROINE = 2
    COMBINE_MATERIAL = 3
    ENEMY = 4
    ENEMY_COLLECTION = 5
    SERVANT_EQUIP = 6
    STATUS_UP = 7
    SVT_EQUIP_MATERIAL = 8
    ENEMY_COLLECTION_DETAIL = 9
    ALL = 10
    COMMAND_CODE = 11


def is_servant(svt_type: int) -> bool:
    return svt_type in [
        SvtType.NORMAL,
        SvtType.HEROINE,
    ]


def is_equip(svt_type: int) -> bool:
    return svt_type == SvtType.SERVANT_EQUIP
