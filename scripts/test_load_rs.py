import time

import httpx

from app.rayshift.quest import get_all_quest_lists, get_multiple_quests
from app.schemas.common import Region


def main() -> None:
    client = httpx.Client(follow_redirects=True, timeout=60)
    query_ids = [
        6462844,
        6461990,
        6468547,
        6466997,
        6468543,
        6466995,
        6468541,
        6466992,
        6467559,
        6468539,
        6466990,
        6468647,
        6468318,
        6468536,
        6466988,
        6460866,
        6468534,
        6466986,
        6467251,
        6468529,
        6466982,
        6468525,
        6466981,
        6468522,
        6466979,
    ]
    quest_details = get_multiple_quests(client, Region.NA, query_ids)
    print(quest_details)


if __name__ == "__main__":
    main()
