FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev
COPY src ./src
RUN uv sync --frozen --no-dev

FROM python:3.13-slim-bookworm
RUN useradd --create-home app
WORKDIR /app
COPY --from=builder /app/.venv ./.venv
COPY content ./content
COPY static ./static
ENV PATH="/app/.venv/bin:$PATH"
USER app
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-", "fraoverstebenk.app:create_app()"]
