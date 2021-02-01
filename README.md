# FGO game data API <!-- omit in toc -->

HTTP API for FGO game data. Transform the raw game data into something a bit more manageable.

- [Environment variables](#environment-variables)
  - [Required environment variables](#required-environment-variables)
  - [Optional environment variables](#optional-environment-variables)
- [Run the API server](#run-the-api-server)
- [Linting](#linting)
- [Formatting](#formatting)
- [Dependencies](#dependencies)
- [Testing](#testing)
- [Helper scripts](#helper-scripts)
  - [`extract_enums.py`](#extract_enumspy)
  - [`update_ce_translation.py`](#update_ce_translationpy)
  - [`get_test_data.py`](#get_test_datapy)

### Environment variables

List of environment variables for the main app. All are required except noted:

#### Required environment variables
- `NA_GAMEDATA`: path to NA gamedata's master folder.
- `JP_GAMEDATA`: path to JP gamedata's master folder.
- `NA_POSTGRESDSN`: DSN to PostgreSQL database for NA.
- `JP_POSTGRESDSN`: DSN to PostgreSQL database for JP.
- `ASSET_URL`: base URL for the game assets.

#### Optional environment variables
- `WRITE_POSTGRES_DATA`: default to `True`. Overwrite the data in PostgreSQL when importing.
- `OPENAPI_URL`: default to `None`. Set the server URL in the openapi schema export.
- `EXPORT_ALL_NICE`: default to `False`. If set to `True`, at start the app will generate nice data of all servant and CE and serve them at the `/export` endpoint. It's recommended to serve the files in the `/export` folder using nginx or equivalent webserver to lighten the load on the API server.
- `DOCUMENTATION_ALL_NICE`: default to `False`. If set to `True`, there will be links to the exported all nice files in the documentation.
- `GITHUB_WEBHOOK_SECRET`: default to `""`. If set, will add a webhook location at `/GITHUB_WEBHOOK_SECRET/update` that will pull and update the game data. If it's not set, the endpoint is not created.
- `GITHUB_WEBHOOK_GIT_PULL`: default to `False`. If set, the app will do `git pull` on the gamedata repos when the webhook above is used.
- `GITHUB_WEBHOOK_SLEEP`: default to `0`. If set, will delay the action above by `GITHUB_WEBHOOK_SLEEP` seconds.
- `BLOOM_SHARD`: default to `0`. [Bloom](https://github.com/valeriansaliou/bloom) shard that is used for caching.
- `REDIS_HOST`: default to `None`. Redis host for Bloom. If set, will clear the Bloom cache when gamedata is updated.
- `REDIS_PORT`: default to `6379`. Redis port for Bloom.
- `REDIS_DB`: default to `0`. Redis DB for Bloom.

You can also make a .env file at the project root with the following entries instead of setting the environment variables:

```
NA_GAMEDATA="/path/to/gamedata/master/NA"
JP_GAMEDATA="/path/to/gamedata/master/JP"
NA_POSTGRESDSN="postgresql://username:password@localhost:5432/fgoapiNA"
JP_POSTGRESDSN="postgresql://username:password@localhost:5432/fgoapiJP"
WRITE_POSTGRES_DATA=True
ASSET_URL="https://example.com/assets/"
OPENAPI_URL="https://api.atlasacademy.io"
EXPORT_ALL_NICE=False
DOCUMENTATION_ALL_NICE=True
GITHUB_WEBHOOK_SECRET="e81c7b97-9a57-4424-a887-149b4b5adf57"
GITHUB_WEBHOOK_GIT_PULL=True
GITHUB_WEBHOOK_SLEEP=0
BLOOM_SHARD=0
REDIS_HOST="localhost"
REDIS_PORT=6379
REDIS_DB=0
```

List of optional enviroment variables for the Docker image can be found [here](https://github.com/tiangolo/uvicorn-gunicorn-docker#environment-variables).

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

#### [`get_test_data.py`](tests/get_test_data.py)

Run this script when the master data changed to update the tests or when new tests are added.

```
python -m tests.get_test_data --raw --nice --basic
```