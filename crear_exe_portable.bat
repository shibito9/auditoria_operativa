@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Crear EXE Portable - GAMAN Auditoria Caja Fuerte

echo ==========================================
echo   CREAR EXE PORTABLE - GAMAN AUDITORIA CAJA FUERTE
echo   Desarrollado por SANTIAGO AGUDELO - GAMAN -
echo ==========================================
echo.

py --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en PATH.
    echo Instala Python desde https://www.python.org/downloads/ y marca la opcion Add Python to PATH.
    pause
    exit /b 1
)

echo Instalando/actualizando dependencias...
py -m pip install --upgrade pip
py -m pip install openpyxl pyinstaller

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist GAMAN_Auditoria_Caja_Fuerte.spec del /q GAMAN_Auditoria_Caja_Fuerte.spec

echo.
echo Generando ejecutable portable...
py -m PyInstaller --noconsole --clean --name "GAMAN_Auditoria_Caja_Fuerte" gui.py

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo generar el EXE.
    pause
    exit /b 1
)

echo.
echo LISTO.
echo El ejecutable quedo en:
echo %CD%\dist\GAMAN_Auditoria_Caja_Fuerte\GAMAN_Auditoria_Caja_Fuerte.exe
echo.
echo Comparte toda la carpeta:
echo %CD%\dist\GAMAN_Auditoria_Caja_Fuerte
echo.
pause
