FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Install dependencies first for better layer caching
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-install-project

# Copy application code
COPY . .
RUN uv sync --no-dev

EXPOSE 8123

CMD ["uv", "run", "langgraph", "dev", "--host", "0.0.0.0", "--port", "8123"]
