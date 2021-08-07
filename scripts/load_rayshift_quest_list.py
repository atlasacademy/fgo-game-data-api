import time

from app.db.load import (
    get_missing_query_ids,
    load_rayshift_quest_details,
    load_rayshift_quest_list,
)
from app.rayshift.quest import get_all_quest_lists, get_multiple_quests
from app.schemas.common import Region


def main() -> None:
    for region in [Region.NA, Region.JP]:
        print(f"Loading {region} rayshift data cache …")
        start_loading_time = time.perf_counter()

        quest_list = get_all_quest_lists(region)

        print(f"Inserting {region} rayshift data cache into db …")
        load_rayshift_quest_list(region, quest_list)

        query_ids = get_missing_query_ids(region)
        print(f"Loading {len(query_ids)} query IDs")

        if query_ids:
            QUERY_IDS_PER_REQUEST = 25
            for i in range(0, len(query_ids), QUERY_IDS_PER_REQUEST):
                request_query_ids = query_ids[i : i + QUERY_IDS_PER_REQUEST]
                quest_details = get_multiple_quests(region, request_query_ids)
                load_rayshift_quest_details(region, quest_details)
                print(
                    f"Loaded {min(i + QUERY_IDS_PER_REQUEST, len(query_ids))} query IDs"
                )

        rayshift_load_time = time.perf_counter() - start_loading_time
        print(f"Loaded {region} rayshift in {rayshift_load_time:.2f}s.")


if __name__ == "__main__":
    main()
