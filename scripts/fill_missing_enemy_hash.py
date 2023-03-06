from app.db.engine import engines
from app.db.helpers.rayshift import (
    fetch_missing_enemy_hash,
    insert_rayshift_quest_hash_db_sync,
)
from app.schemas.common import Region


def main() -> None:
    for region in [Region.NA, Region.JP]:
        engine = engines[region]
        count = 0
        while True:
            with engine.connect() as conn:
                details_missing_hash = fetch_missing_enemy_hash(conn)

            if not details_missing_hash:
                break

            with engine.begin() as conn:
                insert_rayshift_quest_hash_db_sync(conn, details_missing_hash)

            count += len(details_missing_hash)
            print(f"Inserted {count} {region} enemy hashes")


if __name__ == "__main__":
    main()
