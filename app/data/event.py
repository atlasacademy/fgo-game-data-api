from collections import defaultdict
from typing import DefaultDict

from pydantic import DirectoryPath

from ..schemas.raw import MstEvent, MstWar
from .utils import load_master_data


def get_event_with_warIds(gamedata_path: DirectoryPath) -> list[MstEvent]:
    mstEvents = load_master_data(gamedata_path, MstEvent)
    mstWars = load_master_data(gamedata_path, MstWar)

    event_warIds: DefaultDict[int, list[int]] = defaultdict(list)
    for war in mstWars:
        event_warIds[war.eventId].append(war.id)

    for event in mstEvents:
        event.warIds = event_warIds.get(event.id, [])

    return mstEvents
