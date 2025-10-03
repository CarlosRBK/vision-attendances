@echo off
REM Script para ejecutar face-services nativamente en Windows
REM Vision Attendances - Face Services

echo ========================================
echo Vision Attendances - Face Services
echo ========================================
echo.

REM Verificar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado
    echo Descarga: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python detectado
echo.

REM Verificar si existe el entorno virtual
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
    echo Entorno virtual creado
)

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat

REM Verificar dependencias
echo Verificando dependencias...
pip show face-recognition >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias (esto puede tardar varios minutos)...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
    echo Dependencias instaladas
)

echo.
echo Iniciando servicio de deteccion facial...
echo Presiona Ctrl+C para detener
echo.

REM Ejecutar el servicio
python main.py

pause
