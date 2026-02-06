FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies for mysqlclient
RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN addgroup --system appgroup && adduser --system --group appuser

# Set work directory
WORKDIR /app

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Make entrypoint executable and chown
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh && chown -R appuser:appgroup /app

# Expose port
EXPOSE 8000

# Switch to non-root user
USER appuser

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
