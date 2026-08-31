"""
JARVIS Voice Mode - Versión Simple
Sin PyAudio, usa solo síntesis de voz (TTS)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'jarvis'))

from modules.jarvis_voice import JarvisVoice, JARVIS_PHRASES
from colorama import init, Fore, Style
import random

init()


class SimpleVoiceJarvis:
    """JARVIS con salida de voz (sin entrada de micrófono)"""
    
    def __init__(self):
        print(f"{Fore.CYAN}🎤 Inicializando JARVIS Voice Output...{Style.RESET_ALL}")
        
        # Voz de salida
        self.voice = JarvisVoice()
        
        # Importar JARVIS
        from main import Jarvis
        self.jarvis = Jarvis()
        
        # Saludo inicial
        greeting = random.choice(JARVIS_PHRASES["startup"])
        print(f"\n{Fore.GREEN}🤖 JARVIS: {greeting}{Style.RESET_ALL}")
        self.voice.speak(greeting)
    
    def run(self):
        """Ejecutar modo interactivo con voz"""
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  JARVIS con Voz - Escribe y JARVIS responderá con voz{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Escribe 'salir' para terminar{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
        
        while True:
            try:
                # Leer entrada de texto
                user_input = input(f"{Fore.BLUE}[Usuario] ► {Style.RESET_ALL}").strip()
                
                if not user_input:
                    continue
                
                # Comandos de salida
                if user_input.lower() in ["salir", "exit", "quit"]:
                    goodbye = random.choice(JARVIS_PHRASES["goodbye"])
                    print(f"\n{Fore.GREEN}🤖 JARVIS: {goodbye}{Style.RESET_ALL}")
                    self.voice.speak(goodbye)
                    break
                
                # Procesar con JARVIS
                response = self.jarvis.process_input(user_input)
                
                # Mostrar y hablar respuesta
                print(f"{Fore.GREEN}[JARVIS] {response}{Style.RESET_ALL}\n")
                self.voice.speak(response, wait=False)  # No bloquear
                
            except KeyboardInterrupt:
                print(f"\n\n{Fore.CYAN}👋 Interrumpido por usuario{Style.RESET_ALL}")
                goodbye = random.choice(JARVIS_PHRASES["goodbye"])
                self.voice.speak(goodbye)
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")


def main():
    """Punto de entrada"""
    try:
        jarvis = SimpleVoiceJarvis()
        jarvis.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.CYAN}👋 Hasta pronto{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Error fatal: {str(e)}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
