import inspect
import logging
import os
import sys
from typing import Callable

import httpx
import loguru
from gunicorn import glogging
from loguru import logger
from pydantic import HttpUrl
from uvicorn.logging import TRACE_LOG_LEVEL


# https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def build_webhook_sink(url: HttpUrl) -> Callable[["loguru.Message"], None]:
    def sink(message: "loguru.Message") -> None:
        payload = {
            "username": "API",
            "content": f"```\n{str(message).strip()}\n```",
        }

        # There are some issues with gunicorn and loguru async sinks + enqueue so we use a sync client here
        # An event loop is required to add a coroutine sink with `enqueue=True`
        # We can move init loggin inside app start event to avoid this
        # but we want loguru to be configured as early as possible when running under uvicorn
        with httpx.Client(timeout=5.0) as client:
            client.post(str(url), json=payload)

    return sink


def init_logging(error_webhooks: list[HttpUrl]) -> None:
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    intercept_handler = InterceptHandler()

    for logger_name in logging.root.manager.loggerDict:
        if logger_name.startswith("uvicorn"):
            corn_logger = logging.getLogger(logger_name)
            if corn_logger.handlers:
                corn_logger.handlers = [intercept_handler]

    if uvicorn_access_logger.isEnabledFor(TRACE_LOG_LEVEL):
        sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
        sqlalchemy_logger.setLevel(logging.INFO)
        sqlalchemy_logger.handlers = [intercept_handler]

    logger.configure(
        handlers=[{"sink": sys.stdout, "level": uvicorn_access_logger.level}],
    )

    for url in error_webhooks:
        webhook_sink = build_webhook_sink(url)
        logger.add(webhook_sink, level=logging.ERROR)

    running_under_gunicorn = "gunicorn" in os.environ.get("SERVER_SOFTWARE", "")
    if running_under_gunicorn:
        uvicorn_access_logger.handlers = []


class GunicornLogger(glogging.Logger):
    def __init__(self, cfg):
        super().__init__(cfg)
        logging.getLogger("gunicorn.error").handlers = [InterceptHandler()]
        logging.getLogger("gunicorn.access").handlers = [InterceptHandler()]
