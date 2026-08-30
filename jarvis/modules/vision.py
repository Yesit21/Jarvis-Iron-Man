"""
Módulo de Visión
Análisis de imágenes y video usando IA
"""
from PIL import Image
import base64
import io
import requests
from typing import Optional, Dict, List
import cv2
import numpy as np


class VisionModule:
    """Módulo de visión por computadora"""
    
    def __init__(self, ollama_base_url: str = "http://localhost:11434"):
        """
        Inicializar módulo de visión
        
        Args:
            ollama_base_url: URL base de Ollama
        """
        self.ollama_url = ollama_base_url
        self.vision_model = "llava"  # Modelo multimodal de Ollama
    
    def analyze_image(self, image_path: str, question: str = "¿Qué ves en esta imagen?") -> str:
        """
        Analizar una imagen con IA
        
        Args:
            image_path: Ruta de la imagen
            question: Pregunta sobre la imagen
            
        Returns:
            Descripción/respuesta de la IA
        """
        try:
            # Cargar y convertir imagen a base64
            with Image.open(image_path) as img:
                # Redimensionar si es muy grande
                max_size = 800
                if img.width > max_size or img.height > max_size:
                    img.thumbnail((max_size, max_size))
                
                # Convertir a base64
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Enviar a Ollama con modelo de visión
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.vision_model,
                    "prompt": question,
                    "images": [img_base64],
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No pude analizar la imagen")
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error analizando imagen: {str(e)}"
    
    def analyze_image_url(self, url: str, question: str = "¿Qué ves en esta imagen?") -> str:
        """
        Analizar imagen desde URL
        
        Args:
            url: URL de la imagen
            question: Pregunta sobre la imagen
            
        Returns:
            Descripción/respuesta
        """
        try:
            # Descargar imagen
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            # Guardar temporalmente
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name
            
            # Analizar
            result = self.analyze_image(tmp_path, question)
            
            # Limpiar
            import os
            try:
                os.unlink(tmp_path)
            except:
                pass
            
            return result
            
        except Exception as e:
            return f"Error descargando/analizando imagen: {str(e)}"
    
    def detect_objects(self, image_path: str) -> List[Dict]:
        """
        Detectar objetos en una imagen
        
        Args:
            image_path: Ruta de la imagen
            
        Returns:
            Lista de objetos detectados
        """
        # Usar el modelo de visión para describir objetos
        prompt = "Lista todos los objetos que ves en esta imagen, uno por línea"
        response = self.analyze_image(image_path, prompt)
        
        # Parsear respuesta en lista
        objects = []
        for line in response.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                objects.append({"name": line, "confidence": 0.9})
        
        return objects
    
    def describe_scene(self, image_path: str) -> str:
        """
        Describir la escena completa
        
        Args:
            image_path: Ruta de la imagen
            
        Returns:
            Descripción detallada
        """
        prompt = "Describe esta imagen en detalle: escenario, personas, objetos, colores, ambiente"
        return self.analyze_image(image_path, prompt)
    
    def read_text_from_image(self, image_path: str) -> str:
        """
        OCR - Extraer texto de imagen
        
        Args:
            image_path: Ruta de la imagen
            
        Returns:
            Texto encontrado
        """
        prompt = "¿Qué texto aparece en esta imagen? Transcríbelo exactamente"
        return self.analyze_image(image_path, prompt)
    
    def capture_from_webcam(self, save_path: str = "webcam_capture.jpg") -> Dict:
        """
        Capturar imagen desde webcam
        
        Args:
            save_path: Donde guardar la captura
            
        Returns:
            Resultado de la operación
        """
        try:
            # Abrir webcam
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                return {
                    "success": False,
                    "message": "No se pudo acceder a la webcam"
                }
            
            # Capturar frame
            ret, frame = cap.read()
            
            if ret:
                # Guardar imagen
                cv2.imwrite(save_path, frame)
                cap.release()
                
                return {
                    "success": True,
                    "message": f"Imagen capturada en {save_path}",
                    "path": save_path
                }
            else:
                cap.release()
                return {
                    "success": False,
                    "message": "Error capturando imagen"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    def analyze_webcam(self, question: str = "¿Qué ves?") -> str:
        """
        Capturar y analizar imagen de webcam
        
        Args:
            question: Pregunta sobre lo que ve
            
        Returns:
            Respuesta del análisis
        """
        # Capturar
        result = self.capture_from_webcam()
        
        if result["success"]:
            # Analizar
            analysis = self.analyze_image(result["path"], question)
            
            # Limpiar archivo temporal
            try:
                import os
                os.unlink(result["path"])
            except:
                pass
            
            return analysis
        else:
            return result["message"]
    
    def compare_images(self, image1_path: str, image2_path: str) -> str:
        """
        Comparar dos imágenes
        
        Args:
            image1_path: Primera imagen
            image2_path: Segunda imagen
            
        Returns:
            Análisis de similitudes/diferencias
        """
        # Por ahora, usar el modelo de visión dos veces
        desc1 = self.describe_scene(image1_path)
        desc2 = self.describe_scene(image2_path)
        
        comparison = f"Imagen 1: {desc1}\n\nImagen 2: {desc2}\n\n"
        comparison += "Análisis: " + self._compare_descriptions(desc1, desc2)
        
        return comparison
    
    def _compare_descriptions(self, desc1: str, desc2: str) -> str:
        """Comparar dos descripciones (simple)"""
        # Encontrar palabras comunes y diferentes
        words1 = set(desc1.lower().split())
        words2 = set(desc2.lower().split())
        
        common = words1.intersection(words2)
        unique1 = words1 - words2
        unique2 = words2 - words1
        
        result = f"Elementos comunes: {len(common)}, "
        result += f"Únicos en imagen 1: {len(unique1)}, "
        result += f"Únicos en imagen 2: {len(unique2)}"
        
        return result
    
    def is_vision_model_available(self) -> bool:
        """
        Verificar si el modelo de visión está disponible
        
        Returns:
            True si está disponible
        """
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(self.vision_model in model.get("name", "") for model in models)
            return False
        except:
            return False


class VisionCommandRouter:
    """Router para comandos de visión"""
    
    def __init__(self, vision_module: VisionModule):
        self.vision = vision_module
    
    def process_vision_command(self, command: str, image_path: str = None) -> str:
        """
        Procesar comando de visión
        
        Args:
            command: Comando en lenguaje natural
            image_path: Ruta de imagen (opcional si usa webcam)
            
        Returns:
            Respuesta
        """
        cmd_lower = command.lower()
        
        # Verificar si el modelo está disponible
        if not self.vision.is_vision_model_available():
            return (f"El modelo de visión '{self.vision.vision_model}' no está instalado. "
                   f"Instálalo con: ollama pull {self.vision.vision_model}")
        
        # Capturar desde webcam
        if "webcam" in cmd_lower or "cámara" in cmd_lower or "mírame" in cmd_lower:
            question = command
            # Remover palabras clave
            for word in ["webcam", "cámara", "mírame", "mira"]:
                question = question.lower().replace(word, "").strip()
            
            if not question:
                question = "¿Qué ves?"
            
            return self.vision.analyze_webcam(question)
        
        # Analizar imagen proporcionada
        elif image_path:
            if "describe" in cmd_lower or "qué ves" in cmd_lower:
                return self.vision.describe_scene(image_path)
            
            elif "texto" in cmd_lower or "leer" in cmd_lower or "ocr" in cmd_lower:
                return self.vision.read_text_from_image(image_path)
            
            elif "objetos" in cmd_lower or "detecta" in cmd_lower:
                objects = self.vision.detect_objects(image_path)
                if objects:
                    result = "🔍 Objetos detectados:\n\n"
                    for obj in objects:
                        result += f"• {obj['name']}\n"
                    return result
                else:
                    return "No detecté objetos específicos"
            
            else:
                # Pregunta genérica sobre la imagen
                return self.vision.analyze_image(image_path, command)
        
        else:
            return "Necesito una imagen o acceso a la webcam para análisis visual"
