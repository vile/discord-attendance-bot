start :
	$(VENV)/python3 main.py

deps :
	$(VENV)/pip install -r requirements.txt 

include Makefile.venv