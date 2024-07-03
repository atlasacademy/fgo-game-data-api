from typing import cast

import orjson
from pydantic import HttpUrl

from ....config import Settings
from ....schemas.common import Language, NiceTrait, Region
from ....schemas.enums import ATTRIBUTE_NAME
from ....schemas.nice import AscensionAdd, AssetURL, NiceCommonRelease
from ....schemas.raw import ServantEntity
from ...utils import fmt_url, get_np_name, get_traits_list, get_translation
from ..common_release import get_nice_common_release


settings = Settings()


def get_nice_ascensionAdd(
    region: Region, raw_svt: ServantEntity, costume_ids: dict[int, int], lang: Language
) -> AscensionAdd:
    base_settings_id: dict[str, int | str | HttpUrl] = {
        "base_url": settings.asset_url,
        "region": region,
        "item_id": raw_svt.mstSvt.id,
    }
    OVERWRITE_FIELDS = {
        "overWriteServantName": "overWriteServantName",
        "originalOverWriteServantName": "overWriteServantName",
        "overWriteServantBattleName": "overWriteServantBattleName",
        "originalOverWriteServantBattleName": "overWriteServantBattleName",
        "overWriteTDName": "overWriteTDName",
        "originalOverWriteTDName": "overWriteTDName",
        "overWriteTDRuby": "overWriteTDRuby",
        "overWriteTDFileName": "overWriteTDFileName",
        "overWriteTDRank": "overWriteTDRank",
        "overWriteTDTypeText": "overWriteTDTypeText",
    }

    ascensionAdd: dict[
        str,
        dict[
            str,
            dict[int, list[NiceCommonRelease] | list[NiceTrait] | int | str | HttpUrl],
        ],
    ] = {
        ascensionAddField: {"ascension": {}, "costume": {}}
        for ascensionAddField in set(OVERWRITE_FIELDS)
        | {"individuality", "voicePrefix", "lvMax", "rarity", "attribute"}
    }

    ascensionAdd["charaGraphChange"] = {"ascension": {}, "costume": {}}
    ascensionAdd["charaGraphChangeCommonRelease"] = {"ascension": {}, "costume": {}}
    ascensionAdd["faceChange"] = {"ascension": {}, "costume": {}}
    ascensionAdd["faceChangeCommonRelease"] = {"ascension": {}, "costume": {}}

    for limit in raw_svt.mstSvtLimit:
        ascensionAdd["lvMax"]["ascension"][limit.limitCount] = limit.lvMax
        ascensionAdd["rarity"]["ascension"][limit.limitCount] = limit.rarity
        try:
            strParam = orjson.loads(limit.strParam)
            if "changeGraphCommonReleaseId" in strParam:
                nice_release = [
                    get_nice_common_release(cr)
                    for cr in raw_svt.mstCommonRelease
                    if cr.id == strParam["changeGraphCommonReleaseId"]
                ]
                ascensionAdd["charaGraphChangeCommonRelease"]["ascension"][
                    limit.limitCount
                ] = nice_release
            if "changeGraphSuffix" in strParam:
                asset_url = fmt_url(
                    AssetURL.charaGraphChange[limit.limitCount],
                    **base_settings_id,
                    suffix=strParam["changeGraphSuffix"],
                )
                ascensionAdd["charaGraphChange"]["ascension"][
                    limit.limitCount
                ] = asset_url
            if "changeIconCommonReleaseId" in strParam:
                nice_release = [
                    get_nice_common_release(cr)
                    for cr in raw_svt.mstCommonRelease
                    if cr.id == strParam["changeIconCommonReleaseId"]
                ]
                ascensionAdd["faceChangeCommonRelease"]["ascension"][
                    limit.limitCount
                ] = nice_release
            if "changeIconSuffix" in strParam:
                asset_url = fmt_url(
                    AssetURL.faceChange,
                    **base_settings_id,
                    i=limit.limitCount,
                    suffix=strParam["changeIconSuffix"],
                )
                ascensionAdd["faceChange"]["ascension"][limit.limitCount] = asset_url

        except orjson.JSONDecodeError:  # pragma: no cover
            pass

    for limitAdd in raw_svt.mstSvtLimitAdd:
        if limitAdd.limitCount in costume_ids:
            key_value = costume_ids[limitAdd.limitCount]
            dict_to_add = "costume"
        else:
            key_value = limitAdd.limitCount
            dict_to_add = "ascension"

        ascensionAdd["individuality"][dict_to_add][key_value] = (
            get_traits_list(
                sorted(set(limitAdd.individuality + raw_svt.mstSvt.individuality))
            )
            if limitAdd.individuality
            else cast(list[NiceTrait], [])
        )

        if limitAdd.attri is not None and limitAdd.attri != -1:
            ascensionAdd["attribute"][dict_to_add][key_value] = ATTRIBUTE_NAME[
                limitAdd.attri
            ]

        ascensionAdd["voicePrefix"][dict_to_add][key_value] = limitAdd.voicePrefix

    for dst_field, src_field in OVERWRITE_FIELDS.items():
        ascensionAdd[dst_field] = {"ascension": {}, "costume": {}}
        for limitAdd in raw_svt.mstSvtLimitAdd:
            if src_field in limitAdd.script:
                add_category = (
                    "costume" if limitAdd.limitCount in costume_ids else "ascension"
                )
                add_data = limitAdd.script[src_field]

                if dst_field == "overWriteTDFileName":
                    add_data = AssetURL.commandFile.format(
                        base_url=settings.asset_url,
                        region=region,
                        item_id=raw_svt.mstSvt.id,
                        file_name=add_data,
                    )
                elif region == Region.JP:
                    if dst_field in (
                        "overWriteServantName",
                        "overWriteServantBattleName",
                    ):
                        add_data = get_translation(lang, add_data)
                    elif dst_field == "overWriteTDName":
                        add_data = get_np_name(
                            add_data,
                            limitAdd.script.get("overWriteTDRuby", add_data),
                            lang,
                        )

                ascensionAdd[dst_field][add_category][limitAdd.limitCount] = add_data

    return AscensionAdd.model_validate(ascensionAdd)
