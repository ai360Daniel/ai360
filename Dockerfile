# ============================================================
# 🐳 DOCKERFILE CORREGIDO PARA GOOGLE CLOUD RUN
# ============================================================

FROM python:3.10-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8080

# Directorio de trabajo
WORKDIR /app

# Dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copiar código
COPY . .

# Exponer puerto correcto para Cloud Run
EXPOSE 8080

# 🚀 Comando de arranque (CORREGIDO)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
