#!/bin/bash
# Script de instalación para servidor JARVIS
# Ejecutar con: bash setup_server.sh

set -e  # Detener si hay errores

echo "======================================"
echo "  JARVIS Server Setup"
echo "======================================"
echo ""

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para imprimir en color
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Actualizar sistema
print_status "Actualizando sistema..."
sudo apt update && sudo apt upgrade -y
print_success "Sistema actualizado"

# 2. Instalar dependencias del sistema
print_status "Instalando dependencias del sistema..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    sqlite3 \
    build-essential \
    python3-dev \
    portaudio19-dev \
    net-tools
print_success "Dependencias instaladas"

# 3. Instalar Ollama
print_status "Instalando Ollama..."
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.com/install.sh | sh
    print_success "Ollama instalado"
else
    print_success "Ollama ya está instalado"
fi

# 4. Iniciar servicio de Ollama
print_status "Configurando servicio de Ollama..."
sudo systemctl enable ollama
sudo systemctl start ollama
print_success "Servicio Ollama iniciado"

# 5. Descargar modelo de IA
print_status "Descargando modelo de IA (esto puede tardar varios minutos)..."
ollama pull llama3.2:3b
print_success "Modelo descargado"

# 6. Crear directorio para JARVIS
print_status "Creando directorio de trabajo..."
JARVIS_DIR="$HOME/jarvis-server"
mkdir -p "$JARVIS_DIR"
cd "$JARVIS_DIR"
print_success "Directorio creado en $JARVIS_DIR"

# 7. Crear entorno virtual de Python
print_status "Creando entorno virtual de Python..."
python3 -m venv venv
source venv/bin/activate
print_success "Entorno virtual creado"

# 8. Actualizar pip
print_status "Actualizando pip..."
pip install --upgrade pip
print_success "pip actualizado"

# 9. Obtener IP del servidor
SERVER_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "======================================"
echo -e "${GREEN}  Instalación completada!${NC}"
echo "======================================"
echo ""
echo "Información del servidor:"
echo "  - Directorio: $JARVIS_DIR"
echo "  - IP Local: $SERVER_IP"
echo "  - Modelo IA: llama3.2:3b"
echo ""
echo "Próximos pasos:"
echo "  1. Copia tu proyecto JARVIS a este servidor"
echo "  2. Ejecuta: source $JARVIS_DIR/venv/bin/activate"
echo "  3. Instala dependencias: pip install -r requirements.txt"
echo "  4. Configura el servidor API con el script setup_api.sh"
echo ""
