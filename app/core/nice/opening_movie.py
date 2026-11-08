from sqlalchemy.ext.asyncio import AsyncConnection

from ...config import Settings
from ...schemas.common import Region
from ...schemas.gameenums import (
    OPENING_MOVIE_FLAG_NAME,
    OPENING_MOVIE_MATERIAL_POS_TYPE_NAME,
    OPENING_MOVIE_TIMING_NAME,
)
from ...schemas.nice import AssetURL, NiceOpeningMovie, NiceOpeningMovieScript
from ...schemas.raw import OpeningMovieEntity
from ..raw import get_all_opening_movie_entities, get_opening_movie_entity
from ..utils import fmt_url, get_flags
from .common_release import get_nice_common_releases

settings = Settings()


def get_nice_opening_movie(
    region: Region,
    movie_entity: OpeningMovieEntity,
) -> NiceOpeningMovie:
    movie = movie_entity.mstOpeningMovie
    raw_releases = movie_entity.mstCommonRelease
    script = movie.script
    return NiceOpeningMovie(
        id=movie.id,
        priority=movie.priority,
        name=movie.name,
        movieName=movie.movieName,
        url=fmt_url(
            AssetURL.movie,
            base_url=settings.asset_url,
            region=region,
            item_id=movie.movieName.removesuffix(".usm"),
        ),
        eventId=movie.eventId,
        materialPosType=OPENING_MOVIE_MATERIAL_POS_TYPE_NAME[movie.materialPosType],
        materialPosValue=movie.materialPosValue,
        releaseConditions=get_nice_common_releases(raw_releases, movie.commonReleaseId),
        materialReleaseConditions=get_nice_common_releases(
            raw_releases, movie.materialCommonReleaseId
        ),
        playTime=movie.moviePlayTime,
        flags=get_flags(movie.flag, OPENING_MOVIE_FLAG_NAME),
        startedAt=movie.startedAt,
        endedAt=movie.endedAt,
        script=NiceOpeningMovieScript(
            groupId=script.get("groupId"),
            timing=(
                OPENING_MOVIE_TIMING_NAME[script["timing"]]
                if "timing" in script
                else None
            ),
            warId=script.get("warId"),
            isGrand=bool(script["isGrand"]) if "isGrand" in script else None,
            grandPVparentId=script.get("grandPVparentId"),
            playedFlagId=script.get("playedFlagId"),
            afterTransitionParam=script.get("afterTransitionParam"),
        ),
    )


async def get_nice_opening_movie_from_id(
    conn: AsyncConnection, region: Region, movie_id: int
) -> NiceOpeningMovie:
    movie_entity = await get_opening_movie_entity(conn, movie_id)
    return get_nice_opening_movie(region, movie_entity)


async def get_nice_opening_movies(
    conn: AsyncConnection, region: Region
) -> list[NiceOpeningMovie]:
    movie_entities = await get_all_opening_movie_entities(conn)
    return [
        get_nice_opening_movie(region, movie_entity) for movie_entity in movie_entities
    ]
