from collections import defaultdict
from typing import Union

import orjson
from pydantic import HttpUrl
from pydantic.tools import parse_obj_as
from sqlalchemy.engine import Connection

from ....config import Settings
from ....data.custom_mappings import EXTRA_CHARAFIGURES, EXTRA_IMAGES
from ....db.helpers import svt
from ....schemas.common import Region
from ....schemas.gameenums import SvtType
from ....schemas.nice import AssetURL, ExtraAssets, ExtraAssetsUrl
from ....schemas.raw import ServantEntity


settings = Settings()


def fmt_url(url_fmt: str, **kwargs: Union[int, str]) -> HttpUrl:
    url: HttpUrl = parse_obj_as(HttpUrl, url_fmt.format(**kwargs))
    return url


def get_svt_extraAssets(
    conn: Connection,
    region: Region,
    svt_id: int,
    raw_svt: ServantEntity,
    costume_ids: dict[int, int],
) -> ExtraAssets:
    charaGraph = ExtraAssetsUrl()
    charaGraphName = ExtraAssetsUrl()
    faces = ExtraAssetsUrl()
    commands = ExtraAssetsUrl()
    status = ExtraAssetsUrl()
    charaFigure = ExtraAssetsUrl()
    charaFigureForm: dict[int, dict[str, dict[int, str]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    narrowFigure = ExtraAssetsUrl()
    equipFace = ExtraAssetsUrl()
    image = ExtraAssetsUrl()

    base_settings = {"base_url": settings.asset_url, "region": region}
    base_settings_id: dict[str, Union[int, str]] = {
        "base_url": settings.asset_url,
        "region": region,
        "item_id": svt_id,
    }

    if raw_svt.mstSvt.type in (
        SvtType.ENEMY_COLLECTION_DETAIL,
        SvtType.COMBINE_MATERIAL,
        SvtType.STATUS_UP,
    ):
        charaGraph.ascension = {
            0: fmt_url(AssetURL.charaGraphDefault, **base_settings_id)
        }
        faces.ascension = {0: fmt_url(AssetURL.face, **base_settings_id, i=0)}
    elif raw_svt.mstSvt.type in (SvtType.ENEMY, SvtType.ENEMY_COLLECTION):
        faces.ascension = {
            limit.limitCount: fmt_url(
                AssetURL.enemy, **base_settings_id, i=limit.limitCount
            )
            for limit in raw_svt.mstSvtLimit
        }
    elif raw_svt.mstSvt.isServant():
        charaGraph.ascension = {
            i: fmt_url(AssetURL.charaGraph[i], **base_settings_id) for i in range(1, 5)
        }
        faces.ascension = {
            (i + 1): fmt_url(AssetURL.face, **base_settings_id, i=i) for i in range(4)
        }
        commands.ascension = {
            i: fmt_url(AssetURL.commands, **base_settings_id, i=i) for i in range(1, 4)
        }
        status.ascension = {
            i: fmt_url(AssetURL.status, **base_settings_id, i=i) for i in range(1, 4)
        }
        charaFigure.ascension = {
            (i + 1): fmt_url(AssetURL.charaFigure, **base_settings_id, i=i)
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
        narrowFigure.ascension = {
            i: fmt_url(AssetURL.narrowFigure[i], **base_settings_id)
            for i in range(1, 5)
        }

        if costume_ids:
            charaGraph.costume = {
                costume_id: fmt_url(
                    AssetURL.charaGraphDefault, **base_settings, item_id=costume_id
                )
                for costume_id in costume_ids.values()
            }
            faces.costume = {
                costume_id: fmt_url(
                    AssetURL.face, **base_settings, item_id=costume_id, i=0
                )
                for costume_id in costume_ids.values()
            }
            charaFigure.costume = {
                costume_id: fmt_url(
                    AssetURL.charaFigure, **base_settings, item_id=costume_id, i=0
                )
                for costume_id in costume_ids.values()
            }
            charaGraph.costume = {
                costume_id: fmt_url(
                    AssetURL.charaGraphDefault, **base_settings, item_id=costume_id
                )
                for costume_id in costume_ids.values()
            }
            narrowFigure.costume = {
                costume_id: fmt_url(
                    AssetURL.narrowFigureDefault, **base_settings, item_id=costume_id
                )
                for costume_id in costume_ids.values()
            }
            status.costume = {
                costume_id: fmt_url(AssetURL.status, **base_settings_id, i=limit)
                for limit, costume_id in costume_ids.items()
            }
            commands.costume = {
                costume_id: fmt_url(AssetURL.commands, **base_settings_id, i=limit)
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
                        if not charaGraphName.ascension:
                            charaGraphName.ascension = {
                                i: fmt_url(
                                    AssetURL.charaGraphName, **base_settings_id, i=i
                                )
                                for i in range(1, 5)
                            }
                except orjson.JSONDecodeError:  # pragma: no cover
                    # Hard to test this since none of the saintGraphImageId json is broken
                    pass

    elif raw_svt.mstSvt.isEquip():
        charaGraph.equip = {
            svt_id: fmt_url(AssetURL.charaGraphDefault, **base_settings_id)
        }
        faces.equip = {svt_id: fmt_url(AssetURL.face, **base_settings_id, i=0)}
        equipFace.equip = {svt_id: fmt_url(AssetURL.equipFace, **base_settings_id, i=0)}

    if svt_id in EXTRA_CHARAFIGURES:
        charaFigure.story = {}
        for charaFigure_id in sorted(EXTRA_CHARAFIGURES[svt_id]):
            charaFigure.story[charaFigure_id] = fmt_url(
                AssetURL.charaFigureId, **base_settings, charaFigure=charaFigure_id
            )

            svtScripts = svt.get_svt_script(conn, charaFigure_id // 10)
            for svtScript in svtScripts:
                script_form = svtScript.extendData.get("myroomForm", svtScript.form)
                if script_form != 0:
                    charaFigureForm[script_form]["story"][
                        svtScript.id
                    ] = AssetURL.charaFigureForm.format(
                        **base_settings, form_id=script_form, svtScript_id=svtScript.id
                    )

    image.story = {
        i: fmt_url(AssetURL.image, **base_settings, image=image)
        for i, image in enumerate(EXTRA_IMAGES.get(svt_id, []))
    }

    return ExtraAssets(
        charaGraph=charaGraph,
        charaGraphName=charaGraphName,
        faces=faces,
        charaFigure=charaFigure,
        charaFigureForm={
            k: ExtraAssetsUrl.parse_obj(v) for k, v in charaFigureForm.items()
        },
        narrowFigure=narrowFigure,
        commands=commands,
        status=status,
        equipFace=equipFace,
        image=image,
    )
