##### DEPENDENCIES (TOOLS)

FROM python:3.10-alpine3.19 AS deps-tools
ENV PATH="${PATH}:/root/.local/bin"

RUN apk add build-base libffi-dev bash pipx --no-cache && \
    pipx install poetry

##### DEPENDENCIES (ENV)

FROM deps-tools AS deps-env

# Copy Poetry package files
COPY pyproject.toml ./
COPY poetry.lock ./

RUN poetry config virtualenvs.in-project true && \
    poetry install --no-root --no-cache

#### RUNNER (TOOLS)

FROM python:3.10-alpine3.19 AS runner-tools
ENV PATH="${PATH}:/root/.local/bin"

RUN apk add pipx --no-cache && \
    pipx install poetry

##### RUNNER (FINAL)

FROM runner-tools AS runner

WORKDIR /app
COPY --from=deps-env ./.venv ./.venv
COPY . .

# Start bot with Poetry (venv)
CMD ["poetry", "run", "python3", "main.py"]