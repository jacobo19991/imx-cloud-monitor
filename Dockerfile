# --- Stage 1: Compilación (Builder) ---
FROM python:3.11-slim as builder

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias necesarias para compilar (gcc, etc si fuera necesario)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# --- Stage 2: Producción (Ligera y Segura) ---
FROM python:3.11-slim

# Crear usuario non-root por seguridad (OWASP)
RUN useradd -m -r imxuser

WORKDIR /app

# Copiar wheels compilados desde el builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

# Copiar el código de la aplicación
COPY . .

# Ajustar permisos para el usuario
RUN chown -R imxuser:imxuser /app
USER imxuser

VOLUME ["/app/data", "/app/logs"]
EXPOSE 8000

CMD ["python", "-m", "src.main"]
