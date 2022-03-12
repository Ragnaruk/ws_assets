pretty:
	isort ws_assets alembic tests --profile black
	black ws_assets alembic tests
	mypy ws_assets alembic tests

req:
	pip install -r requirements.txt
	pip install -r requirements.dev.txt

up: pretty
	docker-compose up -d --remove-orphans

upb: pretty
	docker-compose up -d --build --remove-orphans

stop:
	docker-compose stop

down:
	docker-compose down