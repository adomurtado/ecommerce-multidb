FROM python:3.12-slim

WORKDIR /app

# Install dep
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua app ke /app (tapi akan di-override kalau pakai volume)
COPY app /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
