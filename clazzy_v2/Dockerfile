# Clazzy V2 - Docker Configuration
# Multi-stage build for production deployment

# ===========================
# Stage 1: Builder
# ===========================
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# ===========================
# Stage 2: Runtime
# ===========================
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY api/ ./api/
COPY core/ ./core/
COPY ml/ ./ml/
COPY data/ ./data/
COPY external/ ./external/
COPY models/ ./models/
COPY config/ ./config/

# Create non-root user
RUN useradd --create-home appuser
USER appuser

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8001/health')" || exit 1

# Run application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001"]
