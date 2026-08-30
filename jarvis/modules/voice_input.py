"""
Módulo de Entrada de Voz
Reconocimiento de voz usando Whisper de OpenAI
"""
import speech_recognition as sr
import whisper
import tempfile
import os
from typing import Optional, Dict
import numpy as np


class VoiceInputModule:
    """Reconocimiento de voz"""
    
    def __init__(self, model_size: str = "base", language: str = "es"):
        """
        Inicializar módulo de voz
        
        Args:
            model_size: tiny, base, small, medium, large
            language: Código de idioma (es, en, etc)
        """
        self.language = language
        self.model_size = model_size
        self.model = None
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Ajustar para ruido ambiente
        print("🎤 Calibrando micrófono...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✅ Micrófono listo")
    
    def _load_whisper_model(self):
        """Cargar modelo de Whisper (lazy loading)"""
        if self.model is None:
            print(f"📥 Cargando modelo Whisper ({self.model_size})...")
            self.model = whisper.load_model(self.model_size)
            print("✅ Modelo Whisper cargado")
    
    def listen(self, timeout: int = 5, phrase_time_limit: int = 10) -> Optional[str]:
        """
        Escuchar desde el micrófono
        
        Args:
            timeout: Tiempo máximo esperando que el usuario hable
            phrase_time_limit: Tiempo máximo de grabación
            
        Returns:
            Texto reconocido o None
        """
        try:
            with self.microphone as source:
                print("🎤 Escuchando...")
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
            
            print("🔄 Procesando...")
            
            # Intentar con Google Speech Recognition (rápido, requiere internet)
            try:
                text = self.recognizer.recognize_google(audio, language=self.language)
                return text
            except sr.UnknownValueError:
                # Si Google falla, intentar con Whisper (más lento, pero offline)
                return self._transcribe_with_whisper(audio)
            
        except sr.WaitTimeoutError:
            print("⏱️ Tiempo de espera agotado")
            return None
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None
    
    def _transcribe_with_whisper(self, audio) -> Optional[str]:
        """
        Transcribir audio con Whisper
        
        Args:
            audio: Objeto AudioData de speech_recognition
            
        Returns:
            Texto transcrito
        """
        try:
            self._load_whisper_model()
            
            # Guardar audio temporal
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_filename = tmp_file.name
                with open(tmp_filename, "wb") as f:
                    f.write(audio.get_wav_data())
            
            # Transcribir con Whisper
            result = self.model.transcribe(tmp_filename, language=self.language)
            
            # Limpiar archivo temporal
            os.unlink(tmp_filename)
            
            return result["text"].strip()
            
        except Exception as e:
            print(f"❌ Error con Whisper: {str(e)}")
            return None
    
    def listen_continuously(self, callback, stop_phrases=None):
        """
        Escuchar continuamente y ejecutar callback con cada frase
        
        Args:
            callback: Función a ejecutar con el texto reconocido
            stop_phrases: Lista de frases para detener la escucha
        """
        if stop_phrases is None:
            stop_phrases = ["jarvis detente", "jarvis stop", "jarvis para"]
        
        print("🎤 Escucha continua activada")
        print(f"   Frases de parada: {', '.join(stop_phrases)}")
        
        while True:
            text = self.listen(timeout=10)
            
            if text:
                print(f"👤 Usuario: {text}")
                
                # Verificar si es frase de parada
                if any(phrase in text.lower() for phrase in stop_phrases):
                    print("⏹️ Deteniendo escucha continua")
                    break
                
                # Ejecutar callback
                callback(text)
    
    def is_wake_word_detected(self, text: str, wake_words=None) -> bool:
        """
        Detectar palabra de activación
        
        Args:
            text: Texto a verificar
            wake_words: Lista de palabras de activación
            
        Returns:
            True si se detectó palabra de activación
        """
        if wake_words is None:
            wake_words = ["jarvis", "hey jarvis", "oye jarvis"]
        
        text_lower = text.lower()
        return any(word in text_lower for word in wake_words)
    
    def listen_for_wake_word(self, wake_words=None, timeout: int = 30):
        """
        Esperar por palabra de activación
        
        Args:
            wake_words: Palabras de activación
            timeout: Tiempo máximo de espera
            
        Returns:
            True si se detectó palabra de activación
        """
        print("👂 Esperando palabra de activación...")
        
        text = self.listen(timeout=timeout)
        
        if text and self.is_wake_word_detected(text, wake_words):
            print("✅ Palabra de activación detectada")
            return True
        
        return False


class VoiceCommandRouter:
    """Router para comandos de voz"""
    
    def __init__(self, voice_input: VoiceInputModule, jarvis_instance):
        self.voice = voice_input
        self.jarvis = jarvis_instance
    
    def start_voice_mode(self):
        """Iniciar modo de voz interactivo"""
        print("\n" + "="*60)
        print("🎤 MODO DE VOZ ACTIVADO")
        print("="*60)
        print("Di 'Jarvis' para activar, luego tu comando")
        print("Di 'Jarvis detente' para salir del modo de voz")
        print("="*60 + "\n")
        
        def process_voice_command(text):
            """Procesar comando de voz"""
            # Remover palabra de activación si está presente
            for wake_word in ["jarvis", "hey jarvis", "oye jarvis"]:
                if text.lower().startswith(wake_word):
                    text = text[len(wake_word):].strip()
            
            if text:
                # Enviar a JARVIS
                response = self.jarvis.process_input(text)
                print(f"🤖 JARVIS: {response}\n")
        
        # Escuchar continuamente
        self.voice.listen_continuously(process_voice_command)
    
    def single_voice_command(self) -> Optional[str]:
        """
        Escuchar un solo comando de voz
        
        Returns:
            Texto reconocido
        """
        print("🎤 Di tu comando...")
        text = self.voice.listen()
        
        if text:
            # Remover palabra de activación si está
            for wake_word in ["jarvis", "hey jarvis", "oye jarvis"]:
                if text.lower().startswith(wake_word):
                    text = text[len(wake_word):].strip()
                    break
            
            return text if text else None
        
        return None
