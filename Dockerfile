# =============================================
# Memora — Multi-stage Production Dockerfile
# =============================================
# Build: docker build -t memora .
# Run:   docker run -p 8002:8002 -p 8503:8503 memora

FROM python:3.11-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ---- Dependencies layer (cached unless requirements.txt changes) ----
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---- Application layer ----
COPY . .

# Create a non-root user for security
RUN groupadd --gid 1000 memora \
    && useradd --uid 1000 --gid memora --shell /bin/bash --create-home memora \
    && chown -R memora:memora /app

USER memora

# Expose API and Streamlit ports
EXPOSE 8002 8503

# Health check against the FastAPI /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8002/health')" || exit 1

# Default: run the startup script
CMD ["bash", "start.sh"]
