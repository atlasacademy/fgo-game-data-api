# FGO game data API <!-- omit in toc -->

HTTP API for FGO game data. Transform the raw game data into something a bit more manageable.

View the API documentation here: https://api.atlasacademy.io.

- [Environment variables](#environment-variables)
  - [Required variables](#required-variables)
  - [Optional variables](#optional-variables)
  - [Secrets](#secrets)
  - [config.json](#configjson)
- [Development environment set up](#development-environment-set-up)
- [Run the API server](#run-the-api-server)
- [Architecture](#architecture)
- [Linting](#linting)
- [Formatting](#formatting)
- [Dependencies](#dependencies)
- [Testing](#testing)
- [Helper scripts](#helper-scripts)
  - [`extract_enums.py`](#extract_enumspy)
  - [`update_ce_translation.py`](#update_ce_translationpy)
  - [`load_rayshift_quest_list.py`](#load_rayshift_quest_listpy)
  - [`get_test_data.py`](#get_test_datapy)

### Environment variables


List of environment variables for the main app.

#### Required variables
- `DATA`: A JSON object string with keys being region strings and values being gamedata's folder location and Postgresql DSN. Not all regions are required in the object. Any combination of regions is accepted.
- `REDISDSN`: Redis DSN to a Redis server for caching.

#### Optional variables
<details>
<summary>Click to view</summary>

- `REDIS_PREFIX`: default to `fgoapi`. Prefix for redis keys.
- `CLEAR_REDIS_CACHE`: default to `True`. If set, will clear the redis cache on start and when the webhook above is used.
- `RATE_LIMIT_PER_5_SEC`: default to `100`. The rate limit per 5 seconds for nice and raw endpoints.
- `RAYSHIFT_API_KEY`: default to `""`. Rayshift.io API key to pull quest data.
- `RAYSHIFT_API_URL`: default to https://rayshift.io/api/v1/. Rayshift.io API URL.
- `QUEST_CACHE_LENGTH`: default to `3600`. How long to cache the quest and war endpoints in seconds. Because the rayshift data is updated continously, web and quest endpoints have lower cache time.
- `WRITE_POSTGRES_DATA`: default to `True`. Overwrite the data in PostgreSQL when importing.
- `WRITE_REDIS_DATA`: default to `True`. Overwrite the data in Redis when importing.
- `ASSET_URL`: defaults to https://assets.atlasacademy.io/GameData/. Base URL for the game assets.
- `OPENAPI_URL`: default to `None`. Set the server URL in the openapi schema export.
- `EXPORT_ALL_NICE`: default to `False`. If set to `True`, at start the app will generate nice data of all servant and CE and serve them at the `/export` endpoint. It's recommended to serve the files in the `/export` folder using nginx or equivalent webserver to lighten the load on the API server.
- `DOCUMENTATION_ALL_NICE`: default to `False`. If set to `True`, there will be links to the exported all nice files in the documentation.
- `GITHUB_WEBHOOK_SECRET`: default to `""`. If set, will add a webhook location at `/GITHUB_WEBHOOK_SECRET/update` that will pull and update the game data. If it's not set, the endpoint is not created.
- `GITHUB_WEBHOOK_GIT_PULL`: default to `False`. If set, the app will do `git pull` on the gamedata repos when the webhook above is used.
- `GITHUB_WEBHOOK_SLEEP`: default to `0`. If set, will delay the action above by `GITHUB_WEBHOOK_SLEEP` seconds.

</details>

#### Secrets

Secret variables can be put in the [secrets](secrets/) folder instead of being supplied as environment variable:
```
> cat .\secrets\rayshift_api_key
eca334a9-3289-4ad7-9b92-1ec2bbc3fc19
> cat .\secrets\redisdsn
redis://localhost
```

#### config.json

You can make a `config.json` file with the settings instead of setting the environment variables. Check the [config.sample.json](config.sample.json) file for an example.

Settings at a higher level will override the settings at a lower level.
1. Secrets variable
2. Enviornment variable
3. `.env` file
4. `config.json`

### Development environment set up

Make sure poetry is installed: https://python-poetry.org/docs/#installation.

Docker is recommended to set up the Postgres and redis servers but those can be set up manually as well. Postgres needs the [PGroonga](https://pgroonga.github.io/install/) extension installed.

```
> git clone --depth 1 --branch JP https://github.com/atlasacademy/fgo-game-data.git fgo-game-data-jp
> git clone --depth 1 --branch NA https://github.com/atlasacademy/fgo-game-data.git fgo-game-data-na
# It's not neccecary to clone the other regions.
> git clone --depth 1 --branch CN https://github.com/atlasacademy/fgo-game-data.git fgo-game-data-cn
> git clone --depth 1 --branch KR https://github.com/atlasacademy/fgo-game-data.git fgo-game-data-kr
> git clone --depth 1 --branch TW https://github.com/atlasacademy/fgo-game-data.git fgo-game-data-tw
> git clone https://github.com/atlasacademy/fgo-game-data-api.git
> cd fgo-game-data-api
> cp config.sample.json config.json
> docker-compose up -d
> poetry install
> poetry shell
```

### Run the API server

Run at the project root to start the API server:

```
> uvicorn app.main:app --reload --log-level debug --reload-dir app

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [16680] using watchgod
INFO      fgoapi: Loading game data …
INFO      fgoapi: Loaded game data in 15.14s.
INFO:     Started server process [33312]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
DEBUG     fgoapi: Processed in 0.21ms.
INFO:     127.0.0.1:56759 - "GET / HTTP/1.1" 307 Temporary Redirect
DEBUG     fgoapi: Processed in 0.24ms.
INFO:     127.0.0.1:56759 - "GET /rapidoc HTTP/1.1" 200 OK
```

Go to http://127.0.0.1:8000 for the API documentation.

Tips:
- Change `write_postgres_data` to `false` after the first run to speed up reloading if it's not needed (schema doesn't change or data hasn't changed).

### Architecture

- `main.py`: Main entrypoint of the application.
- `routers/`: Routers to deal with incoming requests. The routers call functions from `core` to get the response data.
- `core/`: Build response data. Get raw data from either `db/helpers/` or `redis/helpers`.
- `data/`: Import translation data into memory. Preprocessing conde for data to be imported into db and redis.
- `db/`: DB stuffs.
  - `db/helpers/`: Functions to be used by `core` to get data from the DB.
- `redis/`: Redis stuffs.
  - `redis/helpers/`: Functions to be used by `core` to get data from Redis.
- `schemas/`: Response Pydantic models.
- `models/`: SQLAlchemy Core Tables.

### [Linting](scripts/lint.ps1)

[pylint](https://docs.pylint.org/en/latest/index.html) and [mypy](https://mypy.readthedocs.io/en/stable/) are used to lint the code. pylint's configuration and mypy's configuration are in [pyproject.toml](pyproject.toml).

### [Formatting](scripts/format.ps1)

[isort](https://pycqa.github.io/isort/) and [black](https://black.readthedocs.io/en/stable/) are used to format the code. isort's configuration is in [pyproject.toml](pyproject.toml) and black uses default settings.

```
isort app tests export scripts; black app tests export scripts
```

[prettier](https://prettier.io/docs/en/) is used to format the json files.

```
prettier --write tests/*/*.json
prettier --write export/*/Nice*.json
prettier --write export/*/*UserLevel.json --print-width 50
```

### Dependencies

Use [poetry](https://python-poetry.org/docs/) to manage the dependencies. Run `poetry export` after adding a production dependency.

```
poetry export -f requirements.txt -o requirements.txt
```

### [Testing](scripts/test.ps1)

Run pytest at project root to run the tests or use `coverage` to get coverage statistics.

```
coverage run --source=app/ -m pytest; coverage html
```

### Helper scripts

#### [`extract_enums.py`](scripts/extract_enums.py)

Take the `dump.cs` generated by [Il2CppDumper](https://github.com/Perfare/Il2CppDumper) and write the [`gameenums.py`](app/data/gameenums.py) file.

```
python scripts/extract_enums.py dump.cs_path app/schemas/gameenums.py
```

#### [`update_ce_translation.py`](scripts/update_ce_translation.py)

Update `equip_names.json` with new NA CEs translations. `--jp-master` and `--na-master` arguments are not needed if environment variables `JP_GAMEDATA` and `NA_GAMEDATA` are set, added to the `.env` file or set in `config.json`.

```
python scripts/update_ce_translation.py --jp-master jp_master_path --na-master na_master_path
```

#### [`load_rayshift_quest_list.py`](scripts/load_rayshift_quest_list.py)

Update the `rayshiftQuest` tables with the list of available quests from Rayshift. This script should be run periodically to update the `rayshiftQuest` list.

```
python -m scripts.load_rayshift_quest_list
```

#### [`get_test_data.py`](tests/get_test_data.py)

Run this script when the master data changed to update the tests or when new tests are added.

```
python -m tests.get_test_data --raw --nice --basic
```
