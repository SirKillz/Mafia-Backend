# Build the containers
build:
	docker compose -f ./docker/docker-compose.yml build

# Run the containers
up:
	docker compose -f ./docker/docker-compose.yml up -d

# Stop and tear down the containers
down:
	docker compose -f ./docker/docker-compose.yml down

# Connect to the Database container
connect-db:
	docker exec -it database mysql -u root -p