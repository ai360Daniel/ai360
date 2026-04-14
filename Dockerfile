# ============================================================
# � DOCKERFILE OPTIMIZADO PARA GOOGLE CLOUD RUN
# ============================================================
# Imagen base: Python 3.10 slim (optimizada para producción)
FROM python:3.10-slim

# ============================================================
# VARIABLES DE ENTORNO
# ============================================================
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ============================================================
# DIRECTORIOS DE TRABAJO
# ============================================================
WORKDIR /app

# ============================================================
# INSTALAR DEPENDENCIAS DEL SISTEMA
# ============================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ============================================================
# COPIAR Y INSTALAR DEPENDENCIAS DE PYTHON
# ============================================================
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# ============================================================
# COPIAR CÓDIGO DE LA APLICACIÓN
# ============================================================
COPY . .

# ============================================================
# EXPONER PUERTO (Cloud Run usa PORT)
# ============================================================
EXPOSE ${PORT:-8000}

# ============================================================
# COMANDO DE INICIO PARA PRODUCCIÓN
# ============================================================
CMD exec uvicorn main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers 4 \
    --timeout-keep-alive 5 \
    --access-log
