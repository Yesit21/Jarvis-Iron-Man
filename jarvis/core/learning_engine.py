"""
Motor de Aprendizaje - Extrae conocimiento de las conversaciones automáticamente
"""
from typing import Dict, Any, Optional
import re


class LearningEngine:
    """Motor que aprende automáticamente del usuario"""
    
    def __init__(self, ollama_client, memory_system):
        self.ollama = ollama_client
        self.memory = memory_system
        
        # Patrones para detectar información del usuario
        self.patterns = {
            "nombre": [
                r"me llamo (\w+)",
                r"mi nombre es (\w+)",
                r"soy (\w+)"
            ],
            "preferencia": [
                r"me gusta (.*)",
                r"prefiero (.*)",
                r"mi .* favorit[oa] es (.*)"
            ],
            "trabajo": [
                r"trabajo como (.*)",
                r"soy (ingeniero|doctor|profesor|desarrollador|programador|diseñador)(.*)?",
                r"mi trabajo es (.*)"
            ],
            "ubicacion": [
                r"vivo en (\w+)",
                r"estoy en (\w+)",
                r"desde (\w+)"
            ]
        }
    
    def extract_and_learn(self, user_input: str, jarvis_response: str, intent: str):
        """
        Analiza una conversación y extrae conocimiento
        
        Args:
            user_input: Lo que dijo el usuario
            jarvis_response: Respuesta de Jarvis
            intent: Intención detectada
        """
        # Detectar patrones simples primero (rápido)
        self._detect_patterns(user_input)
        
        # Usar IA para extraer información más compleja
        self._ai_extract_facts(user_input, jarvis_response)
    
    def _detect_patterns(self, text: str):
        """Detecta patrones simples usando regex"""
        text_lower = text.lower()
        
        # Detectar nombre
        for pattern in self.patterns["nombre"]:
            match = re.search(pattern, text_lower)
            if match:
                nombre = match.group(1).capitalize()
                self.memory.store_preference("nombre", nombre)
                print(f"🎓 Aprendido: Tu nombre es {nombre}")
                return
        
        # Detectar preferencias
        for pattern in self.patterns["preferencia"]:
            match = re.search(pattern, text_lower)
            if match:
                preferencia = match.group(1)
                self.memory.store_user_fact(f"Le gusta {preferencia}", "preferencias")
                print(f"🎓 Aprendido: Te gusta {preferencia}")
        
        # Detectar trabajo
        for pattern in self.patterns["trabajo"]:
            match = re.search(pattern, text_lower)
            if match:
                trabajo = match.group(1) if match.lastindex >= 1 else match.group(0)
                self.memory.store_user_fact(f"Trabaja como {trabajo}", "profesional")
                print(f"🎓 Aprendido: Trabajas como {trabajo}")
        
        # Detectar ubicación
        for pattern in self.patterns["ubicacion"]:
            match = re.search(pattern, text_lower)
            if match:
                ubicacion = match.group(1).capitalize()
                self.memory.store_preference("ubicacion", ubicacion)
                print(f"🎓 Aprendido: Vives en {ubicacion}")
    
    def _ai_extract_facts(self, user_input: str, jarvis_response: str):
        """
        Usa IA para extraer hechos más complejos
        """
        # Prompt para extraer información
        prompt = f"""Analiza esta conversación y extrae SOLO hechos importantes sobre el usuario que deben ser recordados a largo plazo.
Responde ÚNICAMENTE con hechos concretos, uno por línea. Si no hay hechos importantes, responde "NINGUNO".

Usuario: {user_input}
Asistente: {jarvis_response}

Hechos importantes a recordar:"""
        
        try:
            response = self.ollama.generate(prompt, temperature=0.3)
            
            if response and response.strip().upper() != "NINGUNO":
                # Dividir en líneas y almacenar cada hecho
                facts = [line.strip() for line in response.split('\n') if line.strip() and not line.strip().startswith('-')]
                
                for fact in facts[:3]:  # Máximo 3 hechos por conversación
                    if len(fact) > 10 and len(fact) < 200:  # Validar longitud razonable
                        self.memory.store_user_fact(fact, "aprendizaje_ia")
                        print(f"🎓 IA aprendió: {fact}")
        
        except Exception as e:
            # Silencioso, no es crítico si falla
            pass
    
    def suggest_improvements(self, user_feedback: str) -> Optional[str]:
        """
        Aprende de feedback explícito del usuario
        
        Args:
            user_feedback: Comentario del usuario sobre Jarvis
            
        Returns:
            Confirmación del aprendizaje
        """
        # Detectar feedback negativo/positivo
        feedback_lower = user_feedback.lower()
        
        if any(word in feedback_lower for word in ["mal", "error", "incorrecto", "no me gusta"]):
            self.memory.store_user_fact(f"Feedback negativo: {user_feedback}", "feedback")
            return "Entendido. Aprenderé de este error."
        
        elif any(word in feedback_lower for word in ["bien", "perfecto", "excelente", "me gusta"]):
            self.memory.store_user_fact(f"Feedback positivo: {user_feedback}", "feedback")
            return "Me alegra que te haya gustado. Lo recordaré."
        
        return None
    
    def get_learning_summary(self) -> str:
        """
        Genera un resumen de lo que Jarvis ha aprendido
        
        Returns:
            Resumen en texto natural
        """
        stats = self.memory.get_memory_stats()
        facts = self.memory.recall_user_facts(n_results=10)
        prefs = self.memory.get_all_preferences()
        
        summary = f"📚 He almacenado {stats['total_conversations']} conversaciones.\n\n"
        
        if prefs:
            summary += "🔧 Preferencias conocidas:\n"
            for key, value in prefs.items():
                summary += f"  • {key}: {value}\n"
            summary += "\n"
        
        if facts:
            summary += "💡 Hechos que recuerdo sobre ti:\n"
            for fact in facts[:5]:
                summary += f"  • {fact}\n"
        
        return summary


if __name__ == "__main__":
    print("🧪 Motor de aprendizaje cargado correctamente")
