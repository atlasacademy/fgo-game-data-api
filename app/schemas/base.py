from pydantic import BaseModel, ConfigDict, HttpUrl, PlainSerializer, TypeAdapter


class BaseModelORJson(BaseModel):
    model_config = ConfigDict(from_attributes=True, cache_strings=True)


HttpUrlAdapter: TypeAdapter[HttpUrl] = TypeAdapter(HttpUrl)


DecimalSerializer = PlainSerializer(
    lambda x: float(x), return_type=float, when_used="json"
)
