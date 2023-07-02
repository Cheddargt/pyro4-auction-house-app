.PHONY: install run

install:
	pip install -r requirements.txt

run:
	python -m Pyro5.nameserver
	python auction_house.py
	python interface.py
	python interface.py