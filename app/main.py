import logging
import time

from fastapi import FastAPI, Request

from .routers import raw

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
    raw.router, prefix="/raw", tags=["raw"],
)
