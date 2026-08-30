"""
Módulo de Búsquedas Web
Permite a JARVIS buscar información en internet en tiempo real
"""
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import json
from typing import List, Dict
from datetime import datetime


class WebSearchModule:
    """Módulo para búsquedas web y scraping"""
    
    def __init__(self):
        self.ddgs = DDGS()
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
    
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Buscar en DuckDuckGo
        
        Args:
            query: Consulta de búsqueda
            max_results: Número máximo de resultados
            
        Returns:
            Lista de resultados con título, url, snippet
        """
        try:
            results = []
            ddgs_results = self.ddgs.text(query, max_results=max_results)
            
            for r in ddgs_results:
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                    "source": "duckduckgo"
                })
            
            return results
            
        except Exception as e:
            return [{"error": f"Error en búsqueda: {str(e)}"}]
    
    def search_news(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Buscar noticias recientes
        
        Args:
            query: Consulta de búsqueda
            max_results: Número máximo de resultados
            
        Returns:
            Lista de noticias
        """
        try:
            results = []
            news_results = self.ddgs.news(query, max_results=max_results)
            
            for r in news_results:
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("body", ""),
                    "date": r.get("date", ""),
                    "source": r.get("source", ""),
                    "type": "news"
                })
            
            return results
            
        except Exception as e:
            return [{"error": f"Error en búsqueda de noticias: {str(e)}"}]
    
    def get_weather(self, location: str = "auto") -> Dict:
        """
        Obtener clima actual
        
        Args:
            location: Ubicación (ciudad o "auto" para detectar)
            
        Returns:
            Información del clima
        """
        try:
            # Usar wttr.in - servicio simple sin API key
            if location == "auto":
                url = "https://wttr.in/?format=j1"
            else:
                url = f"https://wttr.in/{location}?format=j1"
            
            response = self.session.get(url, timeout=10)
            data = response.json()
            
            current = data["current_condition"][0]
            
            return {
                "location": location,
                "temperature_c": current["temp_C"],
                "temperature_f": current["temp_F"],
                "description": current["weatherDesc"][0]["value"],
                "humidity": current["humidity"],
                "wind_speed": current["windspeedKmph"],
                "feels_like_c": current["FeelsLikeC"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Error obteniendo clima: {str(e)}"}
    
    def fetch_webpage_content(self, url: str, max_length: int = 2000) -> str:
        """
        Obtener contenido de una página web
        
        Args:
            url: URL de la página
            max_length: Longitud máxima del texto
            
        Returns:
            Contenido de texto de la página
        """
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remover scripts y estilos
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extraer texto
            text = soup.get_text()
            
            # Limpiar
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limitar longitud
            if len(text) > max_length:
                text = text[:max_length] + "..."
            
            return text
            
        except Exception as e:
            return f"Error al obtener contenido: {str(e)}"
    
    def quick_answer(self, query: str) -> str:
        """
        Intentar obtener una respuesta rápida para preguntas simples
        
        Args:
            query: Pregunta
            
        Returns:
            Respuesta o vacío si no hay respuesta directa
        """
        try:
            # DuckDuckGo Instant Answer API
            results = self.ddgs.answers(query)
            
            if results:
                for result in results:
                    if "text" in result:
                        return result["text"]
            
            return ""
            
        except Exception:
            return ""
    
    def search_and_summarize(self, query: str, ollama_client=None) -> str:
        """
        Buscar en web y generar resumen con IA
        
        Args:
            query: Consulta
            ollama_client: Cliente de Ollama para generar resumen
            
        Returns:
            Resumen de resultados
        """
        # Intentar respuesta rápida primero
        quick = self.quick_answer(query)
        if quick:
            return quick
        
        # Buscar
        results = self.search(query, max_results=3)
        
        if not results or "error" in results[0]:
            return "No pude encontrar información sobre eso en este momento."
        
        # Construir contexto para el LLM
        context = f"Pregunta del usuario: {query}\n\n"
        context += "Resultados de búsqueda:\n\n"
        
        for i, result in enumerate(results, 1):
            context += f"{i}. {result['title']}\n"
            context += f"   {result['snippet']}\n\n"
        
        # Si hay cliente Ollama, generar resumen
        if ollama_client:
            prompt = f"{context}\n\nCon base en estos resultados, responde la pregunta del usuario de forma clara y concisa:"
            
            messages = [
                {"role": "system", "content": "Eres JARVIS, asistente de Iron Man. Responde de forma clara y directa basándote en la información proporcionada."},
                {"role": "user", "content": prompt}
            ]
            
            return ollama_client.chat(messages)
        else:
            # Sin LLM, solo retornar los resultados formateados
            response = f"Encontré esto sobre '{query}':\n\n"
            for i, result in enumerate(results, 1):
                response += f"{i}. {result['title']}\n   {result['snippet']}\n\n"
            return response
    
    def get_youtube_results(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Buscar videos en YouTube (vía DuckDuckGo)
        
        Args:
            query: Consulta de búsqueda
            max_results: Número máximo de resultados
            
        Returns:
            Lista de videos
        """
        try:
            results = []
            video_results = self.ddgs.videos(f"{query} site:youtube.com", max_results=max_results)
            
            for r in video_results:
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("content", ""),
                    "thumbnail": r.get("image", ""),
                    "duration": r.get("duration", ""),
                    "type": "video"
                })
            
            return results
            
        except Exception as e:
            return [{"error": f"Error en búsqueda de videos: {str(e)}"}]


class WebQueryRouter:
    """Router para clasificar y procesar consultas web"""
    
    def __init__(self, web_search_module: WebSearchModule, ollama_client=None):
        self.web = web_search_module
        self.ollama = ollama_client
    
    def process_web_query(self, query: str) -> str:
        """
        Procesar una consulta web
        
        Args:
            query: Consulta del usuario
            
        Returns:
            Respuesta generada
        """
        query_lower = query.lower()
        
        # Clima
        if any(word in query_lower for word in ["clima", "tiempo", "temperatura", "llueve"]):
            # Extraer ubicación si se menciona
            location = "auto"
            # TODO: Mejorar extracción de ubicación
            
            weather = self.web.get_weather(location)
            if "error" not in weather:
                return (f"El clima actual es {weather['description']} con "
                       f"{weather['temperature_c']}°C (se siente como {weather['feels_like_c']}°C). "
                       f"Humedad: {weather['humidity']}%, Viento: {weather['wind_speed']} km/h")
            else:
                return weather["error"]
        
        # Noticias
        elif any(word in query_lower for word in ["noticias", "noticia", "últimas noticias"]):
            # Extraer tema si hay
            topic = query_lower.replace("noticias", "").replace("noticia", "").replace("últimas", "").strip()
            if not topic:
                topic = "noticias"
            
            news = self.web.search_news(topic, max_results=5)
            if news and "error" not in news[0]:
                response = "📰 Últimas noticias:\n\n"
                for i, article in enumerate(news[:5], 1):
                    response += f"{i}. {article['title']}\n   Fuente: {article.get('source', 'N/A')}\n\n"
                return response
            else:
                return "No pude obtener las noticias en este momento."
        
        # Videos de YouTube
        elif any(word in query_lower for word in ["video", "youtube", "tutorial"]):
            search_query = query_lower.replace("video", "").replace("youtube", "").replace("tutorial", "").strip()
            if search_query:
                videos = self.web.get_youtube_results(search_query, max_results=3)
                if videos and "error" not in videos[0]:
                    response = f"🎥 Videos sobre '{search_query}':\n\n"
                    for i, video in enumerate(videos, 1):
                        response += f"{i}. {video['title']}\n   {video['url']}\n\n"
                    return response
        
        # Búsqueda general con resumen
        else:
            return self.web.search_and_summarize(query, self.ollama)
