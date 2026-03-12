BACKEND_DIR := pco_backend
FRONTEND_DIR := pco_website

.PHONY: test test-backend test-frontend test-e2e

test: test-backend test-frontend test-e2e

test-backend:
	cd $(BACKEND_DIR) && uv run pytest

test-frontend:
	cd $(FRONTEND_DIR) && pnpm test

test-e2e:
	cd $(FRONTEND_DIR) && pnpm test:e2e

.PHONY: docker-build docker-up docker-down

docker-build:
	cd $(FRONTEND_DIR) && docker compose build

docker-up:
	cd $(FRONTEND_DIR) && docker compose up -d

docker-down:
	cd $(FRONTEND_DIR) && docker compose down
