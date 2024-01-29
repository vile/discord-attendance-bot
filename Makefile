.PHONY: all deps start

all: deps start

deps:
	poetry config virtualenvs.in-project true
	poetry install --no-root

start :; $(VENV)/python3.10 main.py

include Makefile.venv