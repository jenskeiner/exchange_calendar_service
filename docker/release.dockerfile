ARG PYTHON_VERSION=3.12.4
ARG VERSION

# Get uv.
FROM ghcr.io/astral-sh/uv:0.2.13 AS uv

# Builder image.
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

# Set environment varibles.
ENV DEBIAN_FRONTEND=noninteractive \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=from=uv,source=/uv,target=./uv \
    ./uv venv ${VIRTUAL_ENV} \
    && ./uv pip install exchange-calendar-service[server]==${VERSION}


FROM python:${PYTHON_VERSION}-slim-bookworm AS final

# Set environment varibles.
ENV DEBIAN_FRONTEND=noninteractive \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH

EXPOSE 8000

# Add unpriviledged user.
RUN apt-get update -y -q \
    && apt-get upgrade -y -q \
    && adduser --disabled-password app

USER app
WORKDIR /app

COPY --from=builder --link /opt/venv /opt/venv

ENTRYPOINT ["/opt/venv/bin/dumb-init", "--"]
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "--factory", "exchange_calendar_service.core.app:app"]
