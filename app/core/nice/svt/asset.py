from collections import defaultdict
from typing import Dict

import orjson

from ....config import Settings
from ....data.custom_mappings import EXTRA_CHARAFIGURES, EXTRA_IMAGES
from ....data.gamedata import masters
from ....schemas.common import Region
from ....schemas.enums import SvtType
from ....schemas.nice import AssetURL, ExtraAssets
from ....schemas.raw import ServantEntity


settings = Settings()


def get_svt_extraAssets(
    region: Region, svt_id: int, raw_svt: ServantEntity, costume_ids: Dict[int, int]
) -> ExtraAssets:
    charaGraph: Dict[str, Dict[int, str]] = {}
    charaGraphName: Dict[str, Dict[int, str]] = {}
    faces: Dict[str, Dict[int, str]] = {}
    commands: Dict[str, Dict[int, str]] = {}
    status: Dict[str, Dict[int, str]] = {}
    charaFigure: Dict[str, Dict[int, str]] = {}
    charaFigureForm: Dict[int, Dict[str, Dict[int, str]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    narrowFigure: Dict[str, Dict[int, str]] = {}
    equipFace: Dict[str, Dict[int, str]] = {}
    image: Dict[str, Dict[int, str]] = {}

    base_settings = {"base_url": settings.asset_url, "region": region}
    base_settings_id = dict(item_id=svt_id, **base_settings)

    if raw_svt.mstSvt.type in (
        SvtType.ENEMY_COLLECTION_DETAIL,
        SvtType.COMBINE_MATERIAL,
        SvtType.STATUS_UP,
    ):
        charaGraph["ascension"] = {
            0: AssetURL.charaGraphDefault.format(**base_settings_id)
        }
        faces["ascension"] = {0: AssetURL.face.format(**base_settings_id, i=0)}
    elif raw_svt.mstSvt.type in (SvtType.ENEMY, SvtType.ENEMY_COLLECTION):
        faces["ascension"] = {
            limit.limitCount: AssetURL.enemy.format(
                **base_settings_id, i=limit.limitCount
            )
            for limit in raw_svt.mstSvtLimit
        }
    elif raw_svt.mstSvt.isServant():
        charaGraph["ascension"] = {
            i: AssetURL.charaGraph[i].format(**base_settings_id) for i in range(1, 5)
        }
        faces["ascension"] = {
            (i + 1): AssetURL.face.format(**base_settings_id, i=i) for i in range(4)
        }
        commands["ascension"] = {
            i: AssetURL.commands.format(**base_settings_id, i=i) for i in range(1, 4)
        }
        status["ascension"] = {
            i: AssetURL.status.format(**base_settings_id, i=i) for i in range(1, 4)
        }
        charaFigure["ascension"] = {
            (i + 1): AssetURL.charaFigure.format(**base_settings_id, i=i)
            for i in range(3)
        }
        for svtScript in raw_svt.mstSvtScript:
            script_form = svtScript.extendData.get("myroomForm", svtScript.form)
            if script_form != 0:
                charaFigureForm[script_form]["ascension"][
                    svtScript.id % 10 + 1
                ] = AssetURL.charaFigureForm.format(
                    **base_settings, form_id=script_form, svtScript_id=svtScript.id
                )
        narrowFigure["ascension"] = {
            i: AssetURL.narrowFigure[i].format(**base_settings_id) for i in range(1, 5)
        }

        if costume_ids:
            charaGraph["costume"] = {
                costume_id: AssetURL.charaGraphDefault.format(
                    **base_settings, item_id=costume_id
                )
                for costume_id in costume_ids.values()
            }
            faces["costume"] = {
                costume_id: AssetURL.face.format(
                    **base_settings, item_id=costume_id, i=0
                )
                for costume_id in costume_ids.values()
            }
            charaFigure["costume"] = {
                costume_id: AssetURL.charaFigure.format(
                    **base_settings, item_id=costume_id, i=0
                )
                for costume_id in costume_ids.values()
            }
            charaGraph["costume"] = {
                costume_id: AssetURL.charaGraphDefault.format(
                    **base_settings, item_id=costume_id
                )
                for costume_id in costume_ids.values()
            }
            narrowFigure["costume"] = {
                costume_id: AssetURL.narrowFigureDefault.format(
                    **base_settings, item_id=costume_id
                )
                for costume_id in costume_ids.values()
            }
            status["costume"] = {
                costume_id: AssetURL.status.format(**base_settings_id, i=limit)
                for limit, costume_id in costume_ids.items()
            }
            commands["costume"] = {
                costume_id: AssetURL.commands.format(**base_settings_id, i=limit)
                for limit, costume_id in costume_ids.items()
            }

        for svt_limit in raw_svt.mstSvtLimit:
            if svt_limit.strParam != "":
                try:
                    strParam = orjson.loads(svt_limit.strParam)
                    if "saintGraphImageId" in strParam:
                        # image_id = strParam["saintGraphImageId"]
                        # base_settings_name = dict(i=image_id, **base_settings)

                        # if svt_limit.limitCount in costume_ids:
                        #     if "costume" not in charaGraphName:
                        #         charaGraphName["costume"] = {}
                        #     costume_id = costume_ids[svt_limit.limitCount]
                        #     charaGraphName["costume"][
                        #         costume_id
                        #     ] = AssetURL.charaGraphName.format(
                        #         **base_settings_name, item_id=costume_id
                        #     )
                        if "ascension" not in charaGraphName:
                            charaGraphName["ascension"] = {
                                i: AssetURL.charaGraphName.format(
                                    **base_settings_id, i=i
                                )
                                for i in range(1, 5)
                            }
                except orjson.JSONDecodeError:  # pragma: no cover
                    # Hard to test this since none of the saintGraphImageId json is broken
                    pass

    elif raw_svt.mstSvt.isEquip():
        charaGraph["equip"] = {
            svt_id: AssetURL.charaGraphDefault.format(**base_settings_id)
        }
        faces["equip"] = {svt_id: AssetURL.face.format(**base_settings_id, i=0)}
        equipFace["equip"] = {
            svt_id: AssetURL.equipFace.format(**base_settings_id, i=0)
        }

    if svt_id in EXTRA_CHARAFIGURES:
        charaFigure["story"] = {}
        for charaFigure_id in sorted(EXTRA_CHARAFIGURES[svt_id]):
            charaFigure["story"][charaFigure_id] = AssetURL.charaFigureId.format(
                **base_settings, charaFigure=charaFigure_id
            )

            svtScripts = masters[region].mstSvtScriptId.get(charaFigure_id // 10, [])
            for svtScript in svtScripts:
                script_form = svtScript.extendData.get("myroomForm", svtScript.form)
                if script_form != 0:
                    charaFigureForm[script_form]["story"][
                        svtScript.id
                    ] = AssetURL.charaFigureForm.format(
                        **base_settings, form_id=script_form, svtScript_id=svtScript.id
                    )

    image["story"] = {
        i: AssetURL.image.format(**base_settings, image=image)
        for i, image in enumerate(EXTRA_IMAGES.get(svt_id, []))
    }

    return ExtraAssets.parse_obj(
        {
            "charaGraph": charaGraph,
            "charaGraphName": charaGraphName,
            "faces": faces,
            "charaFigure": charaFigure,
            "charaFigureForm": charaFigureForm,
            "narrowFigure": narrowFigure,
            "commands": commands,
            "status": status,
            "equipFace": equipFace,
            "image": image,
        }
    )
