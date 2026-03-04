# Psi Chi Omega Backend (FastAPI)

## Run (local)
- Copy env: \`cp .env.example .env\`
- Start DB: \`docker compose up -d db\`
- Install deps: \`uv sync\`
- Run API: \`uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000\`

## Run (docker)
\`docker compose up --build\`
