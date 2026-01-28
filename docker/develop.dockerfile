ARG PYTHON_VERSION=3.12.4
ARG VERSION

# Get uv.
FROM ghcr.io/astral-sh/uv:0.2.13 AS uv


# Base image to use for builder and final images.
FROM python:${PYTHON_VERSION}-slim-bookworm AS base

# Set environment varibles.
ENV DEBIAN_FRONTEND=noninteractive \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH

# Run OS upgrades.
RUN apt-get update -y -q \
    && apt-get upgrade -y -q \
    && apt-get clean -y -q \
    && rm -rf /var/lib/apt/lists/*


# Builder image.
FROM base AS builder

WORKDIR /root/app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=from=uv,source=/uv,target=./uv \
    ./uv pip install --system poetry==1.8.3 poetry-plugin-export==1.8.0 \
    && ./uv venv ${VIRTUAL_ENV}

COPY --link . .

ARG VERSION=0.0.0.dev0

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=from=uv,source=/uv,target=./uv \
    poetry export --format requirements.txt --output requirements.txt \
    && poetry version ${VERSION} \
    && ./uv pip install -r requirements.txt "exchange_calendar_service @ ." dumb-init==1.2.5.post1


FROM base AS final

EXPOSE 8000

# Add unpriviledged user.
RUN adduser --disabled-password app

USER app
WORKDIR /app

COPY --from=builder --link /opt/venv /opt/venv

ENTRYPOINT ["/opt/venv/bin/dumb-init", "--"]
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "--factory", "exchange_calendar_service.core.app:app"]
