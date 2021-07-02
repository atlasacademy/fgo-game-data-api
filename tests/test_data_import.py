from app.data.event import get_event_with_warIds

from .utils import test_gamedata


def test_append_warIds_to_event() -> None:
    mstEvents = get_event_with_warIds(test_gamedata)
    oniland = next(event for event in mstEvents if event.id == 80119)
    assert oniland.warIds == [9050]
