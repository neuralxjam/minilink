# ---- builder ----
FROM python:3.11.9-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- runtime ----
FROM python:3.11.9-slim AS runtime
WORKDIR /app
COPY --from=builder /install /usr/local
COPY app/ ./app/
ENV BASE_URL=http://localhost:8000
# Railway sets PORT=8080; EXPOSE matches so the proxy auto-detects correctly.
# Local docker-compose maps host 8000 → container 8000 via the runtime CMD's
# ${PORT:-8000} default, so this EXPOSE is documentation-only there.
EXPOSE 8080
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
