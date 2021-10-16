isort app tests export scripts
black app tests export scripts

prettier --tab-width 2 --write app/data/mappings
prettier --tab-width 2 --write tests/*/*.json
prettier --tab-width 2 --write export/*/Nice*.json
prettier --tab-width 2 --write export/*/*UserLevel.json --print-width 50