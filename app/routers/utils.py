from typing import Sequence, Union

from fastapi.responses import Response
from pydantic import BaseModel

from ..data.schemas.base import BaseModelORJson


JSON_MIME = "application/json"


def item_response(item: BaseModel) -> Response:
    return Response(item.json(exclude_unset=True), media_type=JSON_MIME)


def list_response(items: Sequence[Union[BaseModel, BaseModelORJson]]) -> Response:
    return Response(
        "[" + ",".join([item.json(exclude_unset=True) for item in items]) + "]",
        media_type=JSON_MIME,
    )
