# these will speed up builds, for docker-compose >= 1.25
SHELL := /bin/bash

export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

all: down test

setup-python-env: setup-venv activate-venv install-deps

build-docker:
	docker compose build

up-docker:
	docker compose up -d --force-recreate --renew-anon-volumes

up-local:
	python3 src/main.py -c ./configs/development.yaml

up-docker-debug:
	docker compose -f ./docker-compose.debug.yml up -d

up-pytest-infra:
	docker compose -f ./docker-compose.pytest.yml up -d

down:
	docker-compose down --remove-orphans

prune:
	docker system prune -f
	


lint:
	flake8 --exclude=.tox,*.egg,venv,.venv,build,data --ignore=W291,E303,E501 --select=E,W,F  .

code-coverage:
	MONGODB_HOST=localhost && pytest -vv --junitxml=unittestresults.xml --cov --cov-report=term-missing

ci-code-coverage: local-install
	pytest -vv --cov --cov-report=term-missing

logs:
	docker-compose logs --tail=25 

pkg-clean: 
	rm -Rf ./build; rm -Rf ./dist; rm -Rf ./.tox; rm -Rf ./.eggs; rm -Rf ./.pytest_cache; rm -Rf ./**/*.egg-info; rm -Rf ./**/version.py; rm -Rf ./**/__pycache__; rm -Rf ./**/**/__pycache__; rm -Rf ./htmlcov; rm -Rf ./.coverage; rm -Rf ./*.xml; 

local-install: pkg-clean
	pip3 install -e .

clean-venv:
	rm -Rf .venv

setup-venv:
	python3 -m venv .venv

activate-venv:
	pwd && source .venv/bin/activate

install-deps:
	pip3 install --upgrade pip && pip3 install -r requirements.txt 
