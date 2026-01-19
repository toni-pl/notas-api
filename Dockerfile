# ===== FASE 1: Build =====
FROM python:3.12 AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --user -r requirements.txt

# ===== FASE 2: Final =====
FROM python:3.12-slim

WORKDIR /app

# Copiar las dependencias instaladas desde builder
COPY --from=builder /root/.local /root/.local

# Asegurar que los paquetes estén en el PATH
ENV PATH=/root/.local/bin:$PATH

# Copiar el código de la aplicación
COPY app.py .

# Puerto
EXPOSE 5000

# Comando de arranque
CMD ["python", "app.py"]
