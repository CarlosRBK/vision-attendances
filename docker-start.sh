#!/bin/bash
# Script de inicio rápido para Linux/Mac
# Vision Attendances - Docker Quick Start

echo "🚀 Vision Attendances - Docker Setup"
echo "====================================="
echo ""

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instala Docker."
    echo "   Descarga: https://www.docker.com/get-started"
    exit 1
fi

echo "✅ Docker detectado"

# Detectar Docker Compose (v2 'docker compose' o v1 'docker-compose')
if docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
else
    echo "❌ No se encontró Docker Compose."
    echo "   Instala Docker Desktop actualizado o docker-compose v1."
    exit 1
fi

# Forzar plataforma amd64 en macOS Apple Silicon para evitar fallos con dlib
if [ "$(uname -s)" = "Darwin" ] && [ "$(uname -m)" = "arm64" ]; then
    export DOCKER_DEFAULT_PLATFORM=linux/amd64
    echo "ℹ️  macOS ARM detectado: usando DOCKER_DEFAULT_PLATFORM=linux/amd64"
fi

# Verificar si existe el archivo .env del backend
if [ ! -f "backend/.env" ]; then
    echo "⚠️  No se encontró backend/.env"
    echo "   Creando desde backend/.env.example..."
    
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        echo "✅ Archivo backend/.env creado"
        echo "   ⚠️  IMPORTANTE: Edita backend/.env con tus credenciales de MongoDB"
        echo ""
        
        read -p "¿Quieres editar el archivo ahora? (s/n): " edit_now
        if [ "$edit_now" = "s" ] || [ "$edit_now" = "S" ]; then
            ${EDITOR:-nano} backend/.env
        fi
    else
        echo "❌ No se encontró backend/.env.example"
        exit 1
    fi
else
    echo "✅ backend/.env encontrado"
fi

echo ""
echo "🏗️  Construyendo imágenes Docker..."
$COMPOSE_CMD build

if [ $? -ne 0 ]; then
    echo "❌ Error al construir las imágenes"
    exit 1
fi

echo ""
echo "✅ Imágenes construidas exitosamente"
echo ""
echo "🚀 Iniciando servicios..."
$COMPOSE_CMD up -d

if [ $? -ne 0 ]; then
    echo "❌ Error al iniciar los servicios"
    exit 1
fi

echo ""
echo "✅ Servicios iniciados correctamente"
echo ""
echo "📍 Aplicación disponible en:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "📊 Para ver los logs:"
echo "   $COMPOSE_CMD logs -f"
echo ""
echo "🛑 Para detener los servicios:"
echo "   $COMPOSE_CMD down"
echo ""
