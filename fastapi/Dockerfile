FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including gcc for building
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .

# upgrade pip to latest
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt


# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 fastapi-user
USER fastapi-user

EXPOSE 8080

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8080", "main:app"]
