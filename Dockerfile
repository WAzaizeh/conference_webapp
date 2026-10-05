FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
ENV PYTHONUNBUFFERED=True

WORKDIR /app

ENV HOST=0.0.0.0

# Install the exact versions from uv.lock so builds are reproducible
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY app/ .

CMD ["uv", "run", "--frozen", "python", "main.py"]