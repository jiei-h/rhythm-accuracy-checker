FROM python:3.9-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD gunicorn --bind 0.0.0.0:$PORT --timeout 120 app:app