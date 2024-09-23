FROM python:3.12.4-slim
ENV PYTHONUNBUFFERED True

WORKDIR /app

ENV HOST 0.0.0.0

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "8000"]