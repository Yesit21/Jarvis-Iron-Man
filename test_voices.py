"""
Probar y configurar voces disponibles
"""
import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

print("🎤 Voces disponibles en tu sistema:\n")
for i, voice in enumerate(voices):
    print(f"{i}. {voice.name}")
    print(f"   ID: {voice.id}")
    print(f"   Idiomas: {voice.languages}")
    print()

print("\n" + "="*60)
print("Prueba de voces:")
print("="*60 + "\n")

test_text = "Buenos días, señor. Soy JARVIS. Todos los sistemas operativos."

for i, voice in enumerate(voices):
    print(f"\n[{i}] Probando: {voice.name}")
    engine.setProperty('voice', voice.id)
    engine.setProperty('rate', 175)
    engine.say(test_text)
    engine.runAndWait()
    
    input("Presiona ENTER para la siguiente voz...")

print("\n✅ Prueba completada")
print("\nPara usar una voz específica, edita jarvis/modules/jarvis_voice.py")
print("y cambia el índice en la línea donde dice voice.id")
