# Build the containers
build:
	docker compose --env-file .env.dev -f ./docker/docker-compose.yml build

# Run the containers
up:
	docker compose --env-file .env.dev -f ./docker/docker-compose.yml up --build -d

# Stop and tear down the containers
down:
	docker compose --env-file .env.dev -f ./docker/docker-compose.yml down

# Connect to the Database container
connect-db:
	docker compose --env-file .env.dev -f ./docker/docker-compose.yml exec mafia-db psql

dump-db:
	docker compose --env-file .env.dev -f ./docker/docker-compose.yml exec -T mafia-db pg_dump > dump.sql



