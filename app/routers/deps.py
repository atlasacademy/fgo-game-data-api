from typing import Generator

from sqlalchemy.engine import Connection

from ..db.engine import engines
from ..schemas.common import Region


def get_db(region: Region) -> Generator[Connection, None, None]:
    with engines[region].connect() as connection:
        yield connection
