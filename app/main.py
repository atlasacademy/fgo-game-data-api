import hashlib
import json
import pickle
import time
import tomllib
from math import ceil
from typing import Any, Awaitable, Callable, Optional

import orjson
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi_cache import Coder, FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis.asyncio import Redis as AsyncRedis
from sqlalchemy.ext.asyncio import AsyncConnection

from .config import Settings, get_app_info, logger, project_root
from .core.info import get_all_repo_info
from .db.engine import async_engines, engines
from .redis import Redis
from .routers import basic, nice, raw, secret
from .routers.deps import get_redis
from .schemas.common import Region, RepoInfo
from .zstd import zstd_compress, zstd_decompress


settings = Settings()


app_short_description = "Provide raw and nicely bundled FGO game data."


app_more_description = """

### API Usage

It's recommended to use the static export files or search with the `/basic` endpoints
and fetch nice or raw data as needed.
A big search with nice or raw data will take a while to respond.

There are many export files in the "Export files" section above.
Make sure you check them out before querying the API.
Chances are what you need is already there.
Feel free to contact me if you would like to see an export file that is not currently available.

### Miscellaneous info

The current data version can be found [here](/info).

API's changelog can be found [here](https://github.com/atlasacademy/fgo-game-data-api/blob/master/CHANGELOG.md).

To discuss more about the API, you can go to the [Atlas Academy Discord](https://discord.gg/TKJmuCR).
Bug reports and feature requests are welcome.
Source code of the API is available on [GitHub](https://github.com/atlasacademy/fgo-game-data-api).

Available documentation styles: [RapiDoc](/rapidoc), [Swagger UI](/docs), [Redoc](/redoc).

### Static Constants

Here are the static files that can be used for damage calculation.
Change `JP` to `NA` in the URL if you are looking for NA constants.
Mapping of the damage formula to the API can be found
[here](https://github.com/atlasacademy/fgo-game-data-docs/tree/master/battle):
- [Attribute Affinity](/export/JP/NiceAttributeRelation.json)
- [Class Attack Rate](/export/JP/NiceClassAttackRate.json)
- [Class Affinity](/export/JP/NiceClassRelation.json)
- [Card Details](/export/JP/NiceCard.json)
- [Constants](/export/JP/NiceConstant.json)
- [Buff Action info](/export/JP/NiceBuffList.ActionList.json)
- [Master Level info](/export/JP/NiceUserLevel.json)
- [Palingenesis QP cost](/export/JP/NiceSvtGrailCost.json)
"""
export_links = """

### Static export files

#### Full data export files

Pre-generated full nice data that can be served instantly:
- NA data:
  - [NA Servant](/export/NA/nice_servant.json)
  - [NA Servant with lore](/export/NA/nice_servant_lore.json)
  - [NA Craft Essence](/export/NA/nice_equip.json)
  - [NA Craft Essence with lore](/export/NA/nice_equip_lore.json)
  - [NA War](/export/NA/nice_war.json)
  - [NA Event](/export/NA/nice_event.json)
  - [NA Command Code](/export/NA/nice_command_code.json)
  - [NA Material](/export/NA/nice_item.json)
  - [NA Mystic Code](/export/NA/nice_mystic_code.json)
  - [NA Item](/export/NA/nice_item.json)
  - [NA Master Mission](/export/NA/nice_master_mission.json)
  - [NA Illustrator](/export/NA/nice_illustrator.json)
  - [NA Voice Actor](/export/NA/nice_cv.json)
  - [NA BGM](/export/NA/nice_bgm.json)
  - [NA Asset Storage](/export/NA/asset_storage.json)
- JP data:
  - [JP Servant](/export/JP/nice_servant.json),
  [JP Servant with English names](/export/JP/nice_servant_lang_en.json)
  - [JP Servant with lore](/export/JP/nice_servant_lore.json),
  [JP Servant with English names and lore](/export/JP/nice_servant_lore_lang_en.json)
  - [JP Craft Essence](/export/JP/nice_equip.json),
  [JP Craft Essence with English names](/export/JP/nice_equip_lang_en.json)
  - [JP Craft Essence with lore](/export/JP/nice_equip_lore.json),
  [JP Craft Essence with lore and English names](/export/JP/nice_equip_lore_lang_en.json)
  - [JP War](/export/JP/nice_war.json),
  [JP War with English names](/export/JP/nice_war_lang_en.json)
  - [JP Event](/export/JP/nice_event.json),
  [JP Event with English names](/export/JP/nice_event_lang_en.json)
  - [JP Command Code](/export/JP/nice_command_code.json),
  [JP Command Code with English names](/export/JP/nice_command_code_lang_en.json)
  - [JP Mystic Code](/export/JP/nice_mystic_code.json),
  [JP Mystic Code with English names](/export/JP/nice_mystic_code_lang_en.json)
  - [JP Material](/export/JP/nice_item.json),
  [JP Material with English names](/export/JP/nice_item_lang_en.json)
  - [JP Master Mission](/export/JP/nice_master_mission.json)
  - [JP Illustrator](/export/JP/nice_illustrator.json)
  [JP Illustrator with English names](/export/JP/nice_illustrator_lang_en.json)
  - [JP Voice Actor](/export/JP/nice_cv.json)
  [JP Voice Actor with English names](/export/JP/nice_cv_lang_en.json)
  - [JP BGM](/export/JP/nice_bgm.json),
  [JP BGM](/export/JP/nice_bgm_lang_en.json)
  - [JP Asset Storage](/export/JP/asset_storage.json)
- Both regions (The data is the same for both NA and JP endpoints):
  - [All enums](/export/JP/nice_enums.json)
  - [Trait mapping](/export/JP/nice_trait.json)

#### Trimmed-down data export files

Pre-generated, trimmed-down, lightweight basic data that can be used for indexing purposes:
- NA data:
  - [NA servant](/export/NA/basic_servant.json)
  - [NA CE](/export/NA/basic_equip.json)
  - [NA svt](/export/NA/basic_svt.json)
  - [NA Command Code](/export/NA/basic_command_code.json)
  - [NA Mystic Code](/export/NA/basic_mystic_code.json)
  - [NA War](/export/NA/basic_war.json)
  - [NA Event](/export/NA/basic_event.json)
- JP data:
  - [JP servant](/export/JP/basic_servant.json),
  [JP servant with English names](/export/JP/basic_servant_lang_en.json)
  - [JP CE](/export/JP/basic_equip.json),
  [JP CE with English names](/export/JP/basic_equip_lang_en.json)
  - [JP svt](/export/JP/basic_svt.json),
  [JP svt with English names](/export/JP/basic_svt_lang_en.json)
  - [JP Command Code](/export/JP/basic_command_code.json),
  [JP Command Code with English names](/export/JP/basic_command_code_lang_en.json)
  - [JP Mystic Code](/export/JP/basic_mystic_code.json),
  [JP Mystic Code with English names](/export/JP/basic_mystic_code_lang_en.json)
  - [JP War](/export/JP/basic_war.json),
  [JP War with English names](/export/JP/basic_war_lang_en.json)
  - [JP Event](/export/JP/basic_event.json),
  [JP Event with English name](/export/JP/basic_event_lang_en.json)
"""

if settings.documentation_all_nice:  # pragma: no cover
    app_description = app_short_description + export_links + app_more_description
else:  # pragma: no cover
    app_description = app_short_description + app_more_description


tags_metadata = [
    {"name": "nice", "description": "Nicely human-readable bundled data."},
    {"name": "basic", "description": "Minimal nice data for indexing"},
    {"name": "raw", "description": "Raw game data."},
]


with open(project_root / "pyproject.toml", "rb") as f:
    pyproject_toml = tomllib.load(f)


app = FastAPI(
    title="FGO game data API",
    description=app_description,
    version=pyproject_toml["tool"]["poetry"]["version"],
    docs_url=None,
    openapi_tags=tags_metadata,
)


if settings.openapi_url:
    app.servers = [{"url": settings.openapi_url}]


app.add_middleware(CORSMiddleware, allow_origins=["*"])


@app.middleware("http")
async def add_process_time_header(
    request: Request, call_next: Callable[..., Awaitable[Response]]
) -> Response:
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = round((time.perf_counter() - start_time) * 1000, 2)
    response.headers["Server-Timing"] = f"app;dur={process_time}"
    logger.debug(f"Processed in {process_time}ms.")
    return response


async def limiter_callback(
    request: Request,
    response: Response,  # noqa: ARG001
    pexpire: int,
) -> None:  # pragma: no cover
    expire = ceil(pexpire / 1000)
    homepage = request.url.netloc

    raise HTTPException(
        status.HTTP_429_TOO_MANY_REQUESTS,
        f"Too Many Requests. Please check the documentation at {homepage} for the export files."
        " The export files might contain what you need so you don't need to call many small requests."
        " Retry after {expire} seconds.",
        headers={"Retry-After": str(expire)},
    )


def get_region(args: list[Any], kwargs: dict[str, Any]) -> str:  # pragma: no cover
    if "region" in kwargs and isinstance(kwargs["region"], Region):
        return kwargs["region"].value
    elif "search_param" in kwargs:
        search_param = kwargs["search_param"]
        if hasattr(search_param, "region") and isinstance(search_param.region, Region):
            return search_param.region.value
    else:
        for arg in args:
            if isinstance(arg, Region):
                return arg.value
            if hasattr(arg, "region") and isinstance(arg.region, Region):
                return arg.region.value

    return ""


def custom_key_builder(
    __function: Callable[..., Any],
    __namespace: str = "",
    *,
    request: Optional[Request] = None,  # noqa: ARG001
    response: Optional[Response] = None,  # noqa: ARG001
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str:
    prefix = FastAPICache.get_prefix()
    static_kwargs = {k: v for k, v in kwargs.items() if k not in {"conn", "redis"}}

    static_args = [
        arg
        for arg in args
        if not isinstance(arg, AsyncConnection) and not isinstance(arg, AsyncRedis)
    ]

    region = get_region(static_args, static_kwargs)

    try:
        args_dump = orjson.dumps(static_args)
        kwargs_dump = orjson.dumps(static_kwargs)
    except TypeError:  # orjson can't dump 64+ bit int
        args_dump = json.dumps(static_args).encode("utf-8")
        kwargs_dump = json.dumps(static_kwargs).encode("utf-8")

    raw_key = (
        f"{__function.__module__}:{__function.__name__}:".encode("utf-8")
        + args_dump
        + b":"
        + kwargs_dump
    )
    cache_key = hashlib.sha1(raw_key).hexdigest()

    return f"{prefix}:{region}:{__namespace}:{cache_key}"


class PickleCoder(Coder):  # pragma: no cover
    @classmethod
    def encode(cls, value: Any) -> bytes:
        picked = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        return zstd_compress(picked)

    @classmethod
    def decode(cls, value: bytes) -> Any:
        return pickle.loads(zstd_decompress(value))


@app.on_event("startup")
async def startup() -> None:
    redis = await Redis.from_url(str(settings.redisdsn))
    FastAPICache.init(
        RedisBackend(redis),
        prefix=f"{settings.redis_prefix}:cache",
        expire=60 * 60 * 24 * 7,
        key_builder=custom_key_builder,
        coder=PickleCoder,
    )
    app.state.redis = redis


@app.on_event("shutdown")
async def shutdown() -> None:
    for engine in engines.values():
        engine.dispose()
    for async_engine in async_engines.values():
        await async_engine.dispose()


app.include_router(nice.router)

app.include_router(basic.router)

app.include_router(raw.router)


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse("/docs")


@app.get("/info", summary="Data version info", response_model=dict[Region, RepoInfo])
async def main_info(redis: Redis = Depends(get_redis)) -> dict[Region, RepoInfo]:
    return await get_all_repo_info(redis, settings.data.keys())


if settings.github_webhook_secret.get_secret_value() != "":  # pragma: no cover
    app.include_router(secret.router)


app.mount("/export", StaticFiles(directory="export"), name="export")


def custom_openapi() -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        terms_of_service=app.terms_of_service,
        contact=app.contact,
        license_info=app.license_info,
        routes=app.routes,
        tags=app.openapi_tags,
        servers=app.servers,
    )
    app_info = get_app_info()
    openapi_schema["info"]["x-server-commit-hash"] = app_info.hash
    openapi_schema["info"]["x-server-commit-timestamp"] = app_info.timestamp
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore


def get_swagger_ui_html(
    openapi_url: str,
    title: str,
    description: str,
    swagger_js_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui-bundle.js",
    swagger_css_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui.css",
) -> HTMLResponse:
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <link rel="stylesheet" href="{swagger_css_url}">
    <div id="swagger-ui">Loading ...</div>
    <script src="{swagger_js_url}"></script>
    <script>
    async function main() {{
        let spec = await fetch("{openapi_url}").then((resp) => resp.json());
        SwaggerUIBundle({{
            spec: spec,
            dom_id: "#swagger-ui",
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.SwaggerUIStandalonePreset,
            ],
            deepLinking: true,
            defaultModelsExpandDepth: 0,
            showExtensions: true,
            showCommonExtensions: true,
        }})
    }}
    main();
    </script>"""
    return HTMLResponse(html)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url=str(app.openapi_url),
        title=app.title,
        description=app_short_description,
    )


def get_rapidoc_html(
    openapi_url: str,
    title: str,
    description: str,
    rapidoc_js_url: str = "https://cdn.jsdelivr.net/npm/rapidoc/dist/rapidoc-min.js",
) -> HTMLResponse:
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <script src="{rapidoc_js_url}"></script>
    <rapi-doc
        spec-url="{openapi_url}"
        sort-endpoints-by=method
        render-style=view
        theme=dark
        load-fonts=false
        regular-font='"Fira Sans", Avenir, "Segoe UI", Arial, sans-serif'
        schema-expand-level=1
        schema-description-expanded=true
    ></rapi-doc>"""
    return HTMLResponse(html)


@app.get("/rapidoc", include_in_schema=False)
async def rapidoc_html() -> HTMLResponse:
    return get_rapidoc_html(
        openapi_url=str(app.openapi_url),
        title=app.title,
        description=app_short_description,
    )


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(
        "app.main:app", host="127.0.0.1", port=8000, reload=True, log_level="debug"
    )
