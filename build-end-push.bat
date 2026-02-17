@echo off
REM ========================================
REM Coderr Backend - Build and Push Script
REM ========================================

echo.
echo ======================================
echo  Coderr Backend - Build and Push
echo ======================================
echo.

REM Variablen
set REGISTRY=myhomies.cr.de-fra.ionos.com
set IMAGE_NAME=abbas/coderr-backend
set TAG=latest
set FULL_IMAGE=%REGISTRY%/%IMAGE_NAME%:%TAG%

echo Registry: %REGISTRY%
echo Image: %IMAGE_NAME%
echo Tag: %TAG%
echo.

REM Prüfe ob Docker läuft
echo [1/4] Pruefe Docker...
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo FEHLER: Docker ist nicht gestartet!
    echo Bitte starten Sie Docker Desktop und versuchen Sie es erneut.
    pause
    exit /b 1
)
echo Docker ist verfuegbar.
echo.

REM Login zur Registry (falls noch nicht eingeloggt)
echo [2/4] Login zur Container Registry...
echo Bitte geben Sie Ihre Zugangsdaten ein:
docker login %REGISTRY%
if %ERRORLEVEL% NEQ 0 (
    echo FEHLER: Login fehlgeschlagen!
    pause
    exit /b 1
)
echo Login erfolgreich.
echo.

REM Image bauen
echo [3/4] Baue Docker Image...
echo Building: %FULL_IMAGE%
docker build -t %FULL_IMAGE% .
if %ERRORLEVEL% NEQ 0 (
    echo FEHLER: Build fehlgeschlagen!
    pause
    exit /b 1
)
echo Build erfolgreich.
echo.

REM Image pushen
echo [4/4] Pushe Image zur Registry...
docker push %FULL_IMAGE%
if %ERRORLEVEL% NEQ 0 (
    echo FEHLER: Push fehlgeschlagen!
    pause
    exit /b 1
)
echo.

echo ======================================
echo  Build und Push erfolgreich!
echo ======================================
echo.
echo Image: %FULL_IMAGE%
echo.
echo Naechste Schritte:
echo 1. Aktualisieren Sie docker-compose.yml auf dem Server
echo 2. Fuehren Sie aus: docker-compose pull backend
echo 3. Fuehren Sie aus: docker-compose up -d backend
echo.

pause