import sqlalchemy

from ..config import Settings
from ..schemas.common import Region


settings = Settings()


engines = {
    Region.NA: sqlalchemy.create_engine(
        settings.na_postgresdsn, pool_size=5, max_overflow=10
    ),
    Region.JP: sqlalchemy.create_engine(
        settings.jp_postgresdsn, pool_size=5, max_overflow=10
    ),
}
