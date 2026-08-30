"""
Sistema de Memoria a Largo Plazo con RAG (Retrieval-Augmented Generation)
Permite a Jarvis recordar conversaciones y aprender del usuario
"""
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from datetime import datetime
from typing import List, Dict, Any, Optional
import os
import json


class MemorySystem:
    """Sistema de memoria semántica con ChromaDB"""
    
    def __init__(self, persist_directory: str = "../data/memory"):
        """
        Inicializa el sistema de memoria
        
        Args:
            persist_directory: Directorio donde se guardará la memoria
        """
        # Asegurar que existe el directorio
        os.makedirs(persist_directory, exist_ok=True)
        
        print("🧠 Inicializando sistema de memoria...")
        
        # Inicializar modelo de embeddings LOCAL
        print("📥 Cargando modelo de embeddings local...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Función de embedding personalizada para ChromaDB
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Cliente ChromaDB
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Colecciones de memoria con embedding function
        self.conversations = self._get_or_create_collection("conversations")
        self.user_facts = self._get_or_create_collection("user_facts")
        self.preferences = self._get_or_create_collection("preferences")
        
        print("✅ Sistema de memoria listo")
    
    def _get_or_create_collection(self, name: str):
        """Obtiene o crea una colección en ChromaDB"""
        try:
            return self.client.get_collection(
                name=name,
                embedding_function=self.embedding_function
            )
        except:
            return self.client.create_collection(
                name=name,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
    
    def store_conversation(self, user_input: str, jarvis_response: str, intent: str):
        """
        Almacena una conversación en la memoria
        
        Args:
            user_input: Lo que dijo el usuario
            jarvis_response: Respuesta de Jarvis
            intent: Intención clasificada
        """
        timestamp = datetime.now().isoformat()
        conversation_id = f"conv_{timestamp}_{hash(user_input) % 100000}"
        
        # Almacenar en ChromaDB
        self.conversations.add(
            documents=[f"Usuario: {user_input}\nJarvis: {jarvis_response}"],
            metadatas=[{
                "user_input": user_input,
                "jarvis_response": jarvis_response,
                "intent": intent,
                "timestamp": timestamp
            }],
            ids=[conversation_id]
        )
    
    def store_user_fact(self, fact: str, category: str = "general"):
        """
        Almacena un hecho sobre el usuario
        Ejemplo: "Le gusta el café sin azúcar", "Trabaja como ingeniero"
        
        Args:
            fact: Hecho a recordar
            category: Categoría del hecho (personal, trabajo, preferencias, etc.)
        """
        timestamp = datetime.now().isoformat()
        fact_id = f"fact_{timestamp}_{hash(fact) % 100000}"
        
        self.user_facts.add(
            documents=[fact],
            metadatas=[{
                "category": category,
                "timestamp": timestamp
            }],
            ids=[fact_id]
        )
        
        print(f"💾 Recordado: {fact}")
    
    def store_preference(self, preference_key: str, preference_value: str):
        """
        Almacena una preferencia del usuario
        Ejemplo: ("idioma", "español"), ("zona_horaria", "America/Mexico_City")
        
        Args:
            preference_key: Clave de la preferencia
            preference_value: Valor de la preferencia
        """
        timestamp = datetime.now().isoformat()
        pref_id = f"pref_{preference_key}"
        
        # Eliminar preferencia anterior si existe
        try:
            self.preferences.delete(ids=[pref_id])
        except:
            pass
        
        self.preferences.add(
            documents=[f"{preference_key}: {preference_value}"],
            metadatas=[{
                "key": preference_key,
                "value": preference_value,
                "timestamp": timestamp
            }],
            ids=[pref_id]
        )
    
    def recall_similar_conversations(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Busca conversaciones similares en la memoria
        
        Args:
            query: Consulta de búsqueda
            n_results: Número de resultados a devolver
            
        Returns:
            Lista de conversaciones relevantes
        """
        try:
            results = self.conversations.query(
                query_texts=[query],
                n_results=min(n_results, self.conversations.count())
            )
            
            if not results['metadatas'] or not results['metadatas'][0]:
                return []
            
            conversations = []
            for metadata, distance in zip(results['metadatas'][0], results['distances'][0]):
                conversations.append({
                    "user_input": metadata.get("user_input", ""),
                    "jarvis_response": metadata.get("jarvis_response", ""),
                    "intent": metadata.get("intent", ""),
                    "timestamp": metadata.get("timestamp", ""),
                    "relevance": 1 - distance  # Convertir distancia a relevancia
                })
            
            return conversations
            
        except Exception as e:
            print(f"⚠️ Error buscando en memoria: {e}")
            return []
    
    def recall_user_facts(self, query: str = "", category: Optional[str] = None, n_results: int = 5) -> List[str]:
        """
        Recupera hechos sobre el usuario
        
        Args:
            query: Consulta de búsqueda (opcional)
            category: Filtrar por categoría (opcional)
            n_results: Número de resultados
            
        Returns:
            Lista de hechos relevantes
        """
        try:
            if self.user_facts.count() == 0:
                return []
            
            if query:
                results = self.user_facts.query(
                    query_texts=[query],
                    n_results=min(n_results, self.user_facts.count())
                )
                return results['documents'][0] if results['documents'] else []
            else:
                # Obtener todos los hechos
                all_facts = self.user_facts.get()
                return all_facts['documents'][:n_results] if all_facts['documents'] else []
                
        except Exception as e:
            print(f"⚠️ Error recuperando hechos: {e}")
            return []
    
    def get_preference(self, preference_key: str) -> Optional[str]:
        """
        Obtiene una preferencia específica del usuario
        
        Args:
            preference_key: Clave de la preferencia
            
        Returns:
            Valor de la preferencia o None
        """
        try:
            result = self.preferences.get(ids=[f"pref_{preference_key}"])
            if result['metadatas'] and len(result['metadatas']) > 0:
                return result['metadatas'][0].get('value')
        except:
            pass
        return None
    
    def get_all_preferences(self) -> Dict[str, str]:
        """
        Obtiene todas las preferencias del usuario
        
        Returns:
            Diccionario con todas las preferencias
        """
        try:
            all_prefs = self.preferences.get()
            preferences = {}
            if all_prefs['metadatas']:
                for metadata in all_prefs['metadatas']:
                    preferences[metadata['key']] = metadata['value']
            return preferences
        except:
            return {}
    
    def build_context_from_memory(self, current_query: str, max_context_items: int = 3) -> str:
        """
        Construye un contexto enriquecido usando la memoria
        
        Args:
            current_query: Consulta actual del usuario
            max_context_items: Máximo de items de contexto
            
        Returns:
            String con contexto relevante
        """
        context_parts = []
        
        # Buscar conversaciones relevantes
        similar_convs = self.recall_similar_conversations(current_query, n_results=2)
        if similar_convs:
            context_parts.append("## Conversaciones Relevantes del Pasado:")
            for conv in similar_convs[:2]:
                if conv['relevance'] > 0.7:  # Solo si es muy relevante
                    context_parts.append(f"- Usuario preguntó: {conv['user_input'][:100]}")
        
        # Buscar hechos del usuario
        user_facts = self.recall_user_facts(current_query, n_results=3)
        if user_facts:
            context_parts.append("\n## Lo que sé sobre ti:")
            for fact in user_facts[:3]:
                context_parts.append(f"- {fact}")
        
        # Preferencias
        preferences = self.get_all_preferences()
        if preferences:
            context_parts.append("\n## Tus Preferencias:")
            for key, value in preferences.items():
                context_parts.append(f"- {key}: {value}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def get_memory_stats(self) -> Dict[str, int]:
        """Obtiene estadísticas de la memoria"""
        return {
            "total_conversations": self.conversations.count(),
            "user_facts": self.user_facts.count(),
            "preferences": self.preferences.count()
        }
    
    def clear_memory(self):
        """PELIGRO: Borra toda la memoria"""
        self.client.reset()
        print("🗑️ Memoria borrada completamente")


if __name__ == "__main__":
    # Prueba del sistema de memoria
    print("🧪 Probando MemorySystem...\n")
    
    memory = MemorySystem("../../data/memory")
    
    # Almacenar conversaciones
    memory.store_conversation(
        "¿Cuál es el clima hoy?",
        "Hoy estará soleado con 25 grados",
        "CONSULTA_WEB"
    )
    
    # Almacenar hecho
    memory.store_user_fact("Le gusta el café sin azúcar", "preferencias")
    
    # Almacenar preferencia
    memory.store_preference("nombre", "Tony")
    
    # Buscar en memoria
    print("\n🔍 Buscando conversaciones sobre clima...")
    results = memory.recall_similar_conversations("tiempo mañana", n_results=2)
    for r in results:
        print(f"  Relevancia: {r['relevance']:.2f} - {r['user_input']}")
    
    # Estadísticas
    print(f"\n📊 Estadísticas: {memory.get_memory_stats()}")
