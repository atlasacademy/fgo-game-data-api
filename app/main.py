import inspect
import logging
import time

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

from .config import Settings
from .routers import nice, raw


logger = logging.getLogger()
settings = Settings()


app_description = """Provide raw and processed FGO game data.

Available documentation styles: [Swagger UI](/docs), [Redoc](/redoc).

If you encounter bugs or missing data, you can report them at the [Atlas Academy Discord](https://discord.gg/TKJmuCR).

Nice data for damage calculation:
[Attribute Affinity](/export/JP/NiceAttributeRelation.json),
[Class Attack Rate](/export/JP/NiceClassAttackRate.json),
[Class Affinity](/export/JP/NiceClassRelation.json),
[Card Details](/export/JP/NiceCard.json),
[Constants](/export/JP/NiceConstant.json),
[Buff Action info](/export/JP/NiceBuffList.ActionList.json),
[Master Level info](/export/JP/NiceUserLevel.json).
Change `JP` to `NA` in the URL if you are looking for NA constants.
"""
export_links = """

Preprocessed nice data:
[NA servant](/export/NA/nice_servant.json),
[NA CE](/export/NA/nice_equip.json),
[NA MC](/export/NA/nice_mystic_code.json),
[JP servant](/export/JP/nice_servant.json),
[JP CE](/export/JP/nice_equip.json),
[JP MC](/export/JP/nice_mystic_code.json).
"""

if settings.documentation_all_nice:
    app_description += export_links


app = FastAPI(
    title="FGO Game data API",
    description=app_description,
    version="0.3.0",
    docs_url=None,
)


app.add_middleware(CORSMiddleware, allow_origins=["*"])


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = int((time.time() - start_time) * 1000)
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Processed in {process_time}ms.")
    return response


app.include_router(
    nice.router, prefix="/nice", tags=["nice"],
)


app.include_router(
    raw.router, prefix="/raw", tags=["raw"],
)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/docs")


app.mount("/export", StaticFiles(directory="export"), name="export")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["tags"] = [
        {"name": "nice", "description": "Nicely bundled data"},
        {"name": "raw", "description": "Raw game data"},
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore


def get_swagger_ui_html(
    *,
    openapi_url: str,
    title: str,
    swagger_js_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js",
    swagger_css_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css",
) -> HTMLResponse:

    html = f"""
    <!DOCTYPE html>
    <meta charset="utf-8" />
    <title>{title}</title>
    <link type="text/css" rel="stylesheet" href="{swagger_css_url}">
    <div id="swagger-ui"></div>
    <script src="{swagger_js_url}"></script>
    <script>
    async function main() {{
        let spec = await fetch("{openapi_url}").then((resp) => resp.json());
        SwaggerUIBundle({{
            spec: spec,
            dom_id: '#swagger-ui',
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.SwaggerUIStandalonePreset
            ],
            layout: "BaseLayout",
            deepLinking: true
        }})
    }}
    main();
    </script>"""
    return HTMLResponse(inspect.cleandoc(html))


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(openapi_url=str(app.openapi_url), title=app.title)
