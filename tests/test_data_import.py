from app.data.event import get_event_with_warIds
from app.data.item import get_item_with_use

from .utils import test_gamedata


def test_append_warIds_to_event() -> None:
    eventWar = get_event_with_warIds(test_gamedata)
    oniland = next(event for event in eventWar.mstEvents if event.id == 80119)
    assert oniland.warIds == [9050]


def test_append_use_to_item() -> None:
    mstItems = get_item_with_use(test_gamedata)

    claw = next(item for item in mstItems if item.id == 6507)
    assert claw.useSkill is True
    assert claw.useAscension is True
    assert claw.useCostume is False

    feather = next(item for item in mstItems if item.id == 6501)
    assert feather.useSkill is False
    assert feather.useAscension is False
    assert feather.useCostume is True
