# ✅ Checklist de Configuración del Servidor

Imprime esta lista y marca cada paso completado.

---

## Antes de Empezar

- [ ] PC viejo con al menos 8GB RAM
- [ ] USB booteable preparado con Ubuntu Server 22.04
- [ ] Cable Ethernet conectado al router
- [ ] Teclado, mouse y monitor conectados al PC viejo
- [ ] Anotar IP del router (ej: 192.168.1.1)

---

## Instalación del Sistema Operativo

- [ ] Arrancar PC desde USB
- [ ] Completar instalación de Ubuntu Server
- [ ] Configurar usuario: `jarvis`
- [ ] Configurar IP estática (ej: 192.168.1.100)
- [ ] Instalar OpenSSH Server
- [ ] Reiniciar el servidor
- [ ] Anotar la IP asignada: `___________________`

---

## Conexión y Configuración Inicial

- [ ] Conectar por SSH desde tu PC: `ssh jarvis@[IP]`
- [ ] Transferir script `setup_server.sh` al servidor
- [ ] Dar permisos: `chmod +x setup_server.sh`
- [ ] Ejecutar: `./setup_server.sh`
- [ ] Esperar finalización (10-30 minutos)

---

## Transferencia del Proyecto

- [ ] Transferir carpeta `jarvis/` al servidor
- [ ] Transferir carpeta `data/` al servidor
- [ ] Transferir `requirements.txt` al servidor
- [ ] Transferir `main.py` y otros archivos necesarios

---

## Instalación de Dependencias

- [ ] Activar entorno virtual: `source ~/jarvis-server/venv/bin/activate`
- [ ] Instalar dependencias: `pip install -r requirements.txt`
- [ ] Verificar instalación sin errores

---

## Prueba del Sistema

- [ ] Probar Ollama: `ollama run llama3.2:3b "Hola JARVIS"`
- [ ] Ejecutar JARVIS: `python jarvis/main.py`
- [ ] Verificar que funciona correctamente
- [ ] Detener JARVIS: `Ctrl+C`

---

## Configuración de Servicio (Opcional pero Recomendado)

- [ ] Crear servicio systemd: `/etc/systemd/system/jarvis.service`
- [ ] Activar servicio: `sudo systemctl enable jarvis`
- [ ] Iniciar servicio: `sudo systemctl start jarvis`
- [ ] Verificar estado: `sudo systemctl status jarvis`

---

## Información del Servidor Configurado

**Anota esta información:**

```
┌─────────────────────────────────────────┐
│  DATOS DEL SERVIDOR JARVIS              │
├─────────────────────────────────────────┤
│ IP del Servidor: ___________________    │
│ Usuario SSH: jarvis                     │
│ Puerto SSH: 22                          │
│ Directorio: /home/jarvis/jarvis-server  │
│ Modelo IA: llama3.2:3b                  │
│ Python Venv: ~/jarvis-server/venv       │
└─────────────────────────────────────────┘
```

---

## Verificación Final

Ejecuta estos comandos para verificar que todo está funcionando:

```bash
# ¿Está Ollama activo?
sudo systemctl status ollama

# ¿Funciona el modelo?
ollama list

# ¿Está el entorno virtual activo?
which python

# ¿Están los archivos de JARVIS?
ls ~/jarvis-server/jarvis/

# ¿Cuánta RAM tiene el servidor?
free -h
```

**Resultado esperado:**
- [x] Ollama: active (running)
- [x] Modelo llama3.2:3b en la lista
- [x] Python apuntando al venv
- [x] Archivos de JARVIS presentes
- [x] Al menos 6GB RAM libre

---

## 🎉 ¡Listo!

Si todos los checks están marcados, tu servidor está listo.

**Próximo paso:** Configurar la API REST para acceder desde tu PC principal.

Archivos necesarios:
- `setup_api.sh` - Para configurar el servidor API
- `client.py` - Para tu PC principal
