FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy application code (not mounted, actually copied)
COPY app/ ./app/

# Set environment variables
ENV ENVIRONMENT=production
ENV PORT=8080
ENV HOST=0.0.0.0

# Expose port
EXPOSE 8080

# Run the application
WORKDIR /app/app
CMD ["uv", "run", "--directory", "/app/app", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]