# Stage 1 — build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2 — Python runtime + Trivy
FROM aquasec/trivy:latest AS trivy

FROM python:3.12-slim

# Copy Trivy binary from official image — avoids brittle apt-key/repo setup
COPY --from=trivy /usr/local/bin/trivy /usr/local/bin/trivy

# Pre-bake Trivy DB — guarantees 60-second install claim (no network call at startup)
RUN trivy image --download-db-only --quiet

# Install Python deps
WORKDIR /app
COPY backend/pyproject.toml ./backend/
RUN pip install --no-cache-dir -e ./backend

# Copy application
COPY backend/ ./backend/
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

EXPOSE 5050

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "5050"]
