import sqlalchemy

from ..config import Settings
from ..schemas.common import Region


settings = Settings()


engines = {
    Region.NA: sqlalchemy.create_engine(settings.na_postgresdsn),
    Region.JP: sqlalchemy.create_engine(settings.jp_postgresdsn),
}
