FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src

# uv uses the committed lockfile to create a reproducible production environment.
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY src ./src

EXPOSE 8001

CMD ["uv", "run", "--no-sync", "python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8001"]
