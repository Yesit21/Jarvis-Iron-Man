"""
JARVIS Voice Mode
Modo de voz completo con entrada y salida de voz
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'jarvis'))

from modules.jarvis_voice import JarvisVoice, JARVIS_PHRASES
import speech_recognition as sr
from colorama import init, Fore, Style
import random

init()


class VoiceJarvis:
    """JARVIS con voz completa"""
    
    def __init__(self):
        print(f"{Fore.CYAN}🎤 Inicializando JARVIS Voice Mode...{Style.RESET_ALL}")
        
        # Voz de salida
        self.voice = JarvisVoice()
        
        # Reconocimiento de voz
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Calibrar ruido ambiente
        print(f"{Fore.YELLOW}🔊 Calibrando micrófono...{Style.RESET_ALL}")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        
        print(f"{Fore.GREEN}✅ Micrófono calibrado{Style.RESET_ALL}")
        
        # Importar JARVIS
        from main import Jarvis
        self.jarvis = Jarvis()
        
        # Saludo inicial
        greeting = random.choice(JARVIS_PHRASES["startup"])
        print(f"\n{Fore.GREEN}🤖 JARVIS: {greeting}{Style.RESET_ALL}")
        self.voice.speak(greeting)
    
    def listen(self):
        """Escuchar comando de voz"""
        try:
            listening_msg = random.choice(JARVIS_PHRASES["listening"])
            print(f"\n{Fore.YELLOW}🎤 {listening_msg}{Style.RESET_ALL}")
            self.voice.speak(listening_msg, wait=True)
            
            with self.microphone as source:
                print(f"{Fore.CYAN}👂 Escuchando...{Style.RESET_ALL}")
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
            
            print(f"{Fore.YELLOW}🔄 Procesando...{Style.RESET_ALL}")
            
            # Intentar reconocer con Google (rápido)
            try:
                text = self.recognizer.recognize_google(audio, language="es-ES")
                return text
            except sr.UnknownValueError:
                return None
            
        except sr.WaitTimeoutError:
            print(f"{Fore.YELLOW}⏱️ Tiempo agotado{Style.RESET_ALL}")
            return None
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
            return None
    
    def process_and_respond(self, user_input):
        """Procesar entrada y responder con voz"""
        print(f"\n{Fore.BLUE}👤 Usuario: {user_input}{Style.RESET_ALL}")
        
        # Mostrar mensaje de procesamiento
        processing_msg = random.choice(JARVIS_PHRASES["processing"])
        print(f"{Fore.YELLOW}⚙️ {processing_msg}{Style.RESET_ALL}")
        
        # Procesar con JARVIS
        response = self.jarvis.process_input(user_input)
        
        # Mostrar respuesta
        print(f"{Fore.GREEN}🤖 JARVIS: {response}{Style.RESET_ALL}")
        
        # Hablar respuesta (IMPORTANTE: wait=True para que termine antes de continuar)
        try:
            self.voice.speak(response, wait=True)
        except Exception as e:
            print(f"{Fore.RED}⚠️ Error en síntesis de voz: {e}{Style.RESET_ALL}")
    
    def run(self):
        """Ejecutar modo de voz continuo"""
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  JARVIS Voice Mode Activado{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Di 'Jarvis detente' o 'Jarvis para' para salir{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
        
        while True:
            try:
                # Escuchar
                text = self.listen()
                
                if text:
                    text_lower = text.lower()
                    
                    # Verificar comandos de salida
                    if any(cmd in text_lower for cmd in ["jarvis detente", "jarvis para", "jarvis stop"]):
                        goodbye = random.choice(JARVIS_PHRASES["goodbye"])
                        print(f"\n{Fore.GREEN}🤖 JARVIS: {goodbye}{Style.RESET_ALL}")
                        self.voice.speak(goodbye)
                        break
                    
                    # Remover palabra de activación si está
                    for wake_word in ["jarvis", "hey jarvis", "oye jarvis"]:
                        if text_lower.startswith(wake_word):
                            text = text[len(wake_word):].strip()
                            break
                    
                    if text:
                        # Procesar y responder
                        self.process_and_respond(text)
                else:
                    error_msg = random.choice(JARVIS_PHRASES["error"])
                    print(f"{Fore.YELLOW}⚠️ {error_msg}{Style.RESET_ALL}")
                    self.voice.speak(error_msg)
                
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
        jarvis_voice = VoiceJarvis()
        jarvis_voice.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.CYAN}👋 Hasta pronto{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Error fatal: {str(e)}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
