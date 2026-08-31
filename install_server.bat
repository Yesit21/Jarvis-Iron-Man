@echo off
chcp 65001 >nul
color 0B
echo ========================================
echo   JARVIS Server - Instalación Automática
echo ========================================
echo.

REM Verificar Python
echo [1/7] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no encontrado. Instálalo desde python.org
    pause
    exit /b 1
)
echo ✅ Python encontrado

REM Verificar Ollama
echo.
echo [2/7] Verificando Ollama...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ollama no encontrado. Instálalo desde ollama.com
    pause
    exit /b 1
)
echo ✅ Ollama encontrado

REM Verificar modelo
echo.
echo [3/7] Verificando modelo de IA...
ollama list | findstr "llama3.2:1b" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Modelo no encontrado. Descargando...
    ollama pull llama3.2:1b
)
echo ✅ Modelo disponible

REM Crear entorno virtual
echo.
echo [4/7] Creando entorno virtual...
if not exist "venv" (
    python -m venv venv
    echo ✅ Entorno virtual creado
) else (
    echo ⚠️ Entorno virtual ya existe
)

REM Activar entorno virtual
echo.
echo [5/7] Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias mínimas
echo.
echo [6/7] Instalando dependencias...
pip install --upgrade pip >nul 2>&1
pip install ollama==0.3.3 requests flask flask-cors flask-socketio python-socketio eventlet colorama python-dateutil pytz

REM Configurar IP
echo.
echo [7/7] Configuración de red...
echo.
echo Tu IP actual:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4"') do echo %%a
echo.
echo ⚠️ IMPORTANTE: Anota esta IP para conectarte desde otros dispositivos
echo.

REM Crear acceso directo
echo Creando acceso directo...
echo @echo off > start_server.bat
echo call venv\Scripts\activate.bat >> start_server.bat
echo cd jarvis >> start_server.bat
echo python server_api.py --host 0.0.0.0 --port 5000 >> start_server.bat
echo pause >> start_server.bat

echo.
echo ========================================
echo   ✅ Instalación Completada!
echo ========================================
echo.
echo Para iniciar el servidor:
echo   1. Ejecuta: start_server.bat
echo   2. O manualmente: python jarvis/server_api.py
echo.
echo Documentación: README.md
echo ========================================
pause
