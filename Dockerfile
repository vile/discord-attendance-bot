FROM gorialis/discord.py:3.10.10-alpine-pypi-minimal

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]