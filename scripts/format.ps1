isort app tests export scripts
black app tests export scripts

prettier --write tests/*/*.json
prettier --write export/*/Nice*.json
prettier --write export/*/*UserLevel.json --print-width 50