FROM tiangolo/uvicorn-gunicorn:python3.8

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV NA_GAMEDATA="" \
    JP_GAMEDATA="" \
    ASSET_URL="https://assets.atlasacademy.io/GameData/" \
    EXPORT_ALL_NICE="false"
