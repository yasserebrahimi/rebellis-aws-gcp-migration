SHELL := /bin/bash
PROJECT ?= rebellis
ENV ?= development

.PHONY: fmt lint test build up down logs

fmt:
	ruff check --fix src tests || true
	black src tests || true
	isort src tests || true

lint:
	ruff check src tests
	black --check src tests
	isort --check-only src tests
	mypy src

test:
	pytest -q

build:
	docker build -t $(PROJECT)-api:dev .

up:
	docker compose -f docker-compose.yml -f docker-compose.$(ENV).yml up -d --build

down:
	docker compose -f docker-compose.yml -f docker-compose.$(ENV).yml down

logs:
	docker compose logs -f --tail=200
