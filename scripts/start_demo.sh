#!/bin/bash


docker run --rm -p 5432:5432 --name chai-store -e POSTGRES_PASSWORD=admin -d postgres:latest
sleep 3
docker exec -i chai-store env PGPASSWORD=admin psql -U postgres -d postgres < schema.sql

# start valkey server for storing chat messages
docker run --rm -p 6379:6379 --name chai-chatstore -d valkey/valkey:latest

# start the app
uv run uvicorn app.main:app --reload