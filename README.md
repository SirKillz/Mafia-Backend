# Mafia Backend

## Local development

Create `.env.dev` from `.env.dev.example` and set an API key and database password. From the repository root, run:

```sh
docker compose --env-file .env.dev -f docker/docker-compose.yml up --build -d
```

The Compose project is named `mafia-backend`, with services `mafia-backend-api` and `mafia-db`. The API listens on `http://localhost:8000` and Postgres on `localhost:5432`. The API connects to the database service using `DATABASE_HOST=mafia-db`. Check the API with `curl -H "X-API-Key: <your API_KEY>" http://localhost:8000/test`. The Postgres init script creates tables and seed data only when the `postgres_data` volume is first created. To stop the stack, run `docker compose --env-file .env.dev -f docker/docker-compose.yml down`.

`make up`, `make down`, `make connect-db`, and `make dump-db` use the same Compose configuration.

## Database configuration

The backend reads `DATABASE_USERNAME`, `DATABASE_PASSWORD`, `DATABASE_HOST`, `DATABASE_PORT`, and `DATABASE_NAME`. `DATABASE_PORT` defaults to `5432`. Set optional `DATABASE_SSLMODE=require` when the production Postgres service requires TLS. For a migrated production database, point these variables at the existing Postgres instance. The production schema must have the tables and identity sequences expected by the SQLAlchemy models; the local init script is only for fresh local volumes.

Keep `API_KEY` and `ALLOWED_CORS` set for the API. The old `MYSQL_*` variables are no longer used. `.env.dev` and `.env.prod` are ignored by Git, so update the deployed production environment separately.

Hosted on Neon Postgres