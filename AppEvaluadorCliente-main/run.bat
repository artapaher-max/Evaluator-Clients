:: Para debug descomentar las siguientes dos lineas
:: pip install -r requirements.txt
:: python run.py 

@echo off
:: Configuración inicial
title Evaluador Run
color 0B
cd /d "%~dp0"

:: 1. Verificar Python
echo Verificando instalación de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python no está instalado o no está en el PATH
    echo.
    echo Soluciones:
    echo 1. Instale Python desde https://www.python.org/downloads/
    echo 2. Marque "Add Python to PATH" durante la instalación
    echo.
    pause
    exit /b
)

:: 2. Verificar pip
echo Verificando pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: pip no está disponible
    echo.
    echo Intente reinstalar Python marcando la opción "Add Python to PATH"
    echo.
    pause
    exit /b
)

:: 3. Instalar requirements
echo Instalando paquetes requeridos...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
redis-cli ping

:: 4. Ejecutar aplicación
echo.
echo Iniciando la aplicación...
echo.
echo Usa Ctrl + C para detener el proceso
waitress-serve --host=0.0.0.0 --port=5000 run:app

:: 5. Mantener ventana abierta
echo.
echo Proceso completado. Revise si hubo errores arriba.
echo.
pause
