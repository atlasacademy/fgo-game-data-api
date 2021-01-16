import json
from typing import Any, Dict, Iterable, Mapping, Optional, Set, Type, Union

from fastapi.responses import Response
from pydantic import BaseModel

from ..schemas.base import BaseModelORJson
from ..schemas.common import Language


JSON_MIME = "application/json"


class DetailMessage(BaseModel):
    detail: str


ErrorDetailType = Dict[str, Union[Type[DetailMessage], str]]
ERROR_CODE: Dict[int, ErrorDetailType] = {
    400: {"model": DetailMessage, "description": "Insufficient query"},
    403: {"model": DetailMessage, "description": "Response too big"},
    404: {"model": DetailMessage, "description": "Item not found"},
    500: {"model": DetailMessage, "description": "Internal server error"},
}


def get_error_code(
    error_codes: Union[Iterable[int], Mapping[int, Any]]
) -> Dict[Union[int, str], ErrorDetailType]:
    return {k: v for k, v in ERROR_CODE.items() if k in error_codes}


def language_parameter(lang: Optional[Language] = None) -> Language:
    if lang:
        return lang
    else:
        return Language.jp


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
        + ",".join(item.json(exclude_unset=True, exclude_none=True) for item in items)
        + "]"
    )


def list_string_exclude(items: Iterable[BaseModelORJson], exclude: Set[str]) -> str:
    """
    Convert input list of model objects to a json formatted string.
    Attributes given to exclude will be excluded from the output json string.
    """
    all_items = ",".join(
        item.json(exclude_unset=True, exclude_none=True, exclude=exclude)
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
        json.dumps(data, indent=2, ensure_ascii=False), media_type=JSON_MIME
    )
