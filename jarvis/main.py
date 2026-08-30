"""
JARVIS - Just A Rather Very Intelligent System
Punto de entrada principal del asistente
"""
import json
import os
import sys
from datetime import datetime
from colorama import init, Fore, Style

# Inicializar colorama para Windows
init()

# Importar componentes core
from core.ollama_client import OllamaClient
from core.intent_router import IntentRouter
from core.database import JarvisDatabase
from core.memory_system import MemorySystem
from core.learning_engine import LearningEngine

# Importar módulos
from modules.reminders import ReminderModule


class Jarvis:
    """Clase principal del asistente Jarvis"""
    
    def __init__(self):
        print(f"{Fore.CYAN}🚀 Inicializando Jarvis...{Style.RESET_ALL}")
        
        # Cargar configuración
        self.config = self._load_config()
        self.prompts = self._load_prompts()
        
        # Inicializar componentes core
        self.ollama = OllamaClient(
            base_url=self.config["ollama"]["base_url"],
            model=self.config["ollama"]["model"]
        )
        
        # Verificar conexión con Ollama
        if not self.ollama.test_connection():
            print(f"{Fore.RED}❌ Error: No se pudo conectar con Ollama{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Asegúrate de que Ollama esté corriendo: ollama serve{Style.RESET_ALL}")
            sys.exit(1)
        
        self.db = JarvisDatabase(self.config["database"]["path"])
        self.router = IntentRouter(self.ollama, self.prompts)
        
        # Sistema de memoria y aprendizaje
        self.memory = MemorySystem()
        self.learning = LearningEngine(self.ollama, self.memory)
        
        # Inicializar módulos
        self.reminder_module = ReminderModule(self.db, self.router)
        
        print(f"{Fore.GREEN}✅ Jarvis listo para servir{Style.RESET_ALL}\n")
    
    def _load_config(self) -> dict:
        """Carga la configuración desde settings.json"""
        config_path = os.path.join(os.path.dirname(__file__), "config", "settings.json")
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _load_prompts(self) -> dict:
        """Carga los prompts desde prompts.json"""
        prompts_path = os.path.join(os.path.dirname(__file__), "config", "prompts.json")
        with open(prompts_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def process_input(self, user_input: str) -> str:
        """
        Procesa la entrada del usuario y genera una respuesta
        
        Args:
            user_input: Texto del usuario
            
        Returns:
            Respuesta de Jarvis
        """
        # Comandos especiales de memoria
        if user_input.lower() == "¿qué sabes de mí?":
            return self.learning.get_learning_summary()
        
        # Construir contexto desde la memoria
        memory_context = self.memory.build_context_from_memory(user_input)
        
        # Clasificar intención
        intent = self.router.classify_intent(user_input)
        
        response = ""
        
        # Enrutar según la intención
        if intent == "RECORDATORIO":
            result = self.reminder_module.process_reminder(user_input)
            response = result["message"]
            
        elif intent == "CONVERSACIÓN":
            # Chat general con contexto de memoria
            system_prompt = self.prompts["system_prompt"]
            
            # Agregar contexto de memoria si existe
            if memory_context:
                system_prompt += f"\n\n{memory_context}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
            response = self.ollama.chat(messages)
            
        else:
            # Módulos no implementados aún
            response = f"Función '{intent}' detectada pero aún no implementada. Estoy trabajando en ello, señor."
        
        # Aprender de esta conversación
        self.learning.extract_and_learn(user_input, response, intent)
        
        # Guardar en memoria
        self.memory.store_conversation(user_input, response, intent)
        
        # Registrar en historial
        self.db.log_conversation(user_input, response, intent)
        
        return response
    
    def run_interactive(self):
        """Modo interactivo en terminal"""
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  J.A.R.V.I.S - Just A Rather Very Intelligent System{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Modelo: {self.config['ollama']['model']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Comandos especiales:{Style.RESET_ALL}")
        print(f"  • {Fore.YELLOW}listar recordatorios{Style.RESET_ALL} - Ver recordatorios pendientes")
        print(f"  • {Fore.YELLOW}¿qué sabes de mí?{Style.RESET_ALL} - Ver lo que Jarvis ha aprendido")
        print(f"  • {Fore.YELLOW}estadísticas de memoria{Style.RESET_ALL} - Ver estadísticas del sistema de memoria")
        print(f"  • {Fore.YELLOW}salir{Style.RESET_ALL} - Cerrar Jarvis")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        while True:
            try:
                # Prompt
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
                else:
                    # Procesar normalmente
                    response = self.process_input(user_input)
                
                # Mostrar respuesta
                print(f"{Fore.GREEN}[Jarvis] {response}{Style.RESET_ALL}\n")
                
            except KeyboardInterrupt:
                print(f"\n\n{Fore.CYAN}👋 Hasta pronto, señor.{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}\n")


def main():
    """Punto de entrada principal"""
    try:
        jarvis = Jarvis()
        jarvis.run_interactive()
    except Exception as e:
        print(f"{Fore.RED}❌ Error fatal: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
