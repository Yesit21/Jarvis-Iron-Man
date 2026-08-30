# Guía de Configuración del Servidor JARVIS

## 📋 Requisitos del PC Viejo

### Hardware Mínimo:
- **CPU:** Dual-core 2.0 GHz o superior
- **RAM:** 8 GB (16 GB recomendado para mejor rendimiento)
- **Disco:** 50 GB libres (SSD recomendado)
- **Red:** Tarjeta Ethernet (más estable que WiFi)

### Software:
- Ubuntu Server 22.04 LTS o Debian 12 (sin interfaz gráfica para ahorrar recursos)

---

## 🚀 Instalación Paso a Paso

### PASO 1: Instalar el Sistema Operativo

1. **Descargar Ubuntu Server:**
   - Ve a: https://ubuntu.com/download/server
   - Descarga Ubuntu Server 22.04 LTS
   - Crea un USB booteable con Rufus (Windows) o Etcher

2. **Instalar Ubuntu Server:**
   - Conecta teclado, mouse y monitor al PC viejo
   - Arranca desde el USB
   - Sigue el instalador (selecciona instalación mínima)
   - **Importante:** Configura un IP estática durante la instalación
   - Instala OpenSSH cuando te lo pregunte (para acceso remoto)

3. **Configuración inicial:**
   ```bash
   # Crear usuario
   Usuario: jarvis
   Contraseña: [tu contraseña segura]
   ```

---

### PASO 2: Configurar Red (IP Estática)

**Opción A: Durante la instalación** (recomendado)
- El instalador te preguntará por la configuración de red
- Selecciona "Manual" en lugar de DHCP
- Anota la IP que asignes (ej: 192.168.1.100)

**Opción B: Después de instalar**
```bash
# Ver tu configuración actual
ip addr show

# Editar configuración de red
sudo nano /etc/netplan/00-installer-config.yaml
```

Contenido del archivo (ajusta según tu red):
```yaml
network:
  version: 2
  ethernets:
    enp3s0:  # Tu interfaz de red (puede variar)
      dhcp4: no
      addresses:
        - 192.168.1.100/24  # Tu IP estática
      gateway4: 192.168.1.1  # Tu router
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

Aplicar cambios:
```bash
sudo netplan apply
```

---

### PASO 3: Ejecutar Script de Instalación

1. **Conectarte por SSH desde tu PC actual:**
   ```bash
   # Desde tu PC Windows (usa PowerShell o Git Bash)
   ssh jarvis@192.168.1.100
   ```

2. **Transferir el script de instalación:**
   
   **Opción A: Con USB**
   - Copia `setup_server.sh` a un USB
   - Conecta USB al servidor
   - Monta y copia:
   ```bash
   sudo mkdir /mnt/usb
   sudo mount /dev/sdb1 /mnt/usb
   cp /mnt/usb/setup_server.sh ~/
   ```

   **Opción B: Con SCP (desde tu PC)**
   ```bash
   # Desde tu PC Windows
   scp setup_server.sh jarvis@192.168.1.100:~/
   ```

   **Opción C: Descarga directa (si tienes GitHub)**
   ```bash
   wget https://raw.githubusercontent.com/tu-usuario/Iron-Man/main/setup_server.sh
   ```

3. **Ejecutar el script:**
   ```bash
   chmod +x setup_server.sh
   ./setup_server.sh
   ```

   ⏱️ **Este proceso tarda 10-30 minutos** dependiendo de tu conexión a internet.

---

### PASO 4: Transferir tu Proyecto JARVIS

**Opción A: Con Git (recomendado)**
```bash
cd ~/jarvis-server
git clone https://github.com/tu-usuario/Iron-Man.git .
```

**Opción B: Con SCP desde tu PC**
```bash
# Desde tu PC Windows, en PowerShell:
cd "C:\Users\Usuario\Documents\Iron Man"
scp -r jarvis/ data/ *.py *.txt jarvis@192.168.1.100:~/jarvis-server/
```

---

### PASO 5: Instalar Dependencias de Python

```bash
cd ~/jarvis-server
source venv/bin/activate
pip install -r requirements.txt
```

---

### PASO 6: Configurar Base de Datos

```bash
# Crear directorios necesarios
mkdir -p data/memory

# Inicializar base de datos (si es necesario)
python3 -c "from jarvis.core.database import Database; db = Database(); print('Base de datos inicializada')"
```

---

### PASO 7: Probar JARVIS Localmente

```bash
# Activar entorno virtual
source ~/jarvis-server/venv/bin/activate

# Ejecutar JARVIS
cd ~/jarvis-server
python jarvis/main.py
```

Si funciona correctamente, presiona `Ctrl+C` para detenerlo.

---

## 🔧 Configuración Adicional

### Configurar Arranque Automático

Crear servicio systemd:
```bash
sudo nano /etc/systemd/system/jarvis.service
```

Contenido:
```ini
[Unit]
Description=JARVIS AI Assistant Server
After=network.target ollama.service

[Service]
Type=simple
User=jarvis
WorkingDirectory=/home/jarvis/jarvis-server
Environment="PATH=/home/jarvis/jarvis-server/venv/bin"
ExecStart=/home/jarvis/jarvis-server/venv/bin/python jarvis/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activar servicio:
```bash
sudo systemctl daemon-reload
sudo systemctl enable jarvis
sudo systemctl start jarvis
```

Verificar estado:
```bash
sudo systemctl status jarvis
```

---

## 📝 Información Importante

### Credenciales y Datos

**Anota esta información:**
```
IP del Servidor: 192.168.1.100
Usuario SSH: jarvis
Puerto SSH: 22
Directorio JARVIS: /home/jarvis/jarvis-server
Modelo IA: llama3.2:3b
```

### Comandos Útiles

```bash
# Ver logs de JARVIS
sudo journalctl -u jarvis -f

# Reiniciar JARVIS
sudo systemctl restart jarvis

# Ver IP del servidor
hostname -I

# Ver uso de recursos
htop

# Probar modelo de Ollama
ollama run llama3.2:3b "Hola, soy JARVIS"
```

### Abrir Puertos en Firewall (si es necesario)

```bash
# Instalar UFW
sudo apt install ufw

# Permitir SSH
sudo ufw allow 22

# Permitir puerto de JARVIS (cuando configuremos la API)
sudo ufw allow 5000

# Activar firewall
sudo ufw enable
```

---

## ⚠️ Solución de Problemas

### Problema: No puedo conectar por SSH
- Verifica que el PC servidor esté encendido
- Verifica la IP: `ip addr show`
- Verifica que SSH esté activo: `sudo systemctl status ssh`

### Problema: Ollama no inicia
```bash
sudo systemctl restart ollama
sudo journalctl -u ollama -n 50
```

### Problema: Python no encuentra módulos
```bash
# Asegúrate de activar el entorno virtual
source ~/jarvis-server/venv/bin/activate
pip install -r requirements.txt
```

### Problema: Falta memoria RAM
```bash
# Ver uso de memoria
free -h

# Si es necesario, usar un modelo más pequeño
ollama pull llama3.2:1b
```

---

## 🎯 Próximos Pasos

Una vez completada esta guía:
1. ✅ El servidor está configurado
2. ✅ Ollama está funcionando
3. ✅ JARVIS puede ejecutarse localmente

**Siguiente fase:** Configurar la API REST para acceder a JARVIS desde tu PC principal.

Ejecuta: `bash setup_api.sh` (lo crearemos en el siguiente paso)
