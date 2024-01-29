FROM gorialis/discord.py:3.10.10-alpine-pypi-minimal

WORKDIR /app

RUN pip install poetry

# Copy Poetry files
COPY pyproject.toml ./
COPY poetry.lock ./

RUN poetry install --no-root --no-cache

COPY . .

# Start bot with Poetry (venv)
CMD ["poetry", "run", "python3", "main.py"]