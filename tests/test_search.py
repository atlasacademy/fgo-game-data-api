# pylint: disable=R0201
import pytest
from httpx import AsyncClient, Response


RAW_MAIN_ITEM = {
    "servant": "mstSvt",
    "equip": "mstSvt",
    "svt": "mstSvt",
    "function": "mstFunc",
    "buff": "mstBuff",
    "skill": "mstSkill",
    "NP": "mstTreasureDevice",
    "item": "mstItem",
}


def get_item_list(response: Response, response_type: str, endpoint: str) -> set[int]:
    item_type = endpoint.split("/")[1]
    if item_type == "script":
        return {item["scriptId"] for item in response.json()}
    if response_type == "raw":
        if item_type in RAW_MAIN_ITEM:
            main_item = RAW_MAIN_ITEM[item_type]
        else:
            raise ValueError
        return {item[main_item]["id"] for item in response.json()}
    else:
        if item_type in ("servant", "equip", "buff", "svt", "skill", "NP", "item"):
            id_name = "id"
        elif item_type == "function":
            id_name = "funcId"
        else:
            raise ValueError
        return {item[id_name] for item in response.json()}


test_cases_dict: dict[str, tuple[str, set[int]]] = {
    "equip_name_NA_1": ("NA/equip/search?name=Kaleidoscope", {9400340}),
    "equip_name_NA_2": ("NA/equip/search?name=Banquet", {9302550, 9400290}),
    "equip_name_JP": ("JP/equip/search?name=カレイドスコープ", {9400340}),
    "equip_short_name": ("NA/equip/search?name=scope", {9400340}),
    "servant_Artoria": ("JP/servant/search?name=Artoria&className=caster", {504500}),
    "servant_name_NA": (
        "NA/servant/search?name=Pendragon",
        {
            100100,
            100200,
            100300,
            102900,
            202600,
            301900,
            302000,
            402200,
            402700,
            900900,
        },
    ),
    "servant_name_rarity_class": (
        "NA/servant/search?name=Pendragon&rarity=5&className=saber",
        {100100, 102900},
    ),
    "servant_name_rarity_class_gender": (
        "NA/servant/search?name=Pendragon&rarity=5&className=saber&gender=female",
        {100100},
    ),
    "servant_class_attribute": (
        "NA/servant/search?className=archer&attribute=star",
        {201100, 202200, 203100},
    ),
    "servant_class_trait_rarity_lang": (
        "JP/servant/search?className=rider&trait=king&lang=en&rarity=3",
        {401100, 401500, 403900},
    ),
    "servant_search_Okita_Alter": (
        "NA/servant/search?name=Okita Souji (Alter)",
        {1000700},  # shouldn't return Okita Saber
    ),
    "servant_JP_search_EN_name": ("JP/servant/search?name=Skadi", {503900}),
    "servant_NA_search_Scathach": (
        "NA/servant/search?name=Scathach",
        {301300, 503900, 602400},
    ),
    "servant_search_Yagyu": ("NA/servant/search?name=Tajima", {103200}),
    "servant_search_equip": (
        "NA/servant/search?name=Golden%20Sumo&type=servantEquip&className=ALL",
        {9401640},
    ),
    "servant_search_voice_cond_svt_id": (
        "JP/servant/search?voiceCondSvt=202900&lang=en",
        {102800, 404000, 602300},
    ),
    "servant_search_voice_cond_svt_collectionNo": (
        "JP/servant/search?voiceCondSvt=200&lang=en",
        {102800, 404000, 602300},
    ),
    "servant_search_voice_cond_svt_group": (
        "JP/servant/search?voiceCondSvt=190&lang=en&className=archer",
        {201200, 202900},
    ),
    "servant_search_notTrait": (
        "NA/servant/search?notTrait=weakToEnumaElish&notTrait=genderMale&className=archer",
        {202200, 202900},
    ),
    "servant_search_conditional_trait": (
        "JP/servant/search?trait=1177&trait=104",
        {504500},
    ),
    "svt_search_enemy": (
        "JP/svt/search?lang=en&trait=2667&type=enemyCollection",
        {9940530, 9941040, 9941050, 9942530},
    ),
    "svt_search_flag": ("NA/svt/search?flag=svtEquipFriendShip&name=crown", {9300010}),
    "svt_search_en_illustrator_cv": (
        "JP/servant/search?cv=Mamiko Noto&illustrator=Takashi Takeuchi",
        {202900},
    ),
    "servant_search_va": ("JP/svt/search?cv=伊瀬茉莉也", {304400, 603500}),
    "servant_search_old_trait_name": (
        "NA/servant/search?trait=argonaut&rarity=2",
        {203500},
    ),
    "equip_search_illustrator": ("NA/svt/search?illustrator=Cogecha", {9403840}),
    "skill_search_type_coolDown_numFunc": (
        "NA/skill/search?lvl1coolDown=8&numFunctions=8&type=active",
        {961472, 961475, 961620},
    ),
    "skill_search_strength": (
        "JP/skill/search?strengthStatus=2&type=active",
        {94349, 136550},
    ),
    "skill_search_num": (
        "JP/skill/search?strengthStatus=99&type=active&numFunctions=5&num=3",
        {292452, 621675},
    ),
    "skill_search_priority": ("JP/skill/search?priority=5", {744450}),
    "skill_search_name": (
        "NA/skill/search?name=Mystic%20Eyes%20of%20Distortion%20EX&lvl1coolDown=7",
        {454650},
    ),
    "np_search_minNp_strength": (
        "NA/NP/search?minNpNpGain=220&strengthStatus=2",
        {601002},
    ),
    "np_search_hits_maxNp_numFunc": (
        "NA/NP/search?hits=10&maxNpNpGain=50&numFunctions=1",
        {202401},
    ),
    "np_search_name": ("NA/NP/search?name=Mystic%20Eyes", {202901, 602301, 602302}),
    "np_search_individuality": (
        "JP/NP/search?individuality=aoeNP&hits=6&card=arts&strengthStatus=0",
        {504201},
    ),
    "buff_type_tvals": (
        "NA/buff/search?type=upCommandall&tvals=cardQuick&name=Boost",
        {260, 499},
    ),
    "buff_type_vals": ("NA/buff/search?vals=buffCharm", {175, 926, 1315}),
    "buff_type_ckSelfIndv": (
        "NA/buff/search?ckSelfIndv=4002&ckSelfIndv=4003",
        {1162, 1589},
    ),
    "buff_type_ckOpIndv": (
        "NA/buff/search?ckOpIndv=4002&type=downDefencecommandall",
        {301, 456, 506, 1524, 2360},
    ),
    "buff_name": ("NA/buff/search?name=Battlefront Guardian of GUDAGUDA", {1056}),
    "buff_buffGroup": ("NA/buff/search?buffGroup=800", {182, 1178, 1311}),
    "func_type_targetType_targetTeam_vals": (
        "JP/function/search?type=addStateShort&targetType=ptAll&targetTeam=playerAndEnemy&vals=101",
        {115, 116, 117, 7691},
    ),
    "func_tvals": (
        "JP/function/search?type=addStateShort&tvals=divine",
        {965, 966, 967, 1165, 1166, 1167, 3802, 6372},
    ),
    "func_questTvals": (
        "JP/function/search?questTvals=94000046&targetType=ptFull",
        {889, 890, 891},
    ),
    "func_popupText": (
        "NA/function/search?popupText=Curse&targetType=self",
        {490, 1700, 2021, 2451, 4809, 5149},
    ),
}

test_cases = [pytest.param(*value, id=key) for key, value in test_cases_dict.items()]


test_not_found_dict = {
    "servant": "NA/servant/search?name=ÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛ",
    "servant_empty_name": "NA/servant/search?name=      ",
    "equip": "NA/equip/search?name=Kaleidoscope&rarity=4",
}

not_found_cases = [
    pytest.param(value, id=key) for key, value in test_not_found_dict.items()
]


@pytest.mark.asyncio
@pytest.mark.parametrize("response_type", ["basic", "nice", "raw"])
class TestSearch:
    @pytest.mark.parametrize("search_query,result", test_cases)
    async def test_search(
        self,
        client: AsyncClient,
        search_query: str,
        result: set[int],
        response_type: str,
    ) -> None:
        response = await client.get(f"/{response_type}/{search_query}")
        result_ids = get_item_list(response, response_type, search_query)
        assert response.status_code == 200
        assert result_ids == result

    @pytest.mark.parametrize("query", not_found_cases)
    async def test_not_found_any(
        self, client: AsyncClient, response_type: str, query: str
    ) -> None:
        response = await client.get(f"/{response_type}/{query}")
        assert response.status_code == 200
        assert response.text == "[]"

    @pytest.mark.parametrize(
        "endpoint", ["servant", "equip", "svt", "skill", "NP", "buff", "function"]
    )
    async def test_empty_input(
        self, client: AsyncClient, response_type: str, endpoint: str
    ) -> None:
        response = await client.get(f"/{response_type}/NA/{endpoint}/search")
        assert response.status_code == 400


basic_quest_search_test_cases_dict = {
    "quest_enemy_trait": (
        "NA/quest/phase/search?enemyTrait=304&warId=204",
        {(2000411, 2), (2000411, 4)},
    ),
    "quest_enemy_svt_ai_id": (
        "NA/quest/phase/search?enemySvtAiId=94040209",
        {(94040108, 4)},
    ),
    "quest_enemy_svt_id": (
        "NA/quest/phase/search?enemySvtId=402800&warId=9999",
        {(94040525, 1)},
    ),
    "quest_field_ai_id": ("JP/quest/phase/search?fieldAiId=90161870", {(94016145, 1)}),
    "quest_bgm_id": ("NA/quest/phase/search?bgmId=101", {(94008501, 1)}),
    "quest_battle_bg_id": (
        "NA/quest/phase/search?battleBgId=29000&warId=8208",
        {(94020906, 1)},
    ),
    "quest_field_trait_name": (
        "NA/quest/phase/search?warId=204&fieldIndividuality=fieldForest&name=Third",
        {(2000404, 6)},
    ),
    "quest_spot_name": (
        "NA/quest/phase/search?spotName=Rice Field&fieldIndividuality=2038",
        {(2000300, 1)},
    ),
    "quest_class_name_overwrite": (
        "NA/quest/phase/search?enemyClassName=cccFinaleEmiyaAlter",
        {(94034019, 2)},
    ),
    "quest_class_name_mstSvt": (
        "NA/quest/phase/search?warId=201&enemyClassName=assassin&type=main",
        {(2000112, 3)},
    ),
    "quest_type": (
        "JP/quest/phase/search?type=free&spotName=ディーヴァール",
        {(93030506, 1), (93030506, 2), (93030506, 3)},
    ),
    "quest_overwrite_spot": (
        "NA/quest/phase/search?spotName=Southern Town&type=main",
        {(3000412, 4), (3000412, 5)},
    ),
    "quest_flag": (
        "JP/quest/phase/search?flag=supportSelectAfterScript&flag=branch&warId=8362",
        {(94057198, 1), (94057199, 1)},
    ),
}
basic_quest_phase_test_cases = [
    pytest.param(*value, id=key)
    for key, value in basic_quest_search_test_cases_dict.items()
]


@pytest.mark.asyncio
@pytest.mark.parametrize("search_query,result", basic_quest_phase_test_cases)
async def test_search_basic_quest_phase(
    client: AsyncClient, search_query: str, result: set[tuple[int, int]]
) -> None:
    response = await client.get(f"/basic/{search_query}")
    result_ids = {(int(quest["id"]), int(quest["phase"])) for quest in response.json()}
    assert response.status_code == 200
    assert result_ids == result


@pytest.mark.asyncio
async def test_search_basic_quest_phase_empty(client: AsyncClient) -> None:
    response = await client.get("/basic/NA/quest/phase/search")
    assert response.status_code == 400


nice_raw_test_cases_dict = {
    "item_individuality": ("JP/item/search?individuality=10361", {94032206}),
    "item_use_name_background": (
        "NA/item/search?use=skill&use=ascension&use=costume&name=Claw&background=gold",
        {6507},
    ),
    "item_type": ("JP/item/search?type=chargeStone", {6}),
    "script_search": ("JP/script/search?query=存在したでしょう", {"0300051410"}),
}

nice_raw_test_cases = [
    pytest.param(*value, id=key) for key, value in nice_raw_test_cases_dict.items()
]


@pytest.mark.asyncio
@pytest.mark.parametrize("response_type", ["nice", "raw"])
class TestSearchNiceRaw:
    @pytest.mark.parametrize("search_query,result", nice_raw_test_cases)
    async def test_search_nice_raw(
        self,
        client: AsyncClient,
        search_query: str,
        result: set[int],
        response_type: str,
    ) -> None:
        response = await client.get(f"/{response_type}/{search_query}")
        result_ids = get_item_list(response, response_type, search_query)
        assert response.status_code == 200
        assert result_ids == result

    @pytest.mark.parametrize("endpoint", ["item"])
    async def test_empty_input(
        self, client: AsyncClient, response_type: str, endpoint: str
    ) -> None:
        response = await client.get(f"/{response_type}/NA/{endpoint}/search")
        assert response.status_code == 400

    @pytest.mark.parametrize("endpoint", ["servant", "equip", "svt"])
    async def test_too_many_results_svt(
        self, client: AsyncClient, response_type: str, endpoint: str
    ) -> None:
        response = await client.get(
            f"/{response_type}/NA/{endpoint}/search?type=normal"
        )
        assert response.status_code == 403

    async def test_too_many_results_buff(
        self, client: AsyncClient, response_type: str
    ) -> None:
        response = await client.get(
            f"/{response_type}/JP/buff/search?vals=buffPositiveEffect"
        )
        assert response.status_code == 403

    async def test_too_many_results_function(
        self, client: AsyncClient, response_type: str
    ) -> None:
        response = await client.get(
            f"/{response_type}/JP/function/search?type=addState"
        )
        assert response.status_code == 403

    async def test_too_many_results_skill(
        self, client: AsyncClient, response_type: str
    ) -> None:
        response = await client.get(f"/{response_type}/JP/skill/search?type=passive")
        assert response.status_code == 403

    async def test_too_many_results_np(
        self, client: AsyncClient, response_type: str
    ) -> None:
        response = await client.get(f"/{response_type}/NA/NP/search?minNpNpGain=40")
        assert response.status_code == 403
