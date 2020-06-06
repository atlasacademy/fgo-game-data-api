import logging
import time

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

from .data.models.common import Settings
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
[Buff Action info](/export/JP/NiceBuffList.ActionList.json).
Change `JP` to `NA` in the URL if you are looking for NA constants.
"""
export_links = """

Preprocessed nice data:
[NA servant](/export/NA/nice_servant.json),
[NA CE](/export/NA/nice_equip.json),
[JP servant](/export/JP/nice_servant.json),
[JP CE](/export/JP/nice_equip.json).
"""

if settings.documentation_all_nice:
    app_description += export_links


app = FastAPI(title="FGO Game data API", description=app_description, version="0.2.0")


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


@app.get(
    "/",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    response_class=Response,
    summary="Redirect to /docs",
    tags=["default"],
    response_description="307 redirect to /docs",
)
async def root():
    return RedirectResponse("/docs")


app.mount("/export", StaticFiles(directory="export"), name="export")
