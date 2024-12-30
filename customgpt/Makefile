init:
	make install && make pre-commit

install:
	poetry install

pre-commit:
	poetry run pre-commit install --config pre-commit.yaml

lint:
	poetry run ruff check app/

format:
	poetry run ruff format app/