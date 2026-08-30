"""
Cliente para interactuar con Ollama
"""
import json
import requests
from typing import Optional, Dict, Any


class OllamaClient:
    """Cliente para comunicarse con Ollama API"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2:3b"):
        self.base_url = base_url
        self.model = model
        
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> Optional[str]:
        """
        Genera una respuesta usando el modelo de Ollama
        
        Args:
            prompt: El prompt a enviar
            temperature: Control de aleatoriedad (0.0-1.0)
            max_tokens: Máximo de tokens en la respuesta
            
        Returns:
            Respuesta del modelo o None si hay error
        """
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "").strip()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error conectando con Ollama: {e}")
            return None
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return None
    
    def chat(self, messages: list, temperature: float = 0.7) -> Optional[str]:
        """
        Modo chat con historial de mensajes
        
        Args:
            messages: Lista de dict con 'role' y 'content'
            temperature: Control de aleatoriedad
            
        Returns:
            Respuesta del modelo o None si hay error
        """
        try:
            url = f"{self.base_url}/api/chat"
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            }
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result.get("message", {}).get("content", "").strip()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error en chat con Ollama: {e}")
            return None
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return None
    
    def extract_json(self, prompt: str) -> Optional[Dict[Any, Any]]:
        """
        Genera una respuesta y extrae JSON de ella
        Útil para extraer datos estructurados
        
        Args:
            prompt: Prompt que solicita respuesta en JSON
            
        Returns:
            Dict con el JSON parseado o None si falla
        """
        response = self.generate(prompt, temperature=0.3)
        if not response:
            return None
        
        try:
            # Intenta extraer JSON de la respuesta
            # A veces el modelo incluye texto adicional
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
            else:
                # Intenta parsear la respuesta completa
                return json.loads(response)
                
        except json.JSONDecodeError:
            print(f"⚠️ No se pudo extraer JSON de: {response[:100]}...")
            return None
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión con Ollama
        
        Returns:
            True si la conexión es exitosa
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            print("✅ Conexión con Ollama exitosa")
            return True
        except Exception as e:
            print(f"❌ No se pudo conectar con Ollama: {e}")
            return False


if __name__ == "__main__":
    # Prueba básica
    print("🧪 Probando OllamaClient...\n")
    
    client = OllamaClient()
    
    if client.test_connection():
        print("\n🤖 Probando generación de texto:")
        response = client.generate("Preséntate como Jarvis en una línea.")
        print(f"Respuesta: {response}")
        
        print("\n💬 Probando modo chat:")
        messages = [
            {"role": "system", "content": "Eres Jarvis, el asistente de Tony Stark."},
            {"role": "user", "content": "¿Cuál es tu función principal?"}
        ]
        chat_response = client.chat(messages)
        print(f"Respuesta: {chat_response}")
