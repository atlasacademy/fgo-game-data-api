FROM tiangolo/uvicorn-gunicorn:python3.8

COPY ./app /app/app

RUN pip install --no-cache-dir -r requirements.txt
