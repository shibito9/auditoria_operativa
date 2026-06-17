@echo off
chcp 65001 >nul
cd /d "%~dp0"
title GAMAN - Auditoría Caja Fuerte

echo ==========================================
echo   GAMAN - AUDITORIA DE CAJA FUERTE V7
echo   Desarrollado por SANTIAGO AGUDELO - GAMAN -
echo ==========================================
echo.

py -c "import openpyxl" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencia openpyxl...
    py -m pip install openpyxl
)

echo Iniciando interfaz...
echo.
py gui.py

if errorlevel 1 (
    echo.
    echo Ocurrio un error al ejecutar la aplicacion.
    pause
)
