FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV
# OpenCV requires various system libraries for image processing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install Python dependencies
# Using Tsinghua mirror for faster download in China
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn

# Copy application code
COPY app/ /app/app/
COPY run.py /app/
COPY rapidocr_onnxruntime_run/ /app/rapidocr_onnxruntime_run/

# Create directories for logs and uploads
RUN mkdir -p /app/logs /app/uploads

# Copy entrypoint script
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Expose port (default 7850, can be overridden via OCR_PORT env var)
# Using ARG for build-time port configuration
ARG OCR_PORT=7850
EXPOSE ${OCR_PORT}

# Health check (uses OCR_PORT environment variable, default 7850)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD sh -c 'OCR_PORT=${OCR_PORT:-7850}; python -c "import requests; requests.get(\"http://localhost:${OCR_PORT}/health\", timeout=5)"' || exit 1

# Use entrypoint script to handle configurable port
ENTRYPOINT ["/app/docker-entrypoint.sh"]

