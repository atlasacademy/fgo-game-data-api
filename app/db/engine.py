import sqlalchemy

from ..config import Settings


settings = Settings()


engines = {
    region: sqlalchemy.create_engine(
        region_data.postgresdsn, pool_size=1, max_overflow=5, future=True
    )
    for region, region_data in settings.data.items()
}
