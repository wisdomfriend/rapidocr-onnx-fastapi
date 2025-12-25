#!/bin/bash
# Docker entrypoint script - allows configurable port

# Get port from environment variable, default to 7850
OCR_PORT=${OCR_PORT:-7850}

# Start gunicorn with configurable port
exec gunicorn \
    --bind "0.0.0.0:${OCR_PORT}" \
    --workers 1 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    app.main:app

