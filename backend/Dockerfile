# Use official Python slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Cloud Run injects $PORT at runtime (default 8080).
# We expose 8080 as documentation, but the CMD honours $PORT dynamically.
EXPOSE 8080

# Use shell form so $PORT is expanded at runtime
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
