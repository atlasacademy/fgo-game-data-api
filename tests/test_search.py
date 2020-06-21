from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestEquipSearch:
    def test_search_name(self):
        response = client.get("/nice/NA/equip/search?name=Kaleidoscope")
        assert response.status_code == 200
        assert {item["id"] for item in response.json()} == {9400340}

    def test_search_name_raw(self):
        response = client.get("/raw/JP/equip/search?name=カレイドスコープ")
        assert response.status_code == 200
        assert {item["mstSvt"]["id"] for item in response.json()} == {9400340}

    def test_search_name_rarity(self):
        response = client.get("/nice/NA/equip/search?name=Kaleidoscope&rarity=4")
        assert response.status_code == 200
        assert response.text == "[]"

    def test_search_names(self):
        response = client.get("/nice/NA/equip/search?name=Banquet")
        assert response.status_code == 200
        assert {item["id"] for item in response.json()} == {9302550, 9400290}

    def test_NA_search_no_query(self):
        response = client.get("/nice/NA/equip/search")
        assert response.status_code == 400

    def test_JP_search_no_query(self):
        response = client.get("/raw/JP/equip/search")
        assert response.status_code == 400


class TestServantSearch:
    def test_search_name(self):
        response = client.get("/raw/NA/servant/search?name=Pendragon")
        assert response.status_code == 200
        assert {item["mstSvt"]["id"] for item in response.json()} == {
            100100,
            100200,
            100300,
            102900,
            202600,
            301900,
            302000,
            402200,
            402700,
        }

    def test_search_name_rarity_class(self):
        response = client.get(
            "/nice/NA/servant/search?name=Pendragon&rarity=5&className=saber"
        )
        print({item["id"] for item in response.json()})
        assert response.status_code == 200
        assert {item["id"] for item in response.json()} == {100100, 102900}

    def test_search_name_rarity_class_gender(self):
        response = client.get(
            "/nice/NA/servant/search?name=Pendragon&rarity=5&className=saber&gender=female"
        )
        print({item["id"] for item in response.json()})
        assert response.status_code == 200
        assert {item["id"] for item in response.json()} == {100100}

    def test_search_name_class_attribute(self):
        response = client.get("/nice/NA/servant/search?className=archer&attribute=star")
        print({item["id"] for item in response.json()})
        assert response.status_code == 200
        assert {item["id"] for item in response.json()} == {201100, 202200, 203100}

    def test_search_name_class_trait_rarity(self):
        response = client.get(
            "/nice/JP/servant/search?className=rider&trait=king&lang=en&rarity=3"
        )
        print({item["id"] for item in response.json()})
        assert response.status_code == 200
        assert {item["id"] for item in response.json()} == {401100, 401500, 403900}

    def test_nice_search_no_query(self):
        response = client.get("/nice/NA/servant/search")
        assert response.status_code == 400

    def test_raw_search_no_query(self):
        response = client.get("/raw/NA/servant/search")
        assert response.status_code == 400

    def test_NA_search_fuzzy_process_empty(self):
        response = client.get("/raw/NA/servant/search?name=ÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛ")
        assert response.status_code == 200
        assert response.text == "[]"

    def test_NA_search_Okita_Alter(self):  # shouldn't return Okita Saber
        response = client.get("/raw/NA/servant/search?name=Okita Souji (Alter)")
        assert response.status_code == 200
        assert {item["mstSvt"]["id"] for item in response.json()} == {1000700}

    def test_JP_search_Skadi(self):
        response = client.get("/raw/JP/servant/search?name=Skadi")
        assert response.status_code == 200
        assert {item["mstSvt"]["id"] for item in response.json()} == {503900}

    def test_NA_search_Scathach(self):
        response = client.get("/nice/NA/servant/search?name=Scathach")
        assert response.status_code == 200
        assert {item["id"] for item in response.json()} == {301300, 602400}

    def test_NA_search_Yagyu(self):
        response = client.get("/raw/NA/servant/search?name=Tajima")
        assert response.status_code == 200
        assert {item["mstSvt"]["id"] for item in response.json()} == {103200}
