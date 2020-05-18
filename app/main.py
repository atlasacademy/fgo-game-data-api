import logging
import time

from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse, Response

from .routers import raw, nice

logger = logging.getLogger()


app = FastAPI(
    title="FGO Game data API",
    description="Provide raw and processed FGO game data",
    version="0.0.1",
)


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
