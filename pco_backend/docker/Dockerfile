FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml uv.lock /app/

RUN pip install --no-cache-dir uv && uv venv && uv sync --frozen --no-dev

COPY app /app/app
COPY alembic /app/alembic
EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
