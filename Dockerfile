FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install --no-cache-dir -e .

ENV PORT=8000
EXPOSE ${PORT}

CMD uvicorn agronom_agent.api.routes:app --host 0.0.0.0 --port ${PORT}
