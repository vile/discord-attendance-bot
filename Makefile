venv :
	python3.10 -m venv .venv

deps :
	$(VENV)/pip install -r requirements.txt 

start :
	$(VENV)/python3.10 main.py

include Makefile.venv