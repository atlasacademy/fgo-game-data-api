from collections import defaultdict

import orjson
from pydantic import HttpUrl

from ....config import Settings
from ....data.custom_mappings import EXTRA_CHARAFIGURES, EXTRA_IMAGES
from ....schemas.common import Region
from ....schemas.gameenums import SvtType
from ....schemas.nice import AssetURL, ExtraAssets, ExtraAssetsUrl
from ....schemas.raw import ServantEntity
from ...utils import fmt_url


settings = Settings()


def get_male_image_extraAssets(region: Region, svt_id: int) -> ExtraAssets:
    base_settings_id: dict[str, int | str | HttpUrl] = {
        "base_url": settings.asset_url,
        "region": region,
        "item_id": svt_id,
    }

    return ExtraAssets(
        charaGraph=ExtraAssetsUrl(
            equip={svt_id: fmt_url(AssetURL.charaGraphDefault, **base_settings_id)}
        ),
        faces=ExtraAssetsUrl(
            equip={svt_id: fmt_url(AssetURL.face, **base_settings_id, i=0)}
        ),
        charaGraphEx=ExtraAssetsUrl(),
        charaGraphName=ExtraAssetsUrl(),
        narrowFigure=ExtraAssetsUrl(),
        charaFigure=ExtraAssetsUrl(),
        charaFigureForm={},
        charaFigureMulti={},
        commands=ExtraAssetsUrl(),
        status=ExtraAssetsUrl(),
        equipFace=ExtraAssetsUrl(
            equip={svt_id: fmt_url(AssetURL.equipFace, **base_settings_id, i=0)}
        ),
        image=ExtraAssetsUrl(),
        spriteModel=ExtraAssetsUrl(),
        charaGraphChange=ExtraAssetsUrl(),
        narrowFigureChange=ExtraAssetsUrl(),
        facesChange=ExtraAssetsUrl(),
    )


def get_svt_extraAssets(
    region: Region, svt_id: int, raw_svt: ServantEntity, costume_ids: dict[int, int]
) -> ExtraAssets:
    """
    Args:
        region (`Region`): region
        svt_id (`int`): servant ID
        raw_svt (`ServantEntity`): raw servant data
        costume_ids (`dict[int, int]`): servant costume limit to `battleCharaId` mapping

    Returns:
        ExtraAssets
    """
    charaGraph = ExtraAssetsUrl()
    charaGraphEx = ExtraAssetsUrl()
    charaGraphName = ExtraAssetsUrl()
    faces = ExtraAssetsUrl()
    commands = ExtraAssetsUrl()
    status = ExtraAssetsUrl()
    charaFigure = ExtraAssetsUrl()
    charaFigureForm: dict[int, dict[str, dict[int, str]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    charaFigureMulti: dict[int, dict[str, dict[int, str]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    narrowFigure = ExtraAssetsUrl()
    equipFace = ExtraAssetsUrl()
    image = ExtraAssetsUrl()
    spriteModel = ExtraAssetsUrl()
    charaGraphChange = ExtraAssetsUrl()
    narrowFigureChange = ExtraAssetsUrl()
    facesChange = ExtraAssetsUrl()

    base_settings = {"base_url": settings.asset_url, "region": region}
    base_settings_id: dict[str, int | str | HttpUrl] = {
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
    elif raw_svt.mstSvt.type == SvtType.SVT_MATERIAL_TD:
        charaGraph.ascension = {
            1: fmt_url(
                AssetURL.charaGraph[1],
                **base_settings,
                item_id=raw_svt.mstSvt.baseSvtId,
            )
        }
        faces.ascension = {
            0: fmt_url(
                AssetURL.face, **base_settings, item_id=raw_svt.mstSvt.baseSvtId, i=0
            )
        }
    elif raw_svt.mstSvt.type in (SvtType.ENEMY, SvtType.ENEMY_COLLECTION):
        all_limit_adds = {
            limit_add.limitCount: limit_add for limit_add in raw_svt.mstSvtLimitAdd
        }
        faces.ascension = {
            limit.limitCount: fmt_url(
                AssetURL.enemy,
                **base_settings,
                item_id=(
                    all_limit_adds[limit.limitCount].battleCharaId
                    if limit.limitCount in all_limit_adds
                    else svt_id
                ),
                i=limit.limitCount,
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

                    if "changeGraphSuffix" in strParam:
                        charaGraphChange.set_limit_asset(
                            svt_limit.limitCount,
                            fmt_url(
                                AssetURL.charaGraphChange[svt_limit.limitCount],
                                **base_settings_id,
                                suffix=strParam["changeGraphSuffix"],
                            ),
                            costume_ids,
                        )
                        narrowFigureChange.set_limit_asset(
                            svt_limit.limitCount,
                            fmt_url(
                                AssetURL.narrowFigureChange[svt_limit.limitCount],
                                **base_settings_id,
                                suffix=strParam["changeGraphSuffix"],
                            ),
                            costume_ids,
                        )

                    if "changeIconSuffix" in strParam:
                        facesChange.set_limit_asset(
                            svt_limit.limitCount,
                            fmt_url(
                                AssetURL.faceChange,
                                **base_settings_id,
                                i=svt_limit.limitCount,
                                suffix=strParam["changeIconSuffix"],
                            ),
                            costume_ids,
                        )
                except orjson.JSONDecodeError:  # pragma: no cover
                    pass

        if raw_svt.mstSvtAdd and "additionExpandImage" in raw_svt.mstSvtAdd.script:
            for i in raw_svt.mstSvtAdd.script["additionExpandImage"]:
                if i not in costume_ids:
                    if charaGraphEx.ascension is None:
                        charaGraphEx.ascension = {}
                    charaGraphEx.ascension[i + 1] = fmt_url(
                        AssetURL.charaGraphEx[i + 1], **base_settings_id
                    )

                else:
                    if charaGraphEx.costume is None:
                        charaGraphEx.costume = {}
                    charaGraphEx.costume[costume_ids[i]] = fmt_url(
                        AssetURL.charaGraphExCostume,
                        item_id=costume_ids[i],
                        **base_settings,
                    )

    elif raw_svt.mstSvt.isEquip():
        charaGraph.equip = {
            svt_id: fmt_url(AssetURL.charaGraphDefault, **base_settings_id)
        }
        faces.equip = {svt_id: fmt_url(AssetURL.face, **base_settings_id, i=0)}
        equipFace.equip = {svt_id: fmt_url(AssetURL.equipFace, **base_settings_id, i=0)}

        if raw_svt.mstSvtAdd and "additionExpandImage" in raw_svt.mstSvtAdd.script:
            charaGraphEx.equip = {
                svt_id: fmt_url(AssetURL.charaGraphExEquip, **base_settings_id)
            }

    for limit_add in raw_svt.mstSvtLimitAdd:
        model_url = fmt_url(
            AssetURL.servantModel, **base_settings, item_id=limit_add.battleCharaId
        )
        if limit_add.limitCount <= 10:
            if spriteModel.ascension is None:
                spriteModel.ascension = {limit_add.limitCount: model_url}
            else:
                spriteModel.ascension[limit_add.limitCount] = model_url
        else:
            if spriteModel.costume is None:
                spriteModel.costume = {limit_add.battleCharaId: model_url}
            else:
                spriteModel.costume[limit_add.battleCharaId] = model_url

    min_normal_limit_count = min(limit.limitCount for limit in raw_svt.mstSvtLimit)
    if raw_svt.mstSvt.isServant() or raw_svt.mstSvt.type == SvtType.ENEMY:
        model_url = fmt_url(AssetURL.servantModel, **base_settings, item_id=svt_id)
        if spriteModel.ascension is None:
            spriteModel.ascension = {min_normal_limit_count: model_url}
        elif min_normal_limit_count not in spriteModel.ascension:
            spriteModel.ascension[min_normal_limit_count] = model_url

    if svt_id in EXTRA_CHARAFIGURES:
        charaFigure.story = {}
        extra_chara_ids = sorted(EXTRA_CHARAFIGURES[svt_id])
        for battleCharaId in extra_chara_ids:
            charaFigure.story[battleCharaId] = fmt_url(
                AssetURL.charaFigureId, **base_settings, charaFigure=battleCharaId
            )
    else:
        extra_chara_ids = []

    for svtScript in raw_svt.mstSvtScript:
        script_form = svtScript.extendData.get("myroomForm", svtScript.form)
        if script_form != 0:
            asset_url = AssetURL.charaFigureForm.format(
                **base_settings, form_id=script_form, svtScript_id=svtScript.id
            )
            if svtScript.id // 10 == svt_id:
                ascension_level = svtScript.id % 10 + 1
                charaFigureForm[script_form]["ascension"][ascension_level] = asset_url
            elif svtScript.id // 10 in costume_ids.values():
                charaFigureForm[script_form]["costume"][svtScript.id // 10] = asset_url
            elif svtScript.id in extra_chara_ids:  # pragma: no cover
                charaFigureForm[script_form]["story"][svtScript.id] = asset_url

    for multiPortrait in raw_svt.mstSvtMultiPortrait:
        asset_url = AssetURL.charaFigureId.format(
            **base_settings, charaFigure=multiPortrait.portraitImageId
        )
        if multiPortrait.limitCount in costume_ids:  # pragma: no cover
            battleCharaId = costume_ids[multiPortrait.limitCount]
            charaFigureMulti[multiPortrait.idx]["costume"][battleCharaId] = asset_url
        else:
            charaFigureMulti[multiPortrait.idx]["ascension"][
                multiPortrait.limitCount + 1
            ] = asset_url

    image.story = {
        i: fmt_url(AssetURL.image, **base_settings, image=image)
        for i, image in enumerate(EXTRA_IMAGES.get(svt_id, []))
    }

    return ExtraAssets(
        charaGraph=charaGraph,
        charaGraphEx=charaGraphEx,
        charaGraphName=charaGraphName,
        faces=faces,
        charaFigure=charaFigure,
        charaFigureForm={
            k: ExtraAssetsUrl.parse_obj(v) for k, v in charaFigureForm.items()
        },
        charaFigureMulti={
            k: ExtraAssetsUrl.parse_obj(v) for k, v in charaFigureMulti.items()
        },
        narrowFigure=narrowFigure,
        commands=commands,
        status=status,
        equipFace=equipFace,
        image=image,
        spriteModel=spriteModel,
        charaGraphChange=charaGraphChange,
        narrowFigureChange=narrowFigureChange,
        facesChange=facesChange,
    )
