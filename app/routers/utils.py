from typing import Iterable

from fastapi.responses import Response

from ..data.schemas.base import BaseModelORJson


JSON_MIME = "application/json"


def item_response(item: BaseModelORJson) -> Response:
    return Response(item.json(exclude_unset=True), media_type=JSON_MIME)


def list_string(items: Iterable[BaseModelORJson]) -> str:
    return "[" + ",".join([item.json(exclude_unset=True) for item in items]) + "]"


def list_response(items: Iterable[BaseModelORJson]) -> Response:
    return Response(list_string(items), media_type=JSON_MIME)
