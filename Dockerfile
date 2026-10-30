FROM python:3.13-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY run_server.py ./run_server.py

RUN pip install --no-cache-dir .

ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["python", "run_server.py"]
