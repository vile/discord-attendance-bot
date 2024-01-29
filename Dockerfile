FROM python:3.10-alpine3.19

WORKDIR /app

# Copy Poetry files
COPY pyproject.toml ./
COPY poetry.lock ./

ENV PATH="${PATH}:/root/.local/bin"

RUN apk add build-base libffi-dev bash pipx --no-cache && \
    pipx install poetry && \
    pipx ensurepath && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-cache

COPY . .

# Start bot with Poetry (venv)
CMD ["poetry", "run", "python3", "main.py"]