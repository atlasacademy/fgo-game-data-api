from typing import Generator

from sqlalchemy.engine import Connection

from ..db.base import engines
from ..schemas.common import Region


def get_db(region: Region) -> Generator[Connection, None, None]:
    connection = engines[region].connect()
    try:
        yield connection
    finally:
        connection.close()
