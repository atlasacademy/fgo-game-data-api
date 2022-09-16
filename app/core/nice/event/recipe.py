from ....config import Settings
from ....schemas.common import Region
from ....schemas.nice import AssetURL, NiceEventRecipe, NiceEventRecipeGift, NiceItem
from ....schemas.raw import (
    MstCommonConsume,
    MstCommonRelease,
    MstEventRecipe,
    MstEventRecipeGift,
)
from ...utils import fmt_url
from ..common_release import get_nice_common_release
from ..gift import GiftData, get_nice_common_consume, get_nice_gifts


settings = Settings()


def get_nice_recipe_gift(
    region: Region, recipe_gift: MstEventRecipeGift, gift_data: GiftData
) -> NiceEventRecipeGift:
    return NiceEventRecipeGift(
        idx=recipe_gift.idx,
        displayOrder=recipe_gift.displayOrder,
        topIconId=recipe_gift.topIconId,
        gifts=get_nice_gifts(region, recipe_gift.giftId, gift_data),
    )


def get_nice_recipe(
    region: Region,
    recipe: MstEventRecipe,
    recipe_gifts: list[MstEventRecipeGift],
    raw_consumes: list[MstCommonConsume],
    raw_releases: list[MstCommonRelease],
    item_map: dict[int, NiceItem],
    gift_data: GiftData,
) -> NiceEventRecipe:
    return NiceEventRecipe(
        id=recipe.id,
        icon=fmt_url(
            AssetURL.items,
            base_url=settings.asset_url,
            region=region,
            item_id=recipe.iconId,
        ),
        name=recipe.name,
        maxNum=recipe.maxNum,
        eventPointItem=item_map[recipe.eventPointItemId],
        eventPointNum=recipe.eventPointNum,
        consumes=[
            get_nice_common_consume(consume)
            for consume in raw_consumes
            if consume.id == recipe.commonConsumeId
        ],
        releaseConditions=[
            get_nice_common_release(release)
            for release in raw_releases
            if release.id == recipe.commonReleaseId
        ],
        closedMessage=recipe.closedMessage,
        recipeGifts=[
            get_nice_recipe_gift(region, recipe_gift, gift_data)
            for recipe_gift in recipe_gifts
            if recipe_gift.recipeId == recipe.id
        ],
    )
