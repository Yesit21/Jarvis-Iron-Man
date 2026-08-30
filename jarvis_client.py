"""
JARVIS Client
Cliente ligero para conectarse al servidor JARVIS
"""
import requests
import socketio
import sys
import uuid
from colorama import init, Fore, Style
from datetime import datetime

# Inicializar colorama
init()


class JarvisClient:
    """Cliente para comunicarse con JARVIS Server"""
    
    def __init__(self, server_url="http://192.168.1.100:5000"):
        self.server_url = server_url
        self.api_url = f"{server_url}/api"
        self.client_id = str(uuid.uuid4())[:8]
        self.sio = socketio.Client()
        self.connected = False
        
        # Configurar eventos de WebSocket
        self._setup_socketio()
        
        print(f"{Fore.CYAN}🔌 Conectando a JARVIS Server...{Style.RESET_ALL}")
        self._connect()
    
    def _setup_socketio(self):
        """Configurar eventos de WebSocket"""
        
        @self.sio.on('connect')
        def on_connect():
            self.connected = True
            print(f"{Fore.GREEN}✅ Conectado al servidor{Style.RESET_ALL}")
        
        @self.sio.on('disconnect')
        def on_disconnect():
            self.connected = False
            print(f"{Fore.YELLOW}⚠️ Desconectado del servidor{Style.RESET_ALL}")
        
        @self.sio.on('jarvis_response')
        def on_response(data):
            """Recibir respuestas en tiempo real"""
            # Solo mostrar si no es nuestra propia respuesta
            if data.get('client_id') != self.client_id:
                print(f"\n{Fore.MAGENTA}[JARVIS (broadcast)] {data['message']}{Style.RESET_ALL}")
                print(f"{Fore.BLUE}[Usuario] ► {Style.RESET_ALL}", end='', flush=True)
        
        @self.sio.on('connection_established')
        def on_established(data):
            print(f"{Fore.GREEN}{data['message']}{Style.RESET_ALL}")
    
    def _connect(self):
        """Conectar al servidor"""
        try:
            # Verificar salud del servidor
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                print(f"{Fore.GREEN}✅ Servidor online{Style.RESET_ALL}")
                print(f"{Fore.GREEN}Modelo: {health['model']}{Style.RESET_ALL}")
                
                # Conectar WebSocket
                try:
                    self.sio.connect(self.server_url)
                except Exception as e:
                    print(f"{Fore.YELLOW}⚠️ WebSocket no disponible, usando solo HTTP{Style.RESET_ALL}")
            else:
                raise Exception("Servidor no responde correctamente")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error al conectar: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Verifica que el servidor esté corriendo en {self.server_url}{Style.RESET_ALL}")
            sys.exit(1)
    
    def send_message(self, message: str) -> str:
        """Enviar mensaje a JARVIS"""
        try:
            response = requests.post(
                f"{self.api_url}/chat",
                json={"message": message, "client_id": self.client_id},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["response"]
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "Error: El servidor tardó demasiado en responder"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_reminders(self) -> str:
        """Obtener lista de recordatorios"""
        try:
            response = requests.get(f"{self.api_url}/reminders", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data["reminders"]
            else:
                return "Error al obtener recordatorios"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_memory_stats(self) -> dict:
        """Obtener estadísticas de memoria"""
        try:
            response = requests.get(f"{self.api_url}/memory/stats", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {}
        except Exception as e:
            return {}
    
    def get_learning_summary(self) -> str:
        """Obtener resumen de aprendizaje"""
        try:
            response = requests.get(f"{self.api_url}/learning/summary", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data["summary"]
            else:
                return "Error al obtener resumen"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_history(self, limit=10) -> list:
        """Obtener historial de conversaciones"""
        try:
            response = requests.get(f"{self.api_url}/history?limit={limit}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data["history"]
            else:
                return []
        except Exception as e:
            return []
    
    def run_interactive(self):
        """Modo interactivo"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  J.A.R.V.I.S Client - Conectado a Servidor Remoto{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Servidor: {self.server_url}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Cliente ID: {self.client_id}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Comandos especiales:{Style.RESET_ALL}")
        print(f"  • {Fore.YELLOW}recordatorios{Style.RESET_ALL} - Ver recordatorios")
        print(f"  • {Fore.YELLOW}¿qué sabes de mí?{Style.RESET_ALL} - Resumen de aprendizaje")
        print(f"  • {Fore.YELLOW}estadísticas{Style.RESET_ALL} - Estadísticas de memoria")
        print(f"  • {Fore.YELLOW}historial{Style.RESET_ALL} - Últimas 10 conversaciones")
        print(f"  • {Fore.YELLOW}salir{Style.RESET_ALL} - Cerrar cliente")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        while True:
            try:
                user_input = input(f"{Fore.BLUE}[Usuario] ► {Style.RESET_ALL}").strip()
                
                if not user_input:
                    continue
                
                # Comandos especiales
                if user_input.lower() in ["salir", "exit", "quit"]:
                    print(f"\n{Fore.CYAN}👋 Desconectando...{Style.RESET_ALL}")
                    if self.connected:
                        self.sio.disconnect()
                    break
                
                if user_input.lower() in ["recordatorios", "listar recordatorios"]:
                    response = self.get_reminders()
                
                elif user_input.lower() in ["estadísticas", "stats"]:
                    stats = self.get_memory_stats()
                    response = f"📊 Estadísticas de Memoria:\n"
                    response += f"  • Conversaciones: {stats.get('total_conversations', 0)}\n"
                    response += f"  • Hechos sobre ti: {stats.get('user_facts', 0)}\n"
                    response += f"  • Preferencias: {stats.get('preferences', 0)}"
                
                elif user_input.lower() == "¿qué sabes de mí?":
                    response = self.get_learning_summary()
                
                elif user_input.lower() == "historial":
                    history = self.get_history(10)
                    if history:
                        response = "📜 Últimas conversaciones:\n"
                        for i, conv in enumerate(history[-10:], 1):
                            response += f"\n{i}. Usuario: {conv[1]}\n   JARVIS: {conv[2][:100]}..."
                    else:
                        response = "No hay historial disponible"
                
                else:
                    # Enviar al servidor
                    response = self.send_message(user_input)
                
                # Mostrar respuesta
                print(f"{Fore.GREEN}[JARVIS] {response}{Style.RESET_ALL}\n")
                
            except KeyboardInterrupt:
                print(f"\n\n{Fore.CYAN}👋 Hasta pronto, señor.{Style.RESET_ALL}")
                if self.connected:
                    self.sio.disconnect()
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}\n")


def main():
    """Punto de entrada"""
    import argparse
    
    parser = argparse.ArgumentParser(description='JARVIS Client')
    parser.add_argument('--server', default='http://192.168.1.100:5000',
                       help='URL del servidor JARVIS')
    parser.add_argument('--message', '-m', help='Enviar un mensaje único')
    
    args = parser.parse_args()
    
    try:
        client = JarvisClient(args.server)
        
        if args.message:
            # Modo mensaje único
            response = client.send_message(args.message)
            print(f"{Fore.GREEN}[JARVIS] {response}{Style.RESET_ALL}")
        else:
            # Modo interactivo
            client.run_interactive()
            
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
