## FGO Game data API

List of environment variables for the main app. All are required except noted:
- `NA_GAMEDATA`: path to NA gamedata's master folder
- `JP_GAMEDATA`: path to JP gamedata's master folder
- `ASSET_URL`: Base URL for the game assets
- `EXPORT_ALL_NICE`: Optional, default to `False`. If set to `True`, at start the app will generate nice data of all servant and CE in both JP and NA and serve them at the `/export` endpoint. It's recommended to serve the files in the `/export` folder using nginx or equivalent webserver to lighten the load of the API server.

You can also make a .env file at the project root with the following entries instead of setting the environment variables:
```
NA_GAMEDATA="/path/to/gamedata/master/NA"
JP_GAMEDATA="/path/to/gamedata/master/JP"
ASSET_URL="https://example.com/assets/"
EXPORT_ALL_NICE=True
```

Run at the project root to start the API server:
```
uvicorn app.main:app --reload
```

Go to http://127.0.0.1:8000/docs or http://127.0.0.1:8000/redoc for the API documentation.

List of optional enviroment variables for the [Docker image](https://github.com/tiangolo/uvicorn-gunicorn-docker#environment-variables).
