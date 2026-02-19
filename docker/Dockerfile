ARG PYTHON_VERSION=3.14.2

FROM dhi.io/python:${PYTHON_VERSION}-alpine3.22-dev AS python-builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev


FROM dhi.io/python:${PYTHON_VERSION}-alpine3.22 AS prod

# Copy the application from the builder
COPY --from=python-builder --chown=nonroot:nonroot /app/.venv /app/.venv
COPY --from=python-builder --chown=nonroot:nonroot /app/src /app/src

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Use `/app` as the working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

# Expose the service port
EXPOSE 8080

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8080", "--factory", "exchange_calendar_service.app:get_app"]
