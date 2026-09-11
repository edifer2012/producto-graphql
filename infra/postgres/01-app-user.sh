#!/bin/sh
set -eu
# El usuario que usa la API NO es el superusuario de PostgreSQL.
# Las variables SQL se interpolan como identificadores/literales, no como SQL crudo.
psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  --set=ON_ERROR_STOP=1 --set=app_user="$APP_DB_USER" \
  --set=app_password="$APP_DB_PASSWORD" --set=db_name="$POSTGRES_DB" <<'SQL'
SELECT format('CREATE ROLE %I LOGIN PASSWORD %L NOSUPERUSER NOCREATEDB NOCREATEROLE', :'app_user', :'app_password') \gexec
GRANT CONNECT ON DATABASE :"db_name" TO :"app_user";
ALTER SCHEMA public OWNER TO :"app_user";
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
SQL
