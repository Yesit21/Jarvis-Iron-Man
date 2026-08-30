"""
Script de prueba del Sistema de Memoria y Aprendizaje
"""
import sys
import os

# Agregar jarvis al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'jarvis'))

from core.memory_system import MemorySystem
from core.ollama_client import OllamaClient
from core.learning_engine import LearningEngine

print("🧪 PRUEBA DEL SISTEMA DE MEMORIA Y APRENDIZAJE\n")
print("="*60)

# Inicializar componentes
print("\n1️⃣ Inicializando sistema de memoria...")
memory = MemorySystem("data/memory")

print("\n2️⃣ Conectando con Ollama...")
ollama = OllamaClient()
if not ollama.test_connection():
    print("❌ Error: Ollama no está corriendo")
    print("Ejecuta: ollama serve")
    sys.exit(1)

print("\n3️⃣ Inicializando motor de aprendizaje...")
learning = LearningEngine(ollama, memory)

print("\n" + "="*60)
print("📚 SIMULANDO CONVERSACIONES\n")

# Simular conversaciones
conversaciones = [
    ("Me llamo Tony Stark", "Encantado de conocerte, Tony."),
    ("Me gusta el café sin azúcar", "Anotado. Café sin azúcar."),
    ("Trabajo como ingeniero", "Excelente profesión."),
    ("Vivo en Malibú", "Hermosa ubicación."),
]

for user_input, jarvis_response in conversaciones:
    print(f"Usuario: {user_input}")
    print(f"Jarvis: {jarvis_response}")
    
    # Almacenar y aprender
    memory.store_conversation(user_input, jarvis_response, "CONVERSACIÓN")
    learning.extract_and_learn(user_input, jarvis_response, "CONVERSACIÓN")
    print()

print("="*60)
print("🔍 PROBANDO BÚSQUEDA EN MEMORIA\n")

# Buscar conversaciones similares
print("Buscando conversaciones sobre 'café'...")
results = memory.recall_similar_conversations("café", n_results=2)
for r in results:
    print(f"  📝 [{r['relevance']:.2%}] {r['user_input']}")

print("\n" + "="*60)
print("📊 RESUMEN DE LO APRENDIDO\n")
print(learning.get_learning_summary())

print("="*60)
print("✅ PRUEBA COMPLETADA\n")
print("Ahora puedes ejecutar 'python jarvis/main.py' y Jarvis recordará todo.")
print("Prueba preguntándole: '¿qué sabes de mí?'")
