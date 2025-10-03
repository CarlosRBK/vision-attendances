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
docker-compose build

if [ $? -ne 0 ]; then
    echo "❌ Error al construir las imágenes"
    exit 1
fi

echo ""
echo "✅ Imágenes construidas exitosamente"
echo ""
echo "🚀 Iniciando servicios..."
docker-compose up -d

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
echo "   docker-compose logs -f"
echo ""
echo "🛑 Para detener los servicios:"
echo "   docker-compose down"
echo ""
