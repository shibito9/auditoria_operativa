@echo off
title CREAR INSTALADOR - GAMAN AUDITORIA CAJA FUERTE
color 0F

echo ================================================
echo   CREAR INSTALADOR - GAMAN AUDITORIA CAJA FUERTE
echo   Desarrollado por SANTIAGO AGUDELO - GAMAN -
echo ================================================
echo.

cd /d "%~dp0"

set "SCRIPT_ISS=%~dp0instalador_gaman_auditoria_caja_fuerte.iss"
set "ISCC_EXE="

REM Buscar Inno Setup en rutas comunes
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    set "ISCC_EXE=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
)

if not defined ISCC_EXE if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
    set "ISCC_EXE=%ProgramFiles%\Inno Setup 6\ISCC.exe"
)

if not defined ISCC_EXE if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" (
    set "ISCC_EXE=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
)

REM Buscar usando PATH si existe
if not defined ISCC_EXE (
    for /f "delims=" %%I in ('where ISCC.exe 2^>nul') do (
        set "ISCC_EXE=%%I"
        goto :found
    )
)

:found

if not defined ISCC_EXE (
    echo No encontre ISCC.exe aunque Inno Setup parece estar instalado.
    echo.
    echo Revisa manualmente estas rutas:
    echo   C:\Program Files (x86)\Inno Setup 6\ISCC.exe
    echo   C:\Program Files\Inno Setup 6\ISCC.exe
    echo.
    echo Tambien puedes compilar manualmente abriendo:
    echo   %SCRIPT_ISS%
    echo.
    pause
    exit /b 1
)

if not exist "%SCRIPT_ISS%" (
    echo No encontre el archivo .iss:
    echo %SCRIPT_ISS%
    echo.
    pause
    exit /b 1
)

echo Inno Setup encontrado en:
echo "%ISCC_EXE%"
echo.
echo Compilando instalador...
echo.

"%ISCC_EXE%" "%SCRIPT_ISS%"

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo compilar el instalador.
    pause
    exit /b 1
)

echo.
echo ================================================
echo Instalador generado correctamente.
echo Revisa la carpeta:
echo %~dp0Output
echo ================================================
echo.

start "" "%~dp0Output"

pause