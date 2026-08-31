# 🚀 Instalación Rápida - JARVIS Server

## Para el PC Viejo (Servidor)

### Opción 1: Instalación Automática (RECOMENDADO) ⚡

1. **Clona el repositorio:**
   ```cmd
   cd C:\
   git clone https://github.com/Yesit21/Jarvis-Iron-Man.git
   cd Jarvis-Iron-Man
   ```

2. **Ejecuta el instalador:**
   ```cmd
   install_server.bat
   ```

3. **Listo!** El script hará todo automáticamente:
   - ✅ Verifica Python y Ollama
   - ✅ Descarga el modelo de IA
   - ✅ Crea entorno virtual
   - ✅ Instala dependencias
   - ✅ Configura el servidor

---

### Opción 2: Manual 🔧

```cmd
REM 1. Clonar proyecto
cd C:\
git clone https://github.com/Yesit21/Jarvis-Iron-Man.git
cd Jarvis-Iron-Man

REM 2. Descargar modelo
ollama pull llama3.2:1b

REM 3. Crear entorno virtual
python -m venv venv
call venv\Scripts\activate

REM 4. Instalar dependencias
pip install ollama requests flask flask-cors flask-socketio eventlet colorama python-dateutil pytz

REM 5. Iniciar servidor
cd jarvis
python server_api.py --host 0.0.0.0 --port 5000
```

---

## Configurar Auto-Start (Opcional pero Recomendado)

Para que el servidor inicie automáticamente al encender el PC:

1. **Click derecho en `install_service.bat`**
2. **"Ejecutar como administrador"**
3. **Listo!** Ahora JARVIS inicia con Windows

---

## Para tu PC Principal (Cliente)

### Desde el mismo proyecto:

```cmd
REM Conectarte al servidor
python jarvis_client.py --server http://192.168.1.100:5000
```

### O usar JARVIS completo local:

Edita `jarvis/config/settings.json`:
```json
{
  "ollama": {
    "base_url": "http://192.168.1.100:11434"
  }
}
```

Luego:
```cmd
python jarvis/main_v2.py --voice --vision
```

---

## 🌐 Dashboard Web

Una vez el servidor esté corriendo, abre tu navegador:

**Desde el mismo PC servidor:**
```
http://localhost:5000/dashboard.html
```

**Desde tu PC principal:**
```
http://192.168.1.100:5000/dashboard.html
```

**Desde tu móvil (misma red WiFi):**
```
http://192.168.1.100:5000/dashboard.html
```

---

## 🔧 Verificación

### En el PC servidor, verifica:

```cmd
REM Ollama funcionando
ollama list

REM Python funcionando
python --version

REM Ver IP del servidor
ipconfig
```

### Desde otro dispositivo:

```cmd
REM Hacer ping al servidor
ping 192.168.1.100

REM Probar la API
curl http://192.168.1.100:5000/api/health
```

---

## ⚡ Comandos Útiles

### Iniciar servidor:
```cmd
start_server.bat
```

### Detener servidor:
```cmd
Ctrl + C
```

### Ver logs en tiempo real:
```cmd
REM (Los verás en la terminal donde corre el servidor)
```

### Reiniciar servidor:
```cmd
REM Detén (Ctrl+C) y vuelve a ejecutar
start_server.bat
```

---

## 🆘 Solución de Problemas

### ❌ Error: "No se puede conectar"
```cmd
REM Verificar que el servidor está corriendo
REM Verificar firewall de Windows
REM Verificar que ambos PCs están en la misma red
```

### ❌ Error: "Modelo no encontrado"
```cmd
ollama pull llama3.2:1b
```

### ❌ Error: "Puerto 5000 en uso"
```cmd
REM Usa otro puerto
python server_api.py --host 0.0.0.0 --port 5001
```

---

## 📊 Especificaciones del PC Servidor

**Mínimo:**
- CPU: 2 cores
- RAM: 8 GB
- Disco: 50 GB libres
- Red: Ethernet (recomendado)

**Tu PC (Perfecto ✅):**
- CPU: AMD E1-2100 (2 cores)
- RAM: 8 GB
- Disco: **SSD 480 GB** 🚀
- Red: Ethernet

---

## 🎯 Próximos Pasos

1. ✅ Instalar en PC servidor
2. ✅ Probar dashboard desde navegador
3. ✅ Conectar desde PC principal
4. 🔜 Usar voz, visión y capacidades avanzadas
5. 🔜 FASE 3: Inteligencia Proactiva

---

**¿Problemas?** Revisa: `README.md` o `FASE2_COMPLETADA.md`
