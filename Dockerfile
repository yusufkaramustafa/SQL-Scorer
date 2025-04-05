FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies first
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create data directory
RUN mkdir -p /app/data

# Copy project files
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV DB_PATH=/app/data/test.db

# Command to run the application
ENTRYPOINT ["python", "main.py"]