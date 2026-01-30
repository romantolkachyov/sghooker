FROM ghcr.io/gitguardian/wolfi/python:3.13-dev AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV VENV_PATH=/app/.venv

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv venv --python=/usr/bin/python && \
    uv sync --frozen --no-install-project --no-dev --python $VENV_PATH/bin/python

COPY --exclude=.venv . /app/

FROM ghcr.io/gitguardian/wolfi/python:3.13

WORKDIR /app

COPY --from=builder /app/ /app/

ENV PYTHONPATH="/app/:/app/.venv/lib/python3.13/site-packages/"

USER nonroot
EXPOSE 8000

ENTRYPOINT [ "/app/.venv/bin/granian", "--interface", "rsgi", "--host", "0.0.0.0", "sghooker.main:app" ]
