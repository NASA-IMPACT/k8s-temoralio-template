# Dockerfile for Temporal Worker
FROM python:3.12-slim-bookworm

COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app
COPY pyproject.toml .

# Install dependencies
RUN uv sync


COPY entrypoint.sh .

# Copy worker code
COPY *.py .

# ENV TASK_QUEUE=fibonnacci-queue TEMPORAL_SERVER_URL=localhost:7233

# Run the worker
CMD ["bash", "entrypoint.sh"]
