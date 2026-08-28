# Docker Hub is unreliable from the production server; this mirror was
# verified there with `docker pull docker.m.daocloud.io/library/python:3.13-slim`.
FROM docker.m.daocloud.io/library/python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple \
    PIP_DEFAULT_TIMEOUT=60 \
    PIP_RETRIES=5 \
    UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple

# The production host cannot reliably reach PyPI.  Use the Alibaba Cloud mirror
# for both bootstrapping uv and resolving the locked application dependencies.
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY src ./src

EXPOSE 8001

CMD ["uv", "run", "--no-sync", "python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8001"]
