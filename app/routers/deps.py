from typing import Generator

from sqlalchemy.engine import Connection

from ..db.base import engines
from ..schemas.common import Region


def get_db(region: Region) -> Generator[Connection, None, None]:
    try:
        engine = engines[region]
        connection = engine.connect()
        yield connection
    finally:
        connection.close()
