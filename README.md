List of environment variables required for the main app:
- `NA_GAMEDATA`
- `JP_GAMEDATA`

Run `uvicorn main:app --reload` to start.

Go to http://127.0.0.1:8000/docs or http://127.0.0.1:8000/redoc for the API documentation.

List of optional enviroment variables for the Docker image: https://github.com/tiangolo/uvicorn-gunicorn-docker#environment-variables
