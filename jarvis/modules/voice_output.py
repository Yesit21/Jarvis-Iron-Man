"""
Módulo de Salida de Voz (Text-to-Speech)
Síntesis de voz usando pyttsx3 y edge-tts
"""
import pyttsx3
import asyncio
import edge_tts
import tempfile
import os
from typing import Optional
import platform


class VoiceOutputModule:
    """Síntesis de voz (TTS)"""
    
    def __init__(self, engine: str = "pyttsx3", language: str = "es", voice_gender: str = "male"):
        """
        Inicializar módulo de síntesis de voz
        
        Args:
            engine: "pyttsx3" (offline) o "edge-tts" (online, mejor calidad)
            language: Código de idioma
            voice_gender: "male" o "female"
        """
        self.engine_type = engine
        self.language = language
        self.voice_gender = voice_gender
        self.tts_engine = None
        
        if engine == "pyttsx3":
            self._init_pyttsx3()
        
        print(f"🔊 Motor TTS inicializado: {engine}")
    
    def _init_pyttsx3(self):
        """Inicializar pyttsx3 (offline)"""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Configurar velocidad
            self.tts_engine.setProperty('rate', 175)  # Palabras por minuto
            
            # Configurar voz
            voices = self.tts_engine.getProperty('voices')
            
            # Intentar encontrar voz en español
            spanish_voice = None
            for voice in voices:
                if 'spanish' in voice.name.lower() or 'es' in voice.languages:
                    if self.voice_gender == "male" and 'male' in voice.name.lower():
                        spanish_voice = voice.id
                        break
                    elif self.voice_gender == "female" and 'female' in voice.name.lower():
                        spanish_voice = voice.id
                        break
            
            if spanish_voice:
                self.tts_engine.setProperty('voice', spanish_voice)
            
            print("✅ pyttsx3 configurado")
            
        except Exception as e:
            print(f"❌ Error inicializando pyttsx3: {e}")
            self.tts_engine = None
    
    def speak(self, text: str, async_mode: bool = False):
        """
        Hablar texto
        
        Args:
            text: Texto a decir
            async_mode: Si es True, no bloquea (solo con pyttsx3)
        """
        if not text:
            return
        
        if self.engine_type == "pyttsx3":
            self._speak_pyttsx3(text, async_mode)
        elif self.engine_type == "edge-tts":
            asyncio.run(self._speak_edge_tts(text))
    
    def _speak_pyttsx3(self, text: str, async_mode: bool = False):
        """Hablar con pyttsx3"""
        if self.tts_engine is None:
            print(f"[JARVIS diría: {text}]")
            return
        
        try:
            self.tts_engine.say(text)
            
            if async_mode:
                # No esperar a que termine
                self.tts_engine.startLoop(False)
                self.tts_engine.iterate()
                self.tts_engine.endLoop()
            else:
                # Esperar a que termine
                self.tts_engine.runAndWait()
                
        except Exception as e:
            print(f"❌ Error hablando: {e}")
            print(f"[JARVIS diría: {text}]")
    
    async def _speak_edge_tts(self, text: str):
        """Hablar con edge-tts (mejor calidad, requiere internet)"""
        try:
            # Seleccionar voz según idioma y género
            if self.language == "es":
                if self.voice_gender == "male":
                    voice = "es-ES-AlvaroNeural"  # Voz masculina española
                else:
                    voice = "es-ES-ElviraNeural"  # Voz femenina española
            else:
                voice = "en-US-GuyNeural"  # Inglés por defecto
            
            # Generar audio
            communicate = edge_tts.Communicate(text, voice)
            
            # Guardar temporalmente
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                tmp_filename = tmp_file.name
            
            await communicate.save(tmp_filename)
            
            # Reproducir (requiere un reproductor de audio)
            self._play_audio_file(tmp_filename)
            
            # Limpiar
            try:
                os.unlink(tmp_filename)
            except:
                pass
                
        except Exception as e:
            print(f"❌ Error con edge-tts: {e}")
            print(f"[JARVIS diría: {text}]")
    
    def _play_audio_file(self, filepath: str):
        """Reproducir archivo de audio"""
        try:
            if platform.system() == "Windows":
                os.system(f'start /min wmplayer "{filepath}"')
            elif platform.system() == "Darwin":  # macOS
                os.system(f'afplay "{filepath}"')
            else:  # Linux
                os.system(f'mpg123 "{filepath}"')
        except Exception as e:
            print(f"❌ Error reproduciendo audio: {e}")
    
    def stop(self):
        """Detener reproducción de voz"""
        if self.tts_engine and self.engine_type == "pyttsx3":
            try:
                self.tts_engine.stop()
            except:
                pass
    
    def set_rate(self, rate: int):
        """
        Ajustar velocidad de habla
        
        Args:
            rate: Palabras por minuto (150-200 normal)
        """
        if self.tts_engine and self.engine_type == "pyttsx3":
            self.tts_engine.setProperty('rate', rate)
    
    def set_volume(self, volume: float):
        """
        Ajustar volumen
        
        Args:
            volume: 0.0 a 1.0
        """
        if self.tts_engine and self.engine_type == "pyttsx3":
            volume = max(0.0, min(1.0, volume))
            self.tts_engine.setProperty('volume', volume)


class VoiceAssistant:
    """Asistente de voz completo (entrada + salida)"""
    
    def __init__(self, voice_input, voice_output, jarvis_instance):
        """
        Args:
            voice_input: VoiceInputModule
            voice_output: VoiceOutputModule
            jarvis_instance: Instancia de Jarvis
        """
        self.input = voice_input
        self.output = voice_output
        self.jarvis = jarvis_instance
        self.enabled = False
    
    def start_voice_assistant(self):
        """Iniciar asistente de voz completo"""
        self.enabled = True
        
        print("\n" + "="*60)
        print("🎤🔊 ASISTENTE DE VOZ COMPLETO ACTIVADO")
        print("="*60)
        print("Di 'Hey Jarvis' para activar")
        print("Di 'Jarvis detente' para salir")
        print("="*60 + "\n")
        
        self.output.speak("Asistente de voz activado. ¿En qué puedo ayudarte?")
        
        def process_with_voice_response(text):
            """Procesar y responder con voz"""
            # Remover palabra de activación
            for wake_word in ["jarvis", "hey jarvis", "oye jarvis"]:
                if text.lower().startswith(wake_word):
                    text = text[len(wake_word):].strip()
                    break
            
            if text:
                # Procesar con JARVIS
                response = self.jarvis.process_input(text)
                
                # Mostrar y hablar respuesta
                print(f"🤖 JARVIS: {response}\n")
                self.output.speak(response)
        
        # Escuchar continuamente
        self.input.listen_continuously(process_with_voice_response)
    
    def single_interaction(self):
        """Una sola interacción de voz"""
        self.output.speak("¿En qué puedo ayudarte?")
        
        text = self.input.listen()
        
        if text:
            # Remover palabra de activación
            for wake_word in ["jarvis", "hey jarvis", "oye jarvis"]:
                if text.lower().startswith(wake_word):
                    text = text[len(wake_word):].strip()
                    break
            
            if text:
                response = self.jarvis.process_input(text)
                print(f"🤖 JARVIS: {response}")
                self.output.speak(response)
                return response
        
        return None
    
    def stop(self):
        """Detener asistente de voz"""
        self.enabled = False
        self.output.stop()
