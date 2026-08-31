@echo off
color 0B

echo ========================================
echo   J.A.R.V.I.S - Iron Man AI Assistant
echo ========================================
echo.

REM Activar entorno virtual Python 3.11
if exist "venv311\Scripts\activate.bat" (
    echo Activando entorno Python 3.11...
    call venv311\Scripts\activate.bat
) else (
    echo Usando Python global...
)

REM Verificar Ollama
echo.
echo Verificando Ollama...
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo Ollama no esta corriendo
    echo Iniciando Ollama...
    start /B ollama serve
    timeout /t 3 >nul
)

echo Ollama verificado
echo.

REM Iniciar servidor
echo Iniciando JARVIS Server...
echo.
echo Accede a la interfaz en:
echo    http://localhost:5000
echo.
echo Presiona Ctrl+C para detener
echo ========================================
echo.

cd jarvis
python server_api.py

pause
