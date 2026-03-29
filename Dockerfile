# Multi-stage build for ClaimsDesk India - Professional AI Platform
# Stage 1: Build Frontend
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Build Backend & Serve
FROM python:3.10-slim
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
COPY pyrightconfig.json .

# Copy built frontend from Stage 1
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Expose port (HF Spaces defaults to 7860)
EXPOSE 7860

# Default command: run the API server
# We use uvicorn to serve the FastAPI app which also serves the frontend dist
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
