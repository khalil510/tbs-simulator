# TBS monorepo task runner. `make help` for the list.

.PHONY: help dev-up dev-down backend-test backend-shell frontend-install frontend-start frontend-build migrate schema-check

help:
	@echo "Targets:"
	@echo "  dev-up            start the full stack (db, redis, minio, backend, worker, frontend)"
	@echo "  dev-down          stop and remove the stack"
	@echo "  backend-test      run backend tests without Docker (sqlite GIS fallback)"
	@echo "  migrate           apply database migrations inside the backend container"
	@echo "  frontend-install  npm ci in frontend/"
	@echo "  frontend-start    ng serve with /api proxy to :8000"
	@echo "  frontend-build    production build"

dev-up:
	docker compose up --build

dev-down:
	docker compose down

backend-test:
	cd backend && TBS_DB_ENGINE=sqlite TBS_BUNDLED_GIS=1 .venv/bin/python -m pytest -q || \
	(TBS_DB_ENGINE=sqlite TBS_BUNDLED_GIS=1 python -m pytest -q)

migrate:
	docker compose exec backend python manage.py migrate

frontend-install:
	cd frontend && npm ci

frontend-start:
	cd frontend && npm start

frontend-build:
	cd frontend && npm run build

schema-check:
	node -e "JSON.parse(require('fs').readFileSync('schemas/scenario.schema.json')); JSON.parse(require('fs').readFileSync('schemas/aar-event.schema.json')); console.log('schemas OK')"
