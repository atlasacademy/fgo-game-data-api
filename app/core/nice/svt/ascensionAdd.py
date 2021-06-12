from typing import Union

from ....config import Settings
from ....schemas.common import Language, NiceTrait, Region
from ....schemas.nice import AscensionAdd, AssetURL
from ....schemas.raw import ServantEntity
from ...utils import get_np_name, get_traits_list, get_translation


settings = Settings()


def get_nice_ascensionAdd(
    region: Region, raw_svt: ServantEntity, costume_ids: dict[int, int], lang: Language
) -> AscensionAdd:
    OVERWRITE_FIELDS = [
        "overWriteServantName",
        "overWriteServantBattleName",
        "overWriteTDName",
        "overWriteTDRuby",
        "overWriteTDFileName",
    ]

    ascensionAdd: dict[str, dict[str, dict[int, Union[list[NiceTrait], int, str]]]] = {
        ascensionAddField: {"ascension": {}, "costume": {}}
        for ascensionAddField in OVERWRITE_FIELDS + ["individuality", "voicePrefix"]
    }

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
            else []
        )

        ascensionAdd["voicePrefix"][dict_to_add][key_value] = limitAdd.voicePrefix

    for overwrite_field in OVERWRITE_FIELDS:
        ascensionAdd[overwrite_field] = {"ascension": {}, "costume": {}}
        for limitAdd in raw_svt.mstSvtLimitAdd:
            if overwrite_field in limitAdd.script:
                add_category = (
                    "costume" if limitAdd.limitCount in costume_ids else "ascension"
                )
                add_data = limitAdd.script[overwrite_field]

                if overwrite_field == "overWriteTDFileName":
                    add_data = AssetURL.commandFile.format(
                        base_url=settings.asset_url,
                        region=region,
                        item_id=raw_svt.mstSvt.id,
                        file_name=add_data,
                    )
                elif region == Region.JP:
                    if overwrite_field in (
                        "overWriteServantName",
                        "overWriteServantBattleName",
                    ):
                        add_data = get_translation(lang, add_data)
                    elif overwrite_field == "overWriteTDName":
                        add_data = get_np_name(
                            add_data,
                            limitAdd.script.get("overWriteTDRuby", add_data),
                            lang,
                        )

                ascensionAdd[overwrite_field][add_category][
                    limitAdd.limitCount
                ] = add_data

    return AscensionAdd.parse_obj(ascensionAdd)
