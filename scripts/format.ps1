ruff format
ruff check --fix

python ./scripts/format_json.py ./app/data/mappings ./tests/ ./export/*/Nice*.json ./export/BuffList.ActionList.json
