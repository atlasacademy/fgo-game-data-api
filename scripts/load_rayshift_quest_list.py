import argparse
import time

import httpx

from app.db.load import (
    get_all_missing_query_ids,
    get_missing_query_ids,
    load_rayshift_quest_details,
    load_rayshift_quest_list,
)
from app.rayshift.quest import get_all_quest_lists, get_multiple_quests
from app.schemas.common import Region


def main(
    quest_ids: list[int],
    load_all: bool = False,
    no_load: bool = False,
    selected_region: str | None = None,
) -> None:
    client = httpx.Client(follow_redirects=True, timeout=60)
    for region in [Region.NA, Region.JP]:
        if selected_region and region != selected_region:
            continue
        print(f"Loading {region} rayshift data cache …")
        start_loading_time = time.perf_counter()

        try:
            quest_list = get_all_quest_lists(client, region)
        except httpx.TimeoutException:
            print("TimeoutException: Failed to get quest list")
            return

        if not quest_list:
            print(f"No quest list found for {region}")
            continue

        print(f"Inserting {region} rayshift data cache into db …")
        load_rayshift_quest_list(region, quest_list)

        if no_load:
            continue

        if load_all:
            query_ids = get_all_missing_query_ids(region, quest_ids)
        else:
            query_ids = get_missing_query_ids(region, quest_ids)
        print(f"Loading {len(query_ids)} query IDs")

        if query_ids:
            QUERY_IDS_PER_REQUEST = 25
            for i in range(0, len(query_ids), QUERY_IDS_PER_REQUEST):
                request_query_ids = query_ids[i : i + QUERY_IDS_PER_REQUEST]
                quest_details = get_multiple_quests(client, region, request_query_ids)
                if quest_details:
                    load_rayshift_quest_details(region, quest_details)
                    print(
                        f"Loaded {min(i + QUERY_IDS_PER_REQUEST, len(query_ids))} query IDs"
                    )
                else:
                    print(f"Failed to fetch query IDs: {request_query_ids}")

        rayshift_load_time = time.perf_counter() - start_loading_time
        print(f"Loaded {region} rayshift in {rayshift_load_time:.2f}s.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Load Rayshift quest data into the db."
    )
    parser.add_argument(
        "--all",
        "-a",
        help="Load all missing quest details instead of just the latest ones",
        action="store_true",
    )
    parser.add_argument(
        "--no-load", "-n", help="Don't load rayshift quest data", action="store_true"
    )
    parser.add_argument(
        "--quest-id",
        "-q",
        help="quest_id to load rayshift quest data",
        type=int,
        action="append",
        required=False,
    )
    parser.add_argument(
        "--region", "-r", help="Region", type=str, required=False, default=None
    )

    args = parser.parse_args()

    main(args.quest_id, args.all, args.no_load, args.region)
