FROM python:3.11-slim

WORKDIR /app

# Install system utilities (git, curl, build-essential for terminal execution tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Default command starts the CLI
ENTRYPOINT ["python", "-m", "cli.main"]
