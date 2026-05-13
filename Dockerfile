# Stage 1 — build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2 — Python runtime + Trivy
FROM python:3.12-slim

# Install Trivy
RUN apt-get update && apt-get install -y --no-install-recommends wget apt-transport-https gnupg \
    && wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | apt-key add - \
    && echo "deb https://aquasecurity.github.io/trivy-repo/deb generic main" > /etc/apt/sources.list.d/trivy.list \
    && apt-get update && apt-get install -y --no-install-recommends trivy \
    && rm -rf /var/lib/apt/lists/*

# Pre-bake Trivy DB — guarantees 60-second install claim (no network call at startup)
RUN trivy image --download-db-only --quiet

# Install Python deps
WORKDIR /app
COPY backend/pyproject.toml ./backend/
RUN pip install --no-cache-dir -e ./backend

# Copy application
COPY backend/ ./backend/
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

EXPOSE 8080

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
