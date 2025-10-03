# Script para ejecutar face-services nativamente en Windows
# Vision Attendances - Face Services

Write-Host "📹 Vision Attendances - Face Services" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si Python está instalado
$pythonInstalled = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonInstalled) {
    Write-Host "❌ Python no está instalado." -ForegroundColor Red
    Write-Host "   Descarga: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Python detectado: $(python --version)" -ForegroundColor Green

# Verificar si existe el entorno virtual
if (-not (Test-Path "venv")) {
    Write-Host "⚠️  No se encontró entorno virtual" -ForegroundColor Yellow
    Write-Host "   Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv venv
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error al crear el entorno virtual" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Entorno virtual creado" -ForegroundColor Green
}

# Activar entorno virtual
Write-Host "🔧 Activando entorno virtual..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

# Verificar si las dependencias están instaladas
Write-Host "📦 Verificando dependencias..." -ForegroundColor Cyan
$pipList = pip list

if (-not ($pipList -like "*face-recognition*")) {
    Write-Host "⚠️  Instalando dependencias (esto puede tardar varios minutos)..." -ForegroundColor Yellow
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error al instalar dependencias" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Dependencias instaladas" -ForegroundColor Green
} else {
    Write-Host "✅ Dependencias ya instaladas" -ForegroundColor Green
}

Write-Host ""
Write-Host "🚀 Iniciando servicio de detección facial..." -ForegroundColor Cyan
Write-Host "   Presiona Ctrl+C para detener" -ForegroundColor Yellow
Write-Host ""

# Ejecutar el servicio
python main.py
