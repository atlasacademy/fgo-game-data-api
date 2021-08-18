import logging
import time
from typing import Awaitable, Callable

import aioredis
import toml
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import create_async_engine

from .config import SecretSettings, Settings, logger, project_root
from .routers import basic, nice, raw, secret
from .schemas.common import Region, RepoInfo
from .tasks import REGION_PATHS, load_and_export, repo_info


settings = Settings()
secrets = SecretSettings()


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
  - [NA Command Code](/export/NA/nice_command_code.json)
  - [NA Material](/export/NA/nice_item.json)
  - [NA Mystic Code](/export/NA/nice_mystic_code.json)
  - [NA Item](/export/NA/nice_item.json)
  - [NA Master Mission](/export/NA/nice_master_mission.json)
  - [NA Illustrator](/export/NA/nice_illustrator.json)
  - [NA Voice Actor](/export/NA/nice_cv.json)
  - [NA BGM](/export/NA/nice_bgm.json)
- JP data:
  - [JP Servant](/export/JP/nice_servant.json),
  [JP Servant with English names](/export/JP/nice_servant_lang_en.json)
  - [JP Servant with lore](/export/JP/nice_servant_lore.json),
  [JP Servant with English names and lore](/export/JP/nice_servant_lore_lang_en.json)
  - [JP Craft Essence](/export/JP/nice_equip.json),
  [JP Craft Essence with English names](/export/JP/nice_equip_lang_en.json)
  - [JP Craft Essence with lore](/export/JP/nice_equip_lore.json),
  [JP Craft Essence with lore and English names](/export/JP/nice_equip_lore_lang_en.json)
  - [JP Command Code](/export/JP/nice_command_code.json),
  [JP Command Code with English names](/export/JP/nice_command_code_lang_en.json)
  - [JP Mystic Code](/export/JP/nice_mystic_code.json),
  [JP Mystic Code with English names](/export/JP/nice_mystic_code_lang_en.json)
  - [JP Material](/export/JP/nice_item.json),
  [JP Material with English names](/export/JP/nice_item_lang_en.json)
  - [JP Master Mission](/export/JP/nice_master_mission.json)
  - [JP Illustrator](/export/JP/nice_illustrator.json)
  - [JP Voice Actor](/export/JP/nice_cv.json)
  - [JP BGM](/export/JP/nice_bgm.json),
  [JP BGM](/export/JP/nice_bgm_lang_en.json)
- Both regions (The data is the same for both NA and JP endpoints):
  - [All enums](/export/JP/nice_enums.json)
  - [Trait mapping](/export/JP/nice_trait.json)

#### Trimmed-down data export files

Pre-generated, trimmed-down, lightweight basic data that can be used for indexing purposes:
- NA data:
  - [NA servant](/export/NA/basic_servant.json)
  - [NA CE](/export/NA/basic_equip.json)
  - [NA Command Code](/export/NA/basic_command_code.json)
  - [NA Mystic Code](/export/NA/basic_mystic_code.json)
  - [NA War](/export/NA/basic_war.json)
  - [NA Event](/export/NA/basic_event.json)
- JP data:
  - [JP servant](/export/JP/basic_servant.json),
  [JP servant with English names](/export/JP/basic_servant_lang_en.json)
  - [JP CE](/export/JP/basic_equip.json),
  [JP CE with English names](/export/JP/basic_equip_lang_en.json)
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
    {"name": "nice", "description": "Nicely bundled data"},
    {"name": "basic", "description": "Minimal nice data for indexing"},
    {"name": "raw", "description": "Raw game data"},
]


pyproject_toml = toml.load(project_root / "pyproject.toml")


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
    response.headers["Bloom-Response-Buckets"] = "fgo-game-data-api"
    if response.status_code != 200:
        response.headers["Bloom-Response-Ignore"] = "1"
    process_time = round((time.perf_counter() - start_time) * 1000, 2)
    response.headers["Server-Timing"] = f"app;dur={process_time}"
    logger.debug(f"Processed in {process_time}ms.")
    return response


@app.on_event("startup")
async def startup() -> None:
    redis = await aioredis.create_redis_pool(secrets.redisdsn)
    app.state.redis = redis
    async_engines = {
        Region.NA: create_async_engine(
            secrets.na_postgresdsn.replace("postgresql", "postgresql+asyncpg"),
            echo=logger.isEnabledFor(logging.DEBUG),
        ),
        Region.JP: create_async_engine(
            secrets.jp_postgresdsn.replace("postgresql", "postgresql+asyncpg"),
            echo=logger.isEnabledFor(logging.DEBUG),
        ),
    }
    app.state.async_engines = async_engines
    await load_and_export(redis, REGION_PATHS, async_engines)


@app.on_event("shutdown")
async def shutdown() -> None:
    app.state.redis.close()
    await app.state.redis.wait_closed()
    for engine in app.state.async_engines.values():
        await engine.dispose()


app.include_router(nice.router)

app.include_router(basic.router)

app.include_router(raw.router)


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse("/rapidoc")


@app.get("/info", summary="Data version info", response_model=dict[Region, RepoInfo])
async def main_info(response: Response) -> dict[Region, RepoInfo]:
    response.headers["Bloom-Response-Ignore"] = "1"
    return repo_info


if secrets.github_webhook_secret.get_secret_value() != "":  # pragma: no cover
    app.include_router(secret.router)


app.mount("/export", StaticFiles(directory="export"), name="export")


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
