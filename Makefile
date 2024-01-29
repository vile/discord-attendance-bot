.PHONY: all deps start

all: deps start

deps :; poetry install --no-root

start :; $(VENV)/python3.10 main.py

include Makefile.venv