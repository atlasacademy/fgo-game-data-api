## FGO Game data API

List of required environment variables for the main app:
- `NA_GAMEDATA`: path to NA gamedata's master folder
- `JP_GAMEDATA`: path to JP gamedata's master folder

or make a .env file at the project root with the following entries:
```
NA_GAMEDATA=""
JP_GAMEDATA=""
```

Run at the project root to start the API server:
```
uvicorn app.main:app --reload
```

Go to http://127.0.0.1:8000/docs or http://127.0.0.1:8000/redoc for the API documentation.

List of optional enviroment variables for the [Docker image](https://github.com/tiangolo/uvicorn-gunicorn-docker#environment-variables).
