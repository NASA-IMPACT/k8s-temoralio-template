# Dockerfile for Temporal Worker
FROM python:3.12-slim-bookworm

COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/
# Set working directory
WORKDIR /app
COPY pyproject.toml .

# Install dependencies
RUN uv sync

# Copy worker code
COPY main.py .

# ENV TASK_QUEUE=fibonnacci-queue TEMPORAL_SERVER_URL=localhost:7233
# Run the worker
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
