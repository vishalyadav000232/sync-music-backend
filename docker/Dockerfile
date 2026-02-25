# -------------------------------------------------
# Stage 1: Build dependencies
# -------------------------------------------------
FROM python:3.11-slim AS builder

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required for building packages
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (for caching)
COPY requirements.txt .

# Install dependencies into a custom directory
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt


# -------------------------------------------------
# Stage 2: Final lightweight image
# -------------------------------------------------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Create non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

USER appuser

# Expose port
EXPOSE 8000

# Start FastAPI with production ASGI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]