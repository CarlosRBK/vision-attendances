# Dockerfile para el servicio de detección facial
FROM python:3.9-bullseye

# Evitar prompts de apt
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema para OpenCV, dlib y acceso a video
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    g++ \
    libopenblas-dev \
    liblapack-dev \
    libx11-6 \
    libgtk-3-0 \
    libboost-all-dev \
    python3-dev \
    git \
    v4l-utils \
    libv4l-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/input_images /app/optimized_faces /app/asistencias

# Comando por defecto
CMD ["python", "main.py"]
