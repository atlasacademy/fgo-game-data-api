from app.db.load import load_rayshift_quest_list
from app.schemas.common import Region


def main() -> None:
    for region in [Region.NA, Region.JP]:
        load_rayshift_quest_list(region)


if __name__ == "__main__":
    main()
