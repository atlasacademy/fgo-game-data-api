Remove-Item rayshift_quest_jp.sql
Remove-Item rayshift_quest_na.sql
Remove-Item rayshiftQuest.zip
docker-compose exec -it pg-fgoapijp pg_dump --username=user --password --if-exists --clean --table='"rayshiftQuest"' --file=rayshift_quest_jp.sql fgoapijp
docker-compose exec -it pg-fgoapina pg_dump --username=user --password --if-exists --clean --table='"rayshiftQuest"' --file=rayshift_quest_na.sql fgoapina
docker-compose cp pg-fgoapijp:rayshift_quest_jp.sql ./
docker-compose cp pg-fgoapina:rayshift_quest_na.sql ./
$compress = @{
    Path             = "rayshift_quest_jp.sql", "rayshift_quest_na.sql"
    CompressionLevel = "Optimal"
    DestinationPath  = "rayshiftQuest.zip"
}
Compress-Archive @compress
Remove-Item rayshift_quest_jp.sql
Remove-Item rayshift_quest_na.sql
