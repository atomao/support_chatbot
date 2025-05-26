docker run -d --name mysql   -e MYSQL_ROOT_PASSWORD=123456   -e MYSQL_DATABASE=flaskshop   -p 3306:3306   mysql:9.3   --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
