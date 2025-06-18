# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install redis

CMD ["python", "host.py"]  # This gets overridden per container in docker-compose.yml
