## FGO Game data API

List of environment variables for the main app. All are required except noted:
- `NA_GAMEDATA`: path to NA gamedata's master folder
- `JP_GAMEDATA`: path to JP gamedata's master folder
- `ASSET_URL`: Base URL for the game assets
- `EXPORT_ALL_NICE`: Optional, default to `False`. If set to `True`, at start the app will generate nice data of all servant and CE in both JP and NA and serve them at the `/export` endpoint. It's recommended to serve the files in the `/export` folder using nginx or equivalent webserver to lighten the load of the API server.
- `DOCUMENTATION_ALL_NICE`: Optional, default to `False`. If set to `True`, there will be links to the exported all nice files in the documentation.
- `NICE_SERVANT_LRU_CACHE`: Optional, default to `False`. If set to `True`, use [lru_cache](https://docs.python.org/3/library/functools.html#functools.lru_cache) for get nice servant.
- `GITHUB_WEBHOOK_SECRET`: Optional, default to `""`. If set, will add a webhook location at `/GITHUB_WEBHOOK_SECRET/update` that will pull and update the game data. If it's not set, the endpoint is not activated.
- `GITHUB_WEBHOOK_SLEEP`: Optional, default to `0`. If set, will delay the action above by `GITHUB_WEBHOOK_SLEEP` seconds.

You can also make a .env file at the project root with the following entries instead of setting the environment variables:
```
NA_GAMEDATA="/path/to/gamedata/master/NA"
JP_GAMEDATA="/path/to/gamedata/master/JP"
ASSET_URL="https://example.com/assets/"
EXPORT_ALL_NICE=False
DOCUMENTATION_ALL_NICE=True
NICE_SERVANT_LRU_CACHE=False
GITHUB_WEBHOOK_SECRET="e81c7b97-9a57-4424-a887-149b4b5adf57"
GITHUB_WEBHOOK_SLEEP=0
```

Run at the project root to start the API server:
```
uvicorn app.main:app --reload --log-level debug --reload-dir app
```

Go to http://127.0.0.1:8000/docs or http://127.0.0.1:8000/redoc for the API documentation.

List of optional enviroment variables for the [Docker image](https://github.com/tiangolo/uvicorn-gunicorn-docker#environment-variables).
