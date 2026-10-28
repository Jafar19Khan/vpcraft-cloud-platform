.PHONY: test run up down logs infra-fmt infra-validate

test:
	python -m unittest discover -s tests -v

run:
	gunicorn --bind 127.0.0.1:8000 app.wsgi:app

up:
	docker compose up --build -d

down:
	docker compose down

infra-fmt:
	terraform -chdir=infra fmt -recursive

infra-validate:
	terraform -chdir=infra init -backend=false
	terraform -chdir=infra validate
logs:
	docker compose logs -f
