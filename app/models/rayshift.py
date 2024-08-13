from sqlalchemy import VARCHAR, Column, Index, Integer, Table, text
from sqlalchemy.dialects.postgresql import JSONB

from .base import metadata


rayshiftQuest = Table(
    "rayshiftQuest",
    metadata,
    Column("queryId", Integer, primary_key=True),
    Column("questId", Integer, index=True),
    Column("phase", Integer, index=True),
    Column("questDetail", JSONB, nullable=True),
    Index(
        "ix_rayshiftQuest_questDetail_GIN",
        text('"questDetail" jsonb_path_ops'),
        postgresql_using="gin",
    ),
)


rayshiftQuestHash = Table(
    "rayshiftQuestHash",
    metadata,
    Column("queryId", Integer, primary_key=True),
    Column("questHash", VARCHAR(100), index=True),
)
