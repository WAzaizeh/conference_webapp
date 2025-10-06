FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
ENV PYTHONUNBUFFERED=True

WORKDIR /app

ENV HOST=0.0.0.0

COPY pyproject.toml .

RUN uv sync

COPY app/ .

CMD ["uv", "run", "python", "main.py"]