# ClaimsDesk India - Professional AI Platform (Lightning Build)
FROM docker.io/library/python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
RUN pip install --upgrade pip
RUN pip install fastapi uvicorn pydantic pydantic-settings httpx

# Copy backend
COPY backend ./backend
COPY openenv.yaml .

# Copy pre-built frontend DIRECTLY from host (bypassing 40-minute HF queue!)
COPY frontend/dist ./frontend/dist

# Expose port (HF Spaces defaults to 7860)
EXPOSE 7860

# Default command: run the API server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
