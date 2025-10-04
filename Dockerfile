FROM python:3.12.4-slim
ENV PYTHONUNBUFFERED=True

WORKDIR /app

ENV HOST=0.0.0.0

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

CMD ["python", "main.py"]