##### DEPENDENCIES

FROM python:3.10-alpine3.19 AS deps

WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin"

# Copy Poetry files
COPY pyproject.toml ./
COPY poetry.lock ./

RUN apk add build-base libffi-dev bash pipx --no-cache && \
    pipx install poetry && \
    poetry config virtualenvs.in-project true && \
    poetry install --no-root --no-cache

##### RUNNER

FROM python:3.10-alpine3.19 AS runner

WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin"

RUN apk add pipx --no-cache && \
    pipx install poetry

COPY --from=deps /app/.venv ./.venv
COPY . .

# Start bot with Poetry (venv)
CMD ["poetry", "run", "python3", "main.py"]