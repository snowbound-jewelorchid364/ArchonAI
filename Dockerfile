FROM python:3.11-slim AS base

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
RUN pip install --no-cache-dir uv

# Copy dependency spec first (cache layer)
COPY pyproject.toml ./
RUN uv pip install --system -e ".[prod]" 2>/dev/null || uv pip install --system -e .

# Copy source
COPY src/ src/
COPY main.py .
COPY prompts/ prompts/
COPY .env.example .env.example

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# Default: run API server
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
