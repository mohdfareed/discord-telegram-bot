# syntax=docker/dockerfile:1

FROM python:3.13-slim-alpine

WORKDIR /app

COPY bot ./bot
COPY scripts ./scripts
COPY pyproject.toml .
COPY poetry.lock .
COPY README.md .

VOLUME ["/app/data"]

ARG debug=false
ENV DEBUG=$debug

RUN scripts/install.sh
ENTRYPOINT [ "scripts/start.sh" ]
