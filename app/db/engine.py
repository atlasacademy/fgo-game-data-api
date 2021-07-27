import sqlalchemy

from ..config import SecretSettings
from ..schemas.common import Region


secrets = SecretSettings()


engines = {
    Region.NA: sqlalchemy.create_engine(
        secrets.na_postgresdsn, pool_size=3, max_overflow=10, future=True
    ),
    Region.JP: sqlalchemy.create_engine(
        secrets.jp_postgresdsn, pool_size=3, max_overflow=10, future=True
    ),
}
