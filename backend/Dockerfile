# Imagen base con Python 3.9
FROM python:3.9-bullseye

# Evitar prompts de apt
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema necesarias para dlib, opencv y curl (healthcheck)
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    g++ \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libboost-all-dev \
    python3-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de la app
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar Python dependencies (incluye dlib y face_recognition)
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . .

# Crear directorio para archivos media
RUN mkdir -p /app/media

# Exponer el puerto para FastAPI
EXPOSE 8000

# Comando por defecto (con reload para desarrollo)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
