# Types for FGO Game Data API

This is a package containing the Pydantic definitions of the objects returned by https://api.atlasacademy.io/rapidoc.

Example usage:
```
from fgo_api_types.enums import Trait
from fgo_api_types.gameenums import SvtType
from fgo_api_types.nice import NiceServant

r = httpx.get("https://api.atlasacademy.io/nice/NA/servant/200")
fujino = NiceServant.parse_raw(r.content)

assert Trait.genderFemale in fujino.traits
```