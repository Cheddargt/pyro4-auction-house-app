.PHONY: install run

install:
	pip install -r requirements.txt

run:
	python -m Pyro4.naming
	python auction_house.py
	python interface.py
	python interface.py