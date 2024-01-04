start :
	$(VENV)/python3 main.py

venv :
	python3 -m venv .venv

deps :
	$(VENV)/pip install -r requirements.txt 

include Makefile.venv