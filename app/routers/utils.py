from typing import Any, Iterable, Mapping, Type, Union

import orjson
from fastapi.responses import Response
from pydantic import BaseModel

from ..schemas.base import BaseModelORJson


JSON_MIME = "application/json; charset=utf-8"


class DetailMessage(BaseModel):
    detail: str


ErrorDetailType = dict[str, Union[Type[DetailMessage], str]]
ERROR_CODE: dict[int, ErrorDetailType] = {
    400: {"model": DetailMessage, "description": "Insufficient query"},
    403: {"model": DetailMessage, "description": "Response too big"},
    404: {"model": DetailMessage, "description": "Item not found"},
    500: {"model": DetailMessage, "description": "Internal server error"},
}


def get_error_code(
    error_codes: Union[Iterable[int], Mapping[int, Any]],
) -> dict[Union[int, str], ErrorDetailType]:
    """
    Returns detailed Error Code objects to be used by fastapi documentation
    """
    return {k: v for k, v in ERROR_CODE.items() if k in error_codes}


def item_response(item: BaseModelORJson) -> Response:
    """
    Convert input model object to a Starlette Response object.
    Use this method to skip the second validation done by fastapi's json_encodable
    if the input model and the specificed response_model are the same.
    """
    return Response(
        item.model_dump_json(exclude_unset=True, exclude_none=True),
        media_type=JSON_MIME,
    )


def list_string(items: Iterable[BaseModelORJson]) -> str:
    """
    Convert list of model objects to a json formatted string.
    """
    return (
        "["
        + ",".join(
            item.model_dump_json(exclude_unset=True, exclude_none=True)
            for item in items
        )
        + "]"
    )


def list_string_exclude(items: Iterable[BaseModelORJson], exclude: set[str]) -> str:
    """
    Convert input list of model objects to a json formatted string.
    Attributes given to exclude will be excluded from the output json string.
    """
    all_items = ",".join(
        item.model_dump_json(exclude_unset=True, exclude_none=True, exclude=exclude)
        for item in items
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
        orjson.dumps(data, option=orjson.OPT_INDENT_2), media_type=JSON_MIME
    )
