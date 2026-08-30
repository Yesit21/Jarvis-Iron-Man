"""
Router de intenciones - Clasifica qué quiere hacer el usuario
"""
import json
from typing import Optional, Dict, Any
from .ollama_client import OllamaClient


class IntentRouter:
    """Clasifica la intención del usuario y extrae parámetros"""
    
    INTENTS = {
        "RECORDATORIO": ["reminders"],
        "DOMÓTICA": ["smart_home"],
        "CONSULTA_WEB": ["web_queries"],
        "CALENDARIO": ["calendar"],
        "NOTA": ["notes"],
        "CONTROL_SISTEMA": ["system_control"],  # FASE 2
        "VISIÓN": ["vision"],  # FASE 2
        "CONVERSACIÓN": ["general"]
    }
    
    def __init__(self, ollama_client: OllamaClient, prompts: Dict[str, str]):
        self.client = ollama_client
        self.prompts = prompts
        
    def classify_intent(self, user_input: str) -> str:
        """
        Clasifica la intención del usuario
        
        Args:
            user_input: Texto del usuario
            
        Returns:
            Categoría de la intención (RECORDATORIO, DOMÓTICA, etc.)
        """
        prompt = self.prompts["intent_classification"].format(user_input=user_input)
        response = self.client.generate(prompt, temperature=0.3)
        
        if not response:
            return "CONVERSACIÓN"
        
        # Busca la intención en la respuesta
        response_upper = response.upper()
        for intent in self.INTENTS.keys():
            if intent in response_upper:
                return intent
        
        return "CONVERSACIÓN"
    
    def extract_reminder_data(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Extrae datos estructurados para un recordatorio"""
        prompt = self.prompts["reminder_extraction"].format(user_input=user_input)
        return self.client.extract_json(prompt)
    
    def extract_smart_home_data(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Extrae datos estructurados para control de domótica"""
        prompt = self.prompts["smart_home_extraction"].format(user_input=user_input)
        return self.client.extract_json(prompt)
    
    def extract_calendar_data(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Extrae datos estructurados para eventos de calendario"""
        prompt = self.prompts["calendar_extraction"].format(user_input=user_input)
        return self.client.extract_json(prompt)
    
    def extract_note_data(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Extrae metadatos de una nota"""
        prompt = self.prompts["note_processing"].format(user_input=user_input)
        return self.client.extract_json(prompt)
    
    def reformulate_web_query(self, user_input: str) -> str:
        """Optimiza una pregunta para búsqueda web"""
        prompt = self.prompts["web_query_reformulation"].format(user_input=user_input)
        response = self.client.generate(prompt, temperature=0.5)
        return response if response else user_input
    
    def generate_confirmation(self, action_description: str) -> str:
        """Genera mensaje de confirmación natural"""
        prompt = self.prompts["confirmation_template"].format(action_description=action_description)
        response = self.client.generate(prompt, temperature=0.7)
        return response if response else "Hecho, señor."
    
    def generate_error_message(self, error_description: str) -> str:
        """Genera mensaje de error amigable"""
        prompt = self.prompts["error_template"].format(error_description=error_description)
        response = self.client.generate(prompt, temperature=0.7)
        return response if response else f"Ha ocurrido un error: {error_description}"


if __name__ == "__main__":
    # Prueba del router
    print("🧪 Probando IntentRouter...\n")
    
    # Cargar prompts
    with open("../config/prompts.json", "r", encoding="utf-8") as f:
        prompts = json.load(f)
    
    client = OllamaClient()
    router = IntentRouter(client, prompts)
    
    # Pruebas
    tests = [
        "Recuérdame comprar leche mañana a las 10am",
        "Enciende las luces del salón",
        "¿Qué tiempo hará hoy?",
        "Crea un evento: reunión con el equipo el viernes a las 3pm",
        "Toma nota: ideas para mejorar Jarvis"
    ]
    
    for test in tests:
        print(f"📝 Input: {test}")
        intent = router.classify_intent(test)
        print(f"🎯 Intención detectada: {intent}\n")
