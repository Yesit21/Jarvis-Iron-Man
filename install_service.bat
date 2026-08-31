@echo off
chcp 65001 >nul
color 0E
echo ========================================
echo   JARVIS - Instalación como Servicio
echo ========================================
echo.
echo Este script configurará JARVIS para que
echo inicie automáticamente con Windows.
echo.
echo ⚠️ REQUIERE PERMISOS DE ADMINISTRADOR
echo.
pause

REM Verificar permisos de administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Necesitas ejecutar como Administrador
    echo.
    echo Click derecho en el archivo ^> "Ejecutar como administrador"
    pause
    exit /b 1
)

echo ✅ Permisos verificados
echo.

REM Crear script de inicio
echo [1/3] Creando script de inicio...
set SCRIPT_DIR=%~dp0
set START_SCRIPT=%SCRIPT_DIR%start_jarvis_service.bat

echo @echo off > "%START_SCRIPT%"
echo cd /d "%SCRIPT_DIR%" >> "%START_SCRIPT%"
echo call venv\Scripts\activate.bat >> "%START_SCRIPT%"
echo cd jarvis >> "%START_SCRIPT%"
echo python server_api.py --host 0.0.0.0 --port 5000 >> "%START_SCRIPT%"

echo ✅ Script creado
echo.

REM Crear tarea programada
echo [2/3] Creando tarea programada...
schtasks /delete /tn "JARVIS_Server" /f >nul 2>&1
schtasks /create /tn "JARVIS_Server" /tr "\"%START_SCRIPT%\"" /sc onstart /ru SYSTEM /rl HIGHEST /f

if %errorlevel% equ 0 (
    echo ✅ Tarea programada creada
) else (
    echo ❌ Error creando tarea
    pause
    exit /b 1
)
echo.

REM Agregar al firewall
echo [3/3] Configurando firewall...
netsh advfirewall firewall delete rule name="JARVIS Server" >nul 2>&1
netsh advfirewall firewall add rule name="JARVIS Server" dir=in action=allow protocol=TCP localport=5000 >nul 2>&1

if %errorlevel% equ 0 (
    echo ✅ Regla de firewall creada
) else (
    echo ⚠️ Advertencia: No se pudo configurar firewall
)
echo.

echo ========================================
echo   ✅ Instalación Completada!
echo ========================================
echo.
echo JARVIS Server se iniciará automáticamente:
echo   • Al encender el PC
echo   • Puerto: 5000
echo   • Acceso desde red: Permitido
echo.
echo Para administrar:
echo   • Iniciar manualmente: schtasks /run /tn "JARVIS_Server"
echo   • Detener: taskkill /f /im python.exe
echo   • Desinstalar: schtasks /delete /tn "JARVIS_Server"
echo.
echo Dashboard: http://localhost:5000/dashboard.html
echo ========================================
pause
