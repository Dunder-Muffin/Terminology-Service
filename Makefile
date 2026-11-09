install:
	pip install -r requirements-dev.txt
	pre-commit install

migrate:
	python manage.py migrate

run:
	python manage.py runserver

test:
	pytest

lint:
	ruff check .
	ruff format --check .
