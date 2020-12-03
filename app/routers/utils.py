import json
from typing import Any, Iterable, Set

from fastapi.responses import Response

from ..data.schemas.base import BaseModelORJson


JSON_MIME = "application/json"


def item_response(item: BaseModelORJson) -> Response:
    """
    Convert input model object to a Starlette Response object.
    Use this method to skip the second validation done by fastapi's json_encodable
    if the input model and the specificed response_model are the same.
    """
    return Response(
        item.json(exclude_unset=True, exclude_none=True), media_type=JSON_MIME
    )


def list_string(items: Iterable[BaseModelORJson]) -> str:
    """
    Convert list of model objects to a json formatted string.
    """
    return (
        "["
        + ",".join([item.json(exclude_unset=True, exclude_none=True) for item in items])
        + "]"
    )


def list_string_exclude(items: Iterable[BaseModelORJson], exclude: Set[str]) -> str:
    """
    Convert input list of model objects to a json formatted string.
    Attributes given to exclude will be excluded from the output json string.
    """
    all_items = ",".join(
        [
            item.json(exclude_unset=True, exclude_none=True, exclude=exclude)
            for item in items
        ]
    )
    return "[" + all_items + "]"


def list_response(items: Iterable[BaseModelORJson]) -> Response:
    """
    Convert list of model objects to a Starlette Response object.
    Use this method to skip the second validation done by fastapi's json_encodable
    if the input model and the specificed response_model are the same.
    """
    return Response(list_string(items), media_type=JSON_MIME)


def pretty_print_response(data: Any) -> Response:
    """
    Convert data to a Starlette Response object with pretty printed json data.
    """
    return Response(
        json.dumps(data, indent=2, ensure_ascii=False), media_type=JSON_MIME
    )
