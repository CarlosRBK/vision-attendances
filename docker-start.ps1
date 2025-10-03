# Script de inicio rápido para Windows PowerShell
# Vision Attendances - Docker Quick Start

Write-Host "🚀 Vision Attendances - Docker Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si Docker está instalado
$dockerInstalled = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerInstalled) {
    Write-Host "❌ Docker no está instalado. Por favor instala Docker Desktop." -ForegroundColor Red
    Write-Host "   Descarga: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Docker detectado" -ForegroundColor Green

# Verificar si existe el archivo .env del backend
if (-not (Test-Path "backend\.env")) {
    Write-Host "⚠️  No se encontró backend\.env" -ForegroundColor Yellow
    Write-Host "   Creando desde backend\.env.example..." -ForegroundColor Yellow
    
    if (Test-Path "backend\.env.example") {
        Copy-Item "backend\.env.example" "backend\.env"
        Write-Host "✅ Archivo backend\.env creado" -ForegroundColor Green
        Write-Host "   ⚠️  IMPORTANTE: Edita backend\.env con tus credenciales de MongoDB" -ForegroundColor Yellow
        Write-Host ""
        
        $editNow = Read-Host "¿Quieres editar el archivo ahora? (s/n)"
        if ($editNow -eq "s" -or $editNow -eq "S") {
            notepad "backend\.env"
            Write-Host "   Presiona Enter cuando hayas terminado de editar..." -ForegroundColor Cyan
            Read-Host
        }
    } else {
        Write-Host "❌ No se encontró backend\.env.example" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ backend\.env encontrado" -ForegroundColor Green
}

Write-Host ""
Write-Host "🏗️  Construyendo imágenes Docker..." -ForegroundColor Cyan
docker-compose build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al construir las imágenes" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Imágenes construidas exitosamente" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Iniciando servicios..." -ForegroundColor Cyan
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al iniciar los servicios" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Servicios iniciados correctamente" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Aplicación disponible en:" -ForegroundColor Cyan
Write-Host "   Frontend:       http://localhost:3000" -ForegroundColor White
Write-Host "   Backend:        http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs:       http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Face Services:  http://localhost:5001" -ForegroundColor White
Write-Host ""
Write-Host "🎉 ¡Todo listo!" -ForegroundColor Green
Write-Host "   Abre http://localhost:3000 en tu navegador" -ForegroundColor White
Write-Host "   El frontend enviará frames a face-services para detección facial" -ForegroundColor Gray
Write-Host ""
Write-Host "📊 Para ver los logs:" -ForegroundColor Yellow
Write-Host "   docker-compose logs -f" -ForegroundColor Gray
Write-Host ""
Write-Host "🛑 Para detener los servicios:" -ForegroundColor Yellow
Write-Host "   docker-compose down" -ForegroundColor Gray
Write-Host ""
