"""
Voz estilo JARVIS de Iron Man
Configuración optimizada para sonar como Paul Bettany
"""
import pyttsx3
import platform


class JarvisVoice:
    """Voz personalizada estilo JARVIS"""
    
    def __init__(self):
        self.engine = pyttsx3.init()
        self._configure_voice()
    
    def _configure_voice(self):
        """Configurar voz para sonar como JARVIS"""
        
        # Velocidad: JARVIS habla con calma pero eficiencia
        # 175 es óptimo (no muy rápido, no muy lento)
        self.engine.setProperty('rate', 175)
        
        # Volumen: claro pero no agresivo
        self.engine.setProperty('volume', 0.9)
        
        # Seleccionar voz británica/formal si está disponible
        voices = self.engine.getProperty('voices')
        
        # Buscar voz masculina británica/formal
        jarvis_voice = None
        
        for voice in voices:
            voice_name = voice.name.lower()
            
            # Prioridad 1: Voces británicas
            if 'david' in voice_name or 'george' in voice_name or 'hazel' in voice_name:
                jarvis_voice = voice.id
                break
            
            # Prioridad 2: Voces formales en inglés
            elif 'zira' in voice_name or 'mark' in voice_name:
                jarvis_voice = voice.id
                break
        
        # Si encontramos una voz adecuada, usarla
        if jarvis_voice:
            self.engine.setProperty('voice', jarvis_voice)
            print("✅ Voz estilo JARVIS configurada")
        else:
            print("⚠️ Usando voz por defecto")
    
    def speak(self, text: str, wait: bool = True):
        """
        Hablar texto con voz de JARVIS
        
        Args:
            text: Texto a decir
            wait: Si True, espera a terminar antes de continuar
        """
        if not text:
            return
        
        self.engine.say(text)
        
        if wait:
            self.engine.runAndWait()
        else:
            # Modo asíncrono (no bloquea)
            self.engine.startLoop(False)
            self.engine.iterate()
            self.engine.endLoop()
    
    def stop(self):
        """Detener reproducción"""
        try:
            self.engine.stop()
        except:
            pass
    
    def list_available_voices(self):
        """Listar todas las voces disponibles en el sistema"""
        voices = self.engine.getProperty('voices')
        
        print("\n🎤 Voces disponibles en tu sistema:\n")
        for i, voice in enumerate(voices, 1):
            print(f"{i}. {voice.name}")
            print(f"   ID: {voice.id}")
            print(f"   Idiomas: {voice.languages}")
            print()
    
    def set_voice_by_index(self, index: int):
        """
        Cambiar voz por índice
        
        Args:
            index: Número de voz (ver list_available_voices)
        """
        voices = self.engine.getProperty('voices')
        
        if 0 <= index < len(voices):
            self.engine.setProperty('voice', voices[index].id)
            print(f"✅ Voz cambiada a: {voices[index].name}")
        else:
            print("❌ Índice inválido")
    
    def test_voice(self):
        """Probar la voz actual"""
        test_phrases = [
            "Buenos días, señor. Soy JARVIS.",
            "Todos los sistemas operativos.",
            "¿En qué puedo ayudarte hoy?",
            "A sus órdenes, señor."
        ]
        
        print("\n🎤 Probando voz de JARVIS...\n")
        for phrase in test_phrases:
            print(f"   > {phrase}")
            self.speak(phrase, wait=True)
            import time
            time.sleep(0.5)


# Frases características de JARVIS
JARVIS_PHRASES = {
    "startup": [
        "Buenos días, señor. Soy JARVIS.",
        "Sistemas iniciados. A sus órdenes.",
        "JARVIS en línea. ¿En qué puedo ayudarte?",
    ],
    "listening": [
        "Escuchando, señor.",
        "Te escucho.",
        "Adelante.",
    ],
    "processing": [
        "Un momento, señor.",
        "Procesando...",
        "Déjame verificar eso.",
    ],
    "error": [
        "Disculpe, señor, pero no entendí eso.",
        "Necesitaré más información.",
        "No pude procesar esa solicitud.",
    ],
    "goodbye": [
        "Hasta pronto, señor.",
        "Siempre a sus órdenes.",
        "Nos vemos, señor.",
    ]
}


def test_jarvis_voice():
    """Función de prueba"""
    print("="*60)
    print("  JARVIS Voice Configuration Test")
    print("="*60)
    
    jarvis = JarvisVoice()
    
    # Listar voces disponibles
    jarvis.list_available_voices()
    
    # Probar voz
    jarvis.test_voice()
    
    # Menú interactivo
    print("\n" + "="*60)
    print("Comandos:")
    print("  1-9: Cambiar a esa voz")
    print("  test: Probar voz actual")
    print("  exit: Salir")
    print("="*60)
    
    while True:
        cmd = input("\nComando: ").strip().lower()
        
        if cmd == "exit":
            break
        elif cmd == "test":
            jarvis.test_voice()
        elif cmd.isdigit():
            jarvis.set_voice_by_index(int(cmd) - 1)
            jarvis.speak("Esta es mi nueva voz.")
        else:
            jarvis.speak(cmd)


if __name__ == "__main__":
    test_jarvis_voice()
