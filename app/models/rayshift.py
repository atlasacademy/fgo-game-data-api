from sqlalchemy import Column, Integer, Table
from sqlalchemy.dialects.postgresql import JSONB

from .base import metadata


rayshiftQuest = Table(
    "rayshiftQuest",
    metadata,
    Column("queryId", Integer, primary_key=True),
    Column("questId", Integer, index=True),
    Column("phase", Integer, index=True),
    Column("questDetail", JSONB),
)
