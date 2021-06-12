from app.db.load import load_rayshift_quest_list
from app.rayshift.quest import get_all_quest_lists
from app.schemas.common import Region


def main() -> None:
    for region in [Region.NA, Region.JP]:
        quest_list = get_all_quest_lists(region)
        load_rayshift_quest_list(region, quest_list)


if __name__ == "__main__":
    main()
