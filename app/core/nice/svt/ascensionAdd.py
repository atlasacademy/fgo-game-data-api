from typing import Dict, List, Union

from ....config import Settings
from ....data.custom_mappings import TRANSLATIONS
from ....schemas.common import Language, NiceTrait, Region
from ....schemas.nice import AscensionAdd, AssetURL
from ....schemas.raw import ServantEntity
from ...utils import get_safe, get_traits_list


settings = Settings()


def get_nice_ascensionAdd(
    region: Region, raw_svt: ServantEntity, costume_ids: Dict[int, int], lang: Language
) -> AscensionAdd:
    OVERWRITE_FIELDS = [
        "overWriteServantName",
        "overWriteServantBattleName",
        "overWriteTDName",
        "overWriteTDRuby",
        "overWriteTDFileName",
    ]

    ascensionAdd: Dict[str, Dict[str, Dict[int, Union[List[NiceTrait], int, str]]]] = {
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

                if overwrite_field == "overWriteTDFileName":
                    add_data: str = AssetURL.commandFile.format(
                        base_url=settings.asset_url,
                        region=region,
                        item_id=raw_svt.mstSvt.id,
                        file_name=limitAdd.script[overwrite_field],
                    )
                elif (
                    region == Region.JP
                    and lang == Language.en
                    and overwrite_field
                    in [
                        "overWriteServantName",
                        "overWriteServantBattleName",
                    ]
                ):
                    add_data = get_safe(TRANSLATIONS, limitAdd.script[overwrite_field])
                else:
                    add_data = limitAdd.script[overwrite_field]

                ascensionAdd[overwrite_field][add_category][
                    limitAdd.limitCount
                ] = add_data

    return AscensionAdd.parse_obj(ascensionAdd)
