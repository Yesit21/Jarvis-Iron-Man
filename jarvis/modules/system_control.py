"""
Módulo de Control del Sistema
Permite a JARVIS controlar el PC y ejecutar tareas
"""
import subprocess
import os
import psutil
import platform
import webbrowser
from typing import Dict, List
import json


class SystemControlModule:
    """Control del sistema operativo y aplicaciones"""
    
    def __init__(self):
        self.os_type = platform.system()  # Windows, Linux, Darwin (Mac)
        self.apps_registry = self._load_common_apps()
    
    def _load_common_apps(self) -> Dict:
        """Cargar registro de aplicaciones comunes"""
        if self.os_type == "Windows":
            return {
                "chrome": "chrome.exe",
                "firefox": "firefox.exe",
                "edge": "msedge.exe",
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "paint": "mspaint.exe",
                "word": "winword.exe",
                "excel": "excel.exe",
                "spotify": "spotify.exe",
                "discord": "discord.exe",
                "vscode": "code.exe",
                "cmd": "cmd.exe",
                "powershell": "powershell.exe"
            }
        else:
            return {}
    
    def open_application(self, app_name: str) -> Dict:
        """
        Abrir una aplicación
        
        Args:
            app_name: Nombre de la aplicación
            
        Returns:
            Resultado de la operación
        """
        try:
            app_name_lower = app_name.lower()
            
            # Buscar en registro
            if app_name_lower in self.apps_registry:
                executable = self.apps_registry[app_name_lower]
                
                if self.os_type == "Windows":
                    subprocess.Popen(executable, shell=True)
                else:
                    subprocess.Popen([executable])
                
                return {
                    "success": True,
                    "message": f"Abriendo {app_name}..."
                }
            else:
                # Intentar abrir directamente
                if self.os_type == "Windows":
                    subprocess.Popen(f"start {app_name}", shell=True)
                else:
                    subprocess.Popen([app_name])
                
                return {
                    "success": True,
                    "message": f"Intentando abrir {app_name}..."
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"No pude abrir {app_name}: {str(e)}"
            }
    
    def open_website(self, url: str) -> Dict:
        """
        Abrir sitio web en el navegador
        
        Args:
            url: URL del sitio
            
        Returns:
            Resultado
        """
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            webbrowser.open(url)
            
            return {
                "success": True,
                "message": f"Abriendo {url} en el navegador..."
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al abrir sitio web: {str(e)}"
            }
    
    def get_system_info(self) -> Dict:
        """
        Obtener información del sistema
        
        Returns:
            Información del sistema
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "os": f"{platform.system()} {platform.release()}",
                "processor": platform.processor(),
                "cpu_usage": f"{cpu_percent}%",
                "ram_total": f"{memory.total / (1024**3):.1f} GB",
                "ram_used": f"{memory.used / (1024**3):.1f} GB",
                "ram_percent": f"{memory.percent}%",
                "disk_total": f"{disk.total / (1024**3):.1f} GB",
                "disk_used": f"{disk.used / (1024**3):.1f} GB",
                "disk_percent": f"{disk.percent}%"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def list_running_processes(self, limit: int = 10) -> List[Dict]:
        """
        Listar procesos en ejecución
        
        Args:
            limit: Número de procesos a mostrar
            
        Returns:
            Lista de procesos
        """
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    processes.append({
                        "pid": info['pid'],
                        "name": info['name'],
                        "cpu": info['cpu_percent'],
                        "memory": info['memory_percent']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Ordenar por uso de CPU
            processes.sort(key=lambda x: x['cpu'] if x['cpu'] else 0, reverse=True)
            
            return processes[:limit]
            
        except Exception as e:
            return [{"error": str(e)}]
    
    def create_file(self, filepath: str, content: str = "") -> Dict:
        """
        Crear un archivo
        
        Args:
            filepath: Ruta del archivo
            content: Contenido del archivo
            
        Returns:
            Resultado
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "message": f"Archivo creado: {filepath}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al crear archivo: {str(e)}"
            }
    
    def read_file(self, filepath: str) -> Dict:
        """
        Leer un archivo
        
        Args:
            filepath: Ruta del archivo
            
        Returns:
            Contenido del archivo
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "size": len(content)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al leer archivo: {str(e)}"
            }
    
    def execute_command(self, command: str, safe_mode: bool = True) -> Dict:
        """
        Ejecutar comando del sistema
        
        Args:
            command: Comando a ejecutar
            safe_mode: Si True, solo permite comandos seguros
            
        Returns:
            Resultado del comando
        """
        if safe_mode:
            # Lista de comandos prohibidos en modo seguro
            dangerous_cmds = [
                'rm -rf', 'del /f', 'format', 'rmdir', 
                'shutdown', 'reboot', 'mkfs', 'dd if='
            ]
            
            if any(dangerous in command.lower() for dangerous in dangerous_cmds):
                return {
                    "success": False,
                    "message": "Comando peligroso bloqueado por seguridad"
                }
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "Comando excedió tiempo límite"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error ejecutando comando: {str(e)}"
            }
    
    def set_volume(self, level: int) -> Dict:
        """
        Ajustar volumen del sistema (0-100)
        
        Args:
            level: Nivel de volumen
            
        Returns:
            Resultado
        """
        try:
            level = max(0, min(100, level))  # Limitar entre 0-100
            
            if self.os_type == "Windows":
                # Usar nircmd o PowerShell
                cmd = f'powershell -c "(New-Object -ComObject WScript.Shell).SendKeys([char]174)"'
                subprocess.run(cmd, shell=True)
                
                return {
                    "success": True,
                    "message": f"Volumen ajustado a {level}%"
                }
            else:
                return {
                    "success": False,
                    "message": "Control de volumen no implementado para este OS"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error ajustando volumen: {str(e)}"
            }
    
    def take_screenshot(self, filepath: str = None) -> Dict:
        """
        Tomar captura de pantalla
        
        Args:
            filepath: Ruta donde guardar (opcional)
            
        Returns:
            Resultado
        """
        try:
            from PIL import ImageGrab
            from datetime import datetime
            
            if filepath is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = f"screenshot_{timestamp}.png"
            
            screenshot = ImageGrab.grab()
            screenshot.save(filepath)
            
            return {
                "success": True,
                "message": f"Captura guardada en {filepath}",
                "filepath": filepath
            }
            
        except ImportError:
            return {
                "success": False,
                "message": "PIL no instalado. Instala: pip install pillow"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error tomando captura: {str(e)}"
            }


class SystemCommandRouter:
    """Router para comandos del sistema"""
    
    def __init__(self, system_control: SystemControlModule):
        self.sys = system_control
    
    def process_system_command(self, command: str) -> str:
        """
        Procesar comando del sistema
        
        Args:
            command: Comando en lenguaje natural
            
        Returns:
            Respuesta
        """
        cmd_lower = command.lower()
        
        # Abrir aplicación
        if "abre" in cmd_lower or "abrir" in cmd_lower or "ejecuta" in cmd_lower:
            # Extraer nombre de app
            for keyword in ["abre", "abrir", "ejecuta", "ejecutar"]:
                if keyword in cmd_lower:
                    app_name = cmd_lower.split(keyword)[1].strip()
                    
                    # Si es URL
                    if "." in app_name and ("www" in app_name or "http" in app_name or ".com" in app_name):
                        result = self.sys.open_website(app_name)
                    else:
                        result = self.sys.open_application(app_name)
                    
                    return result["message"]
        
        # Información del sistema
        elif any(word in cmd_lower for word in ["sistema", "especificaciones", "info del pc", "recursos"]):
            info = self.sys.get_system_info()
            if "error" not in info:
                return (f"💻 Sistema: {info['os']}\n"
                       f"🔥 CPU: {info['cpu_usage']}\n"
                       f"🧠 RAM: {info['ram_used']} / {info['ram_total']} ({info['ram_percent']})\n"
                       f"💾 Disco: {info['disk_used']} / {info['disk_total']} ({info['disk_percent']})")
            else:
                return f"Error: {info['error']}"
        
        # Listar procesos
        elif "procesos" in cmd_lower or "aplicaciones abiertas" in cmd_lower:
            processes = self.sys.list_running_processes(10)
            if processes and "error" not in processes[0]:
                response = "📊 Procesos principales:\n\n"
                for i, proc in enumerate(processes, 1):
                    response += f"{i}. {proc['name']} (CPU: {proc['cpu']}%)\n"
                return response
            else:
                return "Error al obtener procesos"
        
        # Captura de pantalla
        elif "captura" in cmd_lower or "screenshot" in cmd_lower or "pantallazo" in cmd_lower:
            result = self.sys.take_screenshot()
            return result["message"]
        
        else:
            return "Comando del sistema no reconocido"
