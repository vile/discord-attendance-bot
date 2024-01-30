.PHONY: all deps start dockerup dockerdown

all: deps start

deps:
	poetry config virtualenvs.in-project true
	poetry install --no-root

start :; poetry run python3 main.py

dockerup-build :; docker compose up --build --remove-orphans

dockerup :; docker compose up

dockerdown :; docker compose down --remove-orphans