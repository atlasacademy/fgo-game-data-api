# FGO game data API <!-- omit in toc -->

HTTP API for FGO game data. Transform the raw game data into something a bit more manageable.

- [Environment variables](#environment-variables)
  - [Required environment variables](#required-environment-variables)
  - [Optional environment variables](#optional-environment-variables)
  - [Secrets](#secrets)
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

#### Required environment variables
- `NA_GAMEDATA`: path to NA gamedata's folder that contains the `master` and `ScriptActionEncrypt` folders.
- `JP_GAMEDATA`: path to JP gamedata's folder that contains the `master` and `ScriptActionEncrypt` folders.
- `NA_POSTGRESDSN`: PostgreSQL DSN to a database for NA.
- `JP_POSTGRESDSN`: PostgreSQL DSN to a database for JP.
- `REDISDSN`: Redis DSN to a Redis server for caching.

#### Optional environment variables
- `ASSET_URL`: defaults to https://assets.atlasacademy.io/GameData/. Base URL for the game assets.
- `RAYSHIFT_API_KEY`: default to `""`. Rayshift.io API key to pull quest data.
- `RAYSHIFT_API_URL`: default to https://rayshift.io/api/v1/. Rayshift.io API URL.
- `QUEST_CACHE_LENGTH`: default to `3600`. How long to cache the quest and war endpoints in seconds. Because the rayshift data is updated continously, web and quest endpoints have lower cache time.
- `WRITE_POSTGRES_DATA`: default to `True`. Overwrite the data in PostgreSQL when importing.
- `OPENAPI_URL`: default to `None`. Set the server URL in the openapi schema export.
- `EXPORT_ALL_NICE`: default to `False`. If set to `True`, at start the app will generate nice data of all servant and CE and serve them at the `/export` endpoint. It's recommended to serve the files in the `/export` folder using nginx or equivalent webserver to lighten the load on the API server.
- `DOCUMENTATION_ALL_NICE`: default to `False`. If set to `True`, there will be links to the exported all nice files in the documentation.
- `GITHUB_WEBHOOK_SECRET`: default to `""`. If set, will add a webhook location at `/GITHUB_WEBHOOK_SECRET/update` that will pull and update the game data. If it's not set, the endpoint is not created.
- `GITHUB_WEBHOOK_GIT_PULL`: default to `False`. If set, the app will do `git pull` on the gamedata repos when the webhook above is used.
- `GITHUB_WEBHOOK_SLEEP`: default to `0`. If set, will delay the action above by `GITHUB_WEBHOOK_SLEEP` seconds.
- `BLOOM_SHARD`: default to `0`. [Bloom](https://github.com/valeriansaliou/bloom) shard that is used for caching.
- `REDIS_PREFIX`: default to `fgoapi`. Prefix for redis keys.

You can also make a .env file at the project root with the following entries instead of setting the environment variables:

```
NA_GAMEDATA="/path/to/gamedata/NA"
JP_GAMEDATA="/path/to/gamedata/JP"
NA_POSTGRESDSN="postgresql://username:password@localhost:5432/fgoapiNA"
JP_POSTGRESDSN="postgresql://username:password@localhost:5432/fgoapiJP"
REDISDSN="redis://localhost:6379/0"
RAYSHIFT_API_KEY="eca334a9-3289-4ad7-9b92-1ec2bbc3fc19"
QUEST_CACHE_LENGTH=3600
WRITE_POSTGRES_DATA=True
ASSET_URL="https://example.com/assets/"
OPENAPI_URL="https://api.atlasacademy.io"
EXPORT_ALL_NICE=False
DOCUMENTATION_ALL_NICE=True
GITHUB_WEBHOOK_SECRET="e81c7b97-9a57-4424-a887-149b4b5adf57"
GITHUB_WEBHOOK_GIT_PULL=True
GITHUB_WEBHOOK_SLEEP=0
BLOOM_SHARD=0
REDIS_PREFIX="fgoapi
```

#### Secrets

Secret variables can also be put in the `secrets` folder instead of being supplied as environment variable:
```
> cat .\secrets\JP_POSTGRESDSN
postgresql://username:password@localhost:5432/fgoapiJP
> cat .\secrets\NA_POSTGRESDSN
postgresql://username:password@localhost:5432/fgoapiNA
> cat .\secrets\RAYSHIFT_API_KEY
eca334a9-3289-4ad7-9b92-1ec2bbc3fc19
> cat .\secrets\GITHUB_WEBHOOK_SECRET
e81c7b97-9a57-4424-a887-149b4b5adf57
> cat .\secrets\REDISDSN
redis://localhost
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

Go to http://127.0.0.1:8000/docs or http://127.0.0.1:8000/redoc for the API documentation.

### Architecture

- `main.py`: Main entrypoint of the application.
- `routers/`: Routers to deal with incoming requests. The routers call functions from `core` to get the response data.
- `core/`: Build response data. Get raw data from either `db/helpers/` or the `masters` object in `data/gamedata`.
- `data/`: Import master data and translations data into memory.
  - `data/gamedata.py`: has the `masters` object containing some master data as Pydantic objects. The `masters` object is used for frequently accessed master data.
- `db/`: DB stuffs.
  - `db/helpers/`: Functions to be used by `core` to get data from the DB.
- `schemas/`: Response Pydantic models.
- `models/`: SQLAlchemy Core Tables.

### [Linting](scripts/lint.ps1)

[pylint](https://docs.pylint.org/en/latest/index.html) and [mypy](https://mypy.readthedocs.io/en/stable/) are used to lint the code. pylint's configuration is in [pyproject.toml](pyproject.toml#L39) and mypy's configuration is in [mypy.ini](mypy.ini).

### [Formatting](scripts/format.ps1)

[isort](https://pycqa.github.io/isort/) and [black](https://black.readthedocs.io/en/stable/) are used to format the code. isort's configuration is in [pyproject.toml](pyproject.toml#L30) and black uses default settings.

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

Update `equip_names.json` with new NA CEs translations. `--jp-master` and `--na-master` arguments are not needed if environment variables `JP_GAMEDATA` and `NA_GAMEDATA` are set or added to the `.env` file.

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