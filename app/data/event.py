from collections import defaultdict
from dataclasses import dataclass
from typing import DefaultDict

from pydantic import DirectoryPath

from ..schemas.raw import MstEvent, MstWar
from .utils import load_master_data


@dataclass
class EventWar:
    mstEvents: list[MstEvent]
    mstWars: list[MstWar]


def get_event_with_warIds(gamedata_path: DirectoryPath) -> EventWar:
    mstEvents = load_master_data(gamedata_path, MstEvent)
    mstWars = load_master_data(gamedata_path, MstWar)

    event_names = {event.id: event.name for event in mstEvents if event.name != ""}

    event_warIds: DefaultDict[int, list[int]] = defaultdict(list)
    for war in mstWars:
        event_warIds[war.eventId].append(war.id)
        war.eventName = event_names.get(war.eventId, "")

    for event in mstEvents:
        event.warIds = event_warIds.get(event.id, [])

    return EventWar(mstEvents, mstWars)
