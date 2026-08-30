"""
JARVIS V2 - Just A Rather Very Intelligent System
Versión mejorada con capacidades de FASE 2
"""
import json
import os
import sys
from datetime import datetime
from colorama import init, Fore, Style
import argparse

# Inicializar colorama
init()

# Importar componentes core
from core.ollama_client import OllamaClient
from core.intent_router import IntentRouter
from core.database import JarvisDatabase
from core.memory_system import MemorySystem
from core.learning_engine import LearningEngine

# Módulos FASE 1
from modules.reminders import ReminderModule

# Módulos FASE 2
from modules.web_search import WebSearchModule, WebQueryRouter
from modules.system_control import SystemControlModule, SystemCommandRouter
from modules.voice_input import VoiceInputModule, VoiceCommandRouter
from modules.voice_output import VoiceOutputModule, VoiceAssistant
from modules.vision import VisionModule, VisionCommandRouter


class JarvisV2:
    """Clase principal del asistente Jarvis V2"""
    
    def __init__(self, voice_enabled=False, vision_enabled=False):
        print(f"{Fore.CYAN}🚀 Inicializando JARVIS V2...{Style.RESET_ALL}")
        
        # Cargar configuración
        self.config = self._load_config()
        self.prompts = self._load_prompts()
        
        # Componentes core
        self.ollama = OllamaClient(
            base_url=self.config["ollama"]["base_url"],
            model=self.config["ollama"]["model"]
        )
        
        # Verificar conexión
        if not self.ollama.test_connection():
            print(f"{Fore.RED}❌ Error: No se pudo conectar con Ollama{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Asegúrate de que Ollama esté corriendo{Style.RESET_ALL}")
            sys.exit(1)
        
        self.db = JarvisDatabase(self.config["database"]["path"])
        self.router = IntentRouter(self.ollama, self.prompts)
        self.memory = MemorySystem()
        self.learning = LearningEngine(self.ollama, self.memory)
        
        # FASE 1: Módulos básicos
        self.reminder_module = ReminderModule(self.db, self.router)
        
        # FASE 2: Módulos avanzados
        self.web_search = WebSearchModule()
        self.web_router = WebQueryRouter(self.web_search, self.ollama)
        
        self.system_control = SystemControlModule()
        self.system_router = SystemCommandRouter(self.system_control)
        
        # Voz (opcional)
        self.voice_enabled = voice_enabled
        if voice_enabled:
            try:
                print(f"{Fore.YELLOW}🎤 Inicializando módulo de voz...{Style.RESET_ALL}")
                self.voice_input = VoiceInputModule(model_size="base", language="es")
                self.voice_output = VoiceOutputModule(engine="pyttsx3", language="es")
                self.voice_router = VoiceCommandRouter(self.voice_input, self)
                self.voice_assistant = VoiceAssistant(self.voice_input, self.voice_output, self)
                print(f"{Fore.GREEN}✅ Voz habilitada{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️ Voz no disponible: {str(e)}{Style.RESET_ALL}")
                self.voice_enabled = False
        
        # Visión (opcional)
        self.vision_enabled = vision_enabled
        if vision_enabled:
            try:
                print(f"{Fore.YELLOW}👁️ Inicializando módulo de visión...{Style.RESET_ALL}")
                self.vision = VisionModule(self.config["ollama"]["base_url"])
                self.vision_router = VisionCommandRouter(self.vision)
                
                # Verificar si modelo de visión está disponible
                if self.vision.is_vision_model_available():
                    print(f"{Fore.GREEN}✅ Visión habilitada{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}⚠️ Modelo de visión no encontrado. Instala: ollama pull llava{Style.RESET_ALL}")
                    self.vision_enabled = False
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️ Visión no disponible: {str(e)}{Style.RESET_ALL}")
                self.vision_enabled = False
        
        print(f"{Fore.GREEN}✅ JARVIS V2 listo para servir{Style.RESET_ALL}\n")
    
    def _load_config(self) -> dict:
        """Carga la configuración"""
        config_path = os.path.join(os.path.dirname(__file__), "config", "settings.json")
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _load_prompts(self) -> dict:
        """Carga los prompts"""
        prompts_path = os.path.join(os.path.dirname(__file__), "config", "prompts.json")
        with open(prompts_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def process_input(self, user_input: str, image_path: str = None) -> str:
        """
        Procesar entrada del usuario
        
        Args:
            user_input: Texto del usuario
            image_path: Ruta de imagen (opcional, para análisis visual)
            
        Returns:
            Respuesta de JARVIS
        """
        # Comandos especiales de memoria
        if user_input.lower() == "¿qué sabes de mí?":
            return self.learning.get_learning_summary()
        
        # Contexto de memoria
        memory_context = self.memory.build_context_from_memory(user_input)
        
        # Clasificar intención
        intent = self.router.classify_intent(user_input)
        
        response = ""
        
        # Router de intenciones
        if intent == "RECORDATORIO":
            result = self.reminder_module.process_reminder(user_input)
            response = result["message"]
        
        elif intent == "CONSULTA_WEB":
            response = self.web_router.process_web_query(user_input)
        
        elif intent == "CONTROL_SISTEMA":
            response = self.system_router.process_system_command(user_input)
        
        elif intent == "VISIÓN":
            if self.vision_enabled:
                response = self.vision_router.process_vision_command(user_input, image_path)
            else:
                response = "La capacidad de visión no está habilitada. Activa con: --vision"
        
        elif intent == "CONVERSACIÓN":
            # Chat general con contexto
            system_prompt = self.prompts["system_prompt"]
            if memory_context:
                system_prompt += f"\n\n{memory_context}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
            response = self.ollama.chat(messages)
        
        else:
            response = f"Función '{intent}' detectada pero aún no implementada completamente."
        
        # Aprender de esta conversación
        self.learning.extract_and_learn(user_input, response, intent)
        self.memory.store_conversation(user_input, response, intent)
        self.db.log_conversation(user_input, response, intent)
        
        return response
    
    def run_interactive(self):
        """Modo interactivo en terminal"""
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  J.A.R.V.I.S V2 - Just A Rather Very Intelligent System{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Modelo: {self.config['ollama']['model']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Capacidades FASE 2:{Style.RESET_ALL}")
        print(f"  • {Fore.CYAN}🌐 Búsquedas Web{Style.RESET_ALL} - Clima, noticias, información en tiempo real")
        print(f"  • {Fore.CYAN}🖥️ Control del Sistema{Style.RESET_ALL} - Abrir apps, ejecutar comandos")
        if self.voice_enabled:
            print(f"  • {Fore.GREEN}🎤 Entrada de Voz{Style.RESET_ALL} - Comandos por voz")
            print(f"  • {Fore.GREEN}🔊 Salida de Voz{Style.RESET_ALL} - Respuestas habladas")
        else:
            print(f"  • {Fore.YELLOW}🎤 Voz{Style.RESET_ALL} - Deshabilitada (usa --voice para activar)")
        
        if self.vision_enabled:
            print(f"  • {Fore.GREEN}👁️ Visión{Style.RESET_ALL} - Análisis de imágenes")
        else:
            print(f"  • {Fore.YELLOW}👁️ Visión{Style.RESET_ALL} - Deshabilitada (usa --vision para activar)")
        
        print(f"\n{Fore.GREEN}Comandos especiales:{Style.RESET_ALL}")
        print(f"  • {Fore.YELLOW}recordatorios{Style.RESET_ALL} - Ver recordatorios")
        print(f"  • {Fore.YELLOW}¿qué sabes de mí?{Style.RESET_ALL} - Ver aprendizaje")
        print(f"  • {Fore.YELLOW}estadísticas{Style.RESET_ALL} - Estadísticas de memoria")
        print(f"  • {Fore.YELLOW}sistema{Style.RESET_ALL} - Info del PC")
        if self.voice_enabled:
            print(f"  • {Fore.YELLOW}modo voz{Style.RESET_ALL} - Activar control por voz")
        if self.vision_enabled:
            print(f"  • {Fore.YELLOW}analiza [imagen.jpg]{Style.RESET_ALL} - Analizar imagen")
        print(f"  • {Fore.YELLOW}salir{Style.RESET_ALL} - Cerrar JARVIS")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
        
        while True:
            try:
                user_input = input(f"{Fore.BLUE}[Usuario] ► {Style.RESET_ALL}").strip()
                
                if not user_input:
                    continue
                
                # Comandos especiales
                if user_input.lower() in ["salir", "exit", "quit"]:
                    print(f"\n{Fore.CYAN}👋 Hasta pronto, señor.{Style.RESET_ALL}")
                    break
                
                if user_input.lower() in ["listar recordatorios", "recordatorios"]:
                    response = self.reminder_module.list_reminders()
                
                elif user_input.lower() in ["estadísticas de memoria", "estadísticas", "stats"]:
                    stats = self.memory.get_memory_stats()
                    response = f"📊 Estadísticas de Memoria:\n"
                    response += f"  • Conversaciones: {stats['total_conversations']}\n"
                    response += f"  • Hechos sobre ti: {stats['user_facts']}\n"
                    response += f"  • Preferencias: {stats['preferences']}"
                
                elif user_input.lower() == "sistema":
                    response = self.system_router.process_system_command("info del sistema")
                
                elif user_input.lower() == "modo voz" and self.voice_enabled:
                    self.voice_assistant.start_voice_assistant()
                    continue
                
                elif user_input.lower().startswith("analiza ") and self.vision_enabled:
                    image_path = user_input[8:].strip()
                    if os.path.exists(image_path):
                        response = self.vision.describe_scene(image_path)
                    else:
                        response = f"No encuentro la imagen: {image_path}"
                
                else:
                    # Procesar normalmente
                    response = self.process_input(user_input)
                
                # Mostrar respuesta
                print(f"{Fore.GREEN}[JARVIS] {response}{Style.RESET_ALL}\n")
                
                # Hablar respuesta si voz está habilitada
                if self.voice_enabled and hasattr(self, 'voice_output'):
                    self.voice_output.speak(response, async_mode=True)
                
            except KeyboardInterrupt:
                print(f"\n\n{Fore.CYAN}👋 Hasta pronto, señor.{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}\n")


def main():
    """Punto de entrada principal"""
    parser = argparse.ArgumentParser(description='JARVIS V2 - Asistente IA Avanzado')
    parser.add_argument('--voice', action='store_true', help='Habilitar entrada y salida de voz')
    parser.add_argument('--vision', action='store_true', help='Habilitar análisis de imágenes')
    
    args = parser.parse_args()
    
    try:
        jarvis = JarvisV2(voice_enabled=args.voice, vision_enabled=args.vision)
        jarvis.run_interactive()
    except Exception as e:
        print(f"{Fore.RED}❌ Error fatal: {str(e)}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
