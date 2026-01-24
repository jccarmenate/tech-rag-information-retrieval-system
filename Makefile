.PHONY: install run test lint format

install:
	cd backend && python -m venv .venv && .venv/bin/pip install -e ".[dev]"

run:
	cd backend && .venv/bin/uvicorn app.main:app --reload

test:
	cd backend && .venv/bin/pytest

lint:
	cd backend && .venv/bin/ruff check .

format:
	cd backend && .venv/bin/ruff format .
