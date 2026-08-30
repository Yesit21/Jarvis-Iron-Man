# 🤖 JARVIS - Just A Rather Very Intelligent System

Asistente personal con IA tipo Iron Man usando Ollama y arquitectura cliente-servidor.

---

## 🚀 Características

### ✅ FASE 1: Arquitectura Cliente-Servidor (COMPLETADA)
- 🌐 **API REST** - Acceso remoto desde cualquier dispositivo
- 🔌 **WebSocket** - Comunicación en tiempo real
- 💬 Conversación natural en español
- 🧠 Sistema de memoria y aprendizaje (ChromaDB + RAG)
- ⏰ Recordatorios inteligentes
- 📊 Estadísticas y análisis
- 🔍 Búsqueda semántica de conversaciones

### 🔜 FASE 2: Capacidades Avanzadas
- 🎤 Reconocimiento de voz (Whisper)
- 🔊 Síntesis de voz (Piper TTS)
- 👁️ Visión por computadora
- 🌐 Búsquedas web en tiempo real
- 🖥️ Control del PC y automatización

### 🔜 FASE 3: Inteligencia Real
- 🤖 Proactividad (JARVIS te avisa sin preguntar)
- 📚 Contexto permanente
- 🎯 Sugerencias inteligentes
- ⚡ Multi-tarea simultánea

---

## 📦 Instalación

### Servidor (PC viejo - 8GB RAM, AMD E1-2100)

```cmd
REM 1. Instalar Python 3.11+
python --version

REM 2. Instalar Ollama desde ollama.com

REM 3. Descargar modelo ligero (para PC con 8GB RAM)
ollama pull llama3.2:1b

REM 4. Crear directorio
mkdir C:\jarvis-server
cd C:\jarvis-server

REM 5. Copiar proyecto aquí

REM 6. Instalar dependencias
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Cliente (PC principal)

```cmd
pip install flask flask-cors flask-socketio python-socketio requests colorama
```

---

## ⚙️ Configuración

### 1. Configurar IP Estática en el Servidor

```cmd
REM Ver configuración actual
ipconfig

REM Configurar IP estática (como Admin)
netsh interface ipv4 set address name="Ethernet" static 192.168.1.100 255.255.255.0 192.168.1.1
netsh interface ipv4 set dns name="Ethernet" static 8.8.8.8
```

### 2. Editar configuración de JARVIS

En `jarvis/config/settings.json` del servidor:

```json
{
  "ollama": {
    "model": "llama3.2:1b",
    "base_url": "http://localhost:11434"
  }
}
```

---

## 🎯 Uso

### Modo Servidor (en el PC viejo)

```cmd
cd C:\jarvis-server\jarvis
python server_api.py
```

El servidor escuchará en `http://0.0.0.0:5000`

**Acceso desde otros dispositivos:**
- Mismo PC: `http://localhost:5000`
- Desde red local: `http://192.168.1.100:5000`

### Modo Cliente (en tu PC principal)

```cmd
python jarvis_client.py --server http://192.168.1.100:5000
```

### Modo Local (sin servidor)

```cmd
python jarvis/main.py
```

---

## 📡 API REST Endpoints

### Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/health` | Estado del servidor |
| `POST` | `/api/chat` | Enviar mensaje a JARVIS |
| `GET` | `/api/reminders` | Listar recordatorios |
| `POST` | `/api/reminders` | Crear recordatorio |
| `GET` | `/api/memory/stats` | Estadísticas de memoria |
| `GET` | `/api/learning/summary` | Qué ha aprendido JARVIS |
| `GET` | `/api/history` | Historial de conversaciones |

### Ejemplo de uso con curl

```cmd
curl http://192.168.1.100:5000/api/health

curl -X POST http://192.168.1.100:5000/api/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"Hola JARVIS\"}"
```

### WebSocket

- `connect` - Conectar al servidor
- `message` - Enviar mensaje
- `jarvis_response` - Recibir respuestas en tiempo real

---

## 🔧 Comandos Especiales del Cliente

- `recordatorios` - Ver recordatorios pendientes
- `¿qué sabes de mí?` - Ver lo que JARVIS ha aprendido
- `estadísticas` - Estadísticas de memoria
- `historial` - Últimas 10 conversaciones
- `salir` - Cerrar cliente

---

## 🖥️ Arquitectura

```
┌─────────────────────┐           ┌──────────────────────┐
│   PC Principal      │           │    PC Viejo          │
│   (Cliente)         │           │    (Servidor)        │
│                     │           │                      │
│  jarvis_client.py   │◄────────► │  server_api.py       │
│                     │  HTTP +   │                      │
│  • Terminal UI      │  WebSocket│  • Ollama            │
│  • Comandos         │           │  • llama3.2:1b       │
│  • Real-time sync   │           │  • ChromaDB Memory   │
│                     │           │  • SQLite DB         │
└─────────────────────┘           └──────────────────────┘
         │                                   │
         │         Otros Dispositivos        │
         └───────────────┬──────────────────┘
                         │
                 ┌───────▼────────┐
                 │  Navegador Web │
                 │  Móvil (futuro)│
                 └────────────────┘
```

---

## 📁 Estructura del Proyecto

```
Iron Man/
├── jarvis/
│   ├── core/                  # Componentes principales
│   │   ├── ollama_client.py   # Cliente Ollama
│   │   ├── intent_router.py   # Clasificación de intenciones
│   │   ├── database.py        # SQLite
│   │   ├── memory_system.py   # ChromaDB + RAG
│   │   └── learning_engine.py # Aprendizaje autónomo
│   ├── modules/               # Módulos de funcionalidad
│   │   └── reminders.py       # Recordatorios
│   ├── config/                # Configuración
│   │   ├── settings.json
│   │   └── prompts.json
│   ├── main.py               # Modo local
│   └── server_api.py         # 🆕 API REST + WebSocket
├── jarvis_client.py          # 🆕 Cliente para PC principal
├── data/                     # Datos locales
│   ├── jarvis.db            # Historial SQL
│   └── memory/              # ChromaDB vectores
├── requirements.txt
└── README.md
```

---

## 🚀 Guía Rápida: Configurar Servidor

### Opción 1: Windows (tu caso)

1. **Instalar Python**: python.org
2. **Instalar Ollama**: ollama.com/download
3. **Descargar modelo**:
   ```cmd
   ollama pull llama3.2:1b
   ```
4. **Copiar proyecto** a `C:\jarvis-server\`
5. **Instalar dependencias**:
   ```cmd
   cd C:\jarvis-server
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
6. **Ejecutar**:
   ```cmd
   cd jarvis
   python server_api.py
   ```

### Opción 2: Linux (alternativa)

Consulta: `GUIA_SERVIDOR.md` (incluido en el proyecto)

---

## 📊 Especificaciones Recomendadas

### Servidor Mínimo
- **CPU:** 2 cores (AMD E1-2100 funciona ✅)
- **RAM:** 8 GB
- **Disco:** 50 GB (SSD recomendado)
- **Red:** Ethernet

### Modelos según RAM
- 8 GB RAM → `llama3.2:1b` (1.3 GB)
- 16 GB RAM → `llama3.2:3b` (2 GB)
- 32+ GB RAM → `llama3.1:8b` (4.7 GB)

---

## 📝 Estado Actual

- [x] Cliente Ollama funcionando
- [x] Sistema de Memoria (ChromaDB + RAG)
- [x] Motor de Aprendizaje Autónomo
- [x] Sistema de recordatorios
- [x] **API REST del servidor** ✨
- [x] **Cliente remoto** ✨
- [x] **WebSocket en tiempo real** ✨
- [ ] Reconocimiento de voz (FASE 2)
- [ ] Síntesis de voz (FASE 2)
- [ ] Control del PC (FASE 2)
- [ ] Búsquedas web (FASE 2)
- [ ] Proactividad (FASE 3)

---

## 🎓 Próximos Pasos

1. ✅ **FASE 1 Completada** - Arquitectura Cliente-Servidor
2. 🔜 Configurar servidor en PC viejo
3. 🔜 Probar conexión cliente-servidor
4. 🔜 Implementar FASE 2 (Voz + Visión + Web)
5. 🔜 Implementar FASE 3 (Inteligencia Avanzada)

---

**Versión**: 1.0.0 (FASE 1 Completa)  
**Modelo**: llama3.2:1b/3b via Ollama  
**Arquitectura**: Cliente-Servidor con REST + WebSocket
