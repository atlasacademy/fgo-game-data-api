import inspect
import logging
import time

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from .config import Settings
from .data.gamedata import pull_and_update
from .routers import basic, nice, raw


logger = logging.getLogger()
settings = Settings()


app_short_description = "Provide raw and nicely bundled FGO game data."


app_more_description = """

Available documentation styles: [Swagger UI](/docs), [Redoc](/redoc).

To discuss more about the API, you can go to the [Atlas Academy Discord](https://discord.gg/TKJmuCR).
Bug reports and feature requests are welcome.
Source code of the API is available on [GitHub](https://github.com/atlasacademy/fgo-game-data-api).

Static files that can be used for damage calculation. Change `JP` to `NA` in the URL if you are looking for NA constants. Mapping of the damage formula to the API can be found [here](https://github.com/atlasacademy/fgo-game-data-docs/tree/master/battle):
- [Attribute Affinity](/export/JP/NiceAttributeRelation.json)
- [Class Attack Rate](/export/JP/NiceClassAttackRate.json)
- [Class Affinity](/export/JP/NiceClassRelation.json)
- [Card Details](/export/JP/NiceCard.json)
- [Constants](/export/JP/NiceConstant.json)
- [Buff Action info](/export/JP/NiceBuffList.ActionList.json)
- [Master Level info](/export/JP/NiceUserLevel.json)
"""
export_links = """

Pre-generated nice data that can be served instantly unlike querying the API:
- NA data:
  - [NA Servant](/export/NA/nice_servant.json)
  - [NA Craft Essence](/export/NA/nice_equip.json)
  - [NA Command Code](/export/NA/nice_command_code.json)
  - [NA Material](/export/NA/nice_item.json)
  - [NA  Mystic Code](/export/NA/nice_mystic_code.json)
- JP data:
  - [JP Servant](/export/JP/nice_servant.json)
  - [JP Craft Essence](/export/JP/nice_equip.json)
  - [JP Command Code](/export/JP/nice_command_code.json)
  - [JP Material](/export/JP/nice_item.json)
  - [JP Mystic CodeC](/export/JP/nice_mystic_code.json)
"""

app_description = app_short_description + app_more_description
if settings.documentation_all_nice:
    app_description += export_links


tags_metadata = [
    {"name": "nice", "description": "Nicely bundled data"},
    {"name": "basic", "description": "Minimal nice data for indexing"},
    {"name": "raw", "description": "Raw game data"},
]


app = FastAPI(
    title="FGO game data API",
    description=app_description,
    version="0.11.0",
    docs_url=None,
    openapi_tags=tags_metadata,
)


app.add_middleware(CORSMiddleware, allow_origins=["*"])


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = round((time.perf_counter() - start_time) * 1000, 2)
    response.headers["Server-Timing"] = f"app;dur={process_time}"
    logger.debug(f"Processed in {process_time}ms.")
    return response


app.include_router(
    nice.router, prefix="/nice", tags=["nice"],
)

app.include_router(
    basic.router, prefix="/basic", tags=["basic"],
)


app.include_router(
    raw.router, prefix="/raw", tags=["raw"],
)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/docs")


if settings.github_webhook_secret != "":  # pragma: no cover

    @app.post(f"/{settings.github_webhook_secret}/update", include_in_schema=False)
    async def update_gamedata(background_tasks: BackgroundTasks):
        background_tasks.add_task(pull_and_update)
        return {"message": "Game data is updated in the background"}


app.mount("/export", StaticFiles(directory="export"), name="export")


def get_swagger_ui_html(
    openapi_url: str,
    title: str,
    description: str,
    swagger_js_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js",
    swagger_css_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css",
) -> HTMLResponse:

    html = f"""
    <!DOCTYPE html>
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
    return HTMLResponse(inspect.cleandoc(html))


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=str(app.openapi_url),
        title=app.title,
        description=app_short_description,
    )
