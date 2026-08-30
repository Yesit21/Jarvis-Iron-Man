"""
JARVIS Server API
API REST para acceso remoto a JARVIS
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import queue
from datetime import datetime
from colorama import Fore, Style

from core.ollama_client import OllamaClient
from core.intent_router import IntentRouter
from core.database import JarvisDatabase
from core.memory_system import MemorySystem
from core.learning_engine import LearningEngine
from modules.reminders import ReminderModule
import json
import os
import sys


class JarvisServer:
    """Servidor API de JARVIS"""
    
    def __init__(self, config_path="config/settings.json"):
        print(f"{Fore.CYAN}🚀 Inicializando JARVIS Server...{Style.RESET_ALL}")
        
        # Flask app
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'jarvis-secret-key-change-in-production'
        CORS(self.app)  # Permitir CORS para acceso desde otros dispositivos
        
        # WebSocket para comunicación en tiempo real
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Cargar configuración
        self.config = self._load_config(config_path)
        self.prompts = self._load_prompts()
        
        # Inicializar componentes core
        self.ollama = OllamaClient(
            base_url=self.config["ollama"]["base_url"],
            model=self.config["ollama"]["model"]
        )
        
        # Verificar conexión
        if not self.ollama.test_connection():
            print(f"{Fore.RED}❌ Error: No se pudo conectar con Ollama{Style.RESET_ALL}")
            sys.exit(1)
        
        self.db = JarvisDatabase(self.config["database"]["path"])
        self.router = IntentRouter(self.ollama, self.prompts)
        self.memory = MemorySystem()
        self.learning = LearningEngine(self.ollama, self.memory)
        self.reminder_module = ReminderModule(self.db, self.router)
        
        # Cola de tareas asíncronas
        self.task_queue = queue.Queue()
        
        # Registrar rutas
        self._register_routes()
        self._register_socketio_events()
        
        print(f"{Fore.GREEN}✅ JARVIS Server listo{Style.RESET_ALL}\n")
    
    def _load_config(self, config_path):
        """Cargar configuración"""
        full_path = os.path.join(os.path.dirname(__file__), config_path)
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _load_prompts(self):
        """Cargar prompts"""
        prompts_path = os.path.join(os.path.dirname(__file__), "config", "prompts.json")
        with open(prompts_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _register_routes(self):
        """Registrar todas las rutas de la API"""
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Verificar estado del servidor"""
            return jsonify({
                "status": "online",
                "timestamp": datetime.now().isoformat(),
                "model": self.config["ollama"]["model"],
                "ollama_connected": self.ollama.test_connection()
            })
        
        @self.app.route('/api/chat', methods=['POST'])
        def chat():
            """Enviar mensaje a JARVIS"""
            try:
                data = request.get_json()
                user_input = data.get("message", "")
                client_id = data.get("client_id", "unknown")
                
                if not user_input:
                    return jsonify({"error": "No message provided"}), 400
                
                # Procesar entrada
                response = self.process_input(user_input)
                
                # Enviar por WebSocket a todos los clientes conectados
                self.socketio.emit('jarvis_response', {
                    'message': response,
                    'timestamp': datetime.now().isoformat(),
                    'client_id': client_id
                })
                
                return jsonify({
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/memory/stats', methods=['GET'])
        def memory_stats():
            """Obtener estadísticas de memoria"""
            try:
                stats = self.memory.get_memory_stats()
                return jsonify(stats)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/memory/context', methods=['POST'])
        def get_memory_context():
            """Obtener contexto de memoria para una consulta"""
            try:
                data = request.get_json()
                query = data.get("query", "")
                context = self.memory.build_context_from_memory(query)
                return jsonify({"context": context})
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/reminders', methods=['GET'])
        def list_reminders():
            """Listar recordatorios"""
            try:
                response = self.reminder_module.list_reminders()
                return jsonify({"reminders": response})
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/reminders', methods=['POST'])
        def create_reminder():
            """Crear recordatorio"""
            try:
                data = request.get_json()
                user_input = data.get("message", "")
                result = self.reminder_module.process_reminder(user_input)
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/learning/summary', methods=['GET'])
        def learning_summary():
            """Obtener resumen de aprendizaje"""
            try:
                summary = self.learning.get_learning_summary()
                return jsonify({"summary": summary})
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/history', methods=['GET'])
        def conversation_history():
            """Obtener historial de conversaciones"""
            try:
                limit = request.args.get('limit', 50, type=int)
                history = self.db.get_conversation_history(limit=limit)
                return jsonify({"history": history})
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/config', methods=['GET'])
        def get_config():
            """Obtener configuración actual (sin credenciales)"""
            safe_config = self.config.copy()
            # Remover información sensible
            if 'smart_home' in safe_config.get('modules', {}):
                safe_config['modules']['smart_home']['api_token'] = "***"
            return jsonify(safe_config)
    
    def _register_socketio_events(self):
        """Registrar eventos de WebSocket"""
        
        @self.socketio.on('connect')
        def handle_connect():
            print(f"{Fore.GREEN}✅ Cliente conectado: {request.sid}{Style.RESET_ALL}")
            emit('connection_established', {
                'message': 'Conectado a JARVIS',
                'timestamp': datetime.now().isoformat()
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            print(f"{Fore.YELLOW}⚠️ Cliente desconectado: {request.sid}{Style.RESET_ALL}")
        
        @self.socketio.on('message')
        def handle_message(data):
            """Manejar mensajes por WebSocket"""
            try:
                user_input = data.get('message', '')
                response = self.process_input(user_input)
                
                emit('jarvis_response', {
                    'message': response,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                emit('error', {'error': str(e)})
    
    def process_input(self, user_input: str) -> str:
        """
        Procesar entrada del usuario
        (Mismo código que main.py)
        """
        # Comandos especiales
        if user_input.lower() == "¿qué sabes de mí?":
            return self.learning.get_learning_summary()
        
        # Contexto de memoria
        memory_context = self.memory.build_context_from_memory(user_input)
        
        # Clasificar intención
        intent = self.router.classify_intent(user_input)
        
        response = ""
        
        if intent == "RECORDATORIO":
            result = self.reminder_module.process_reminder(user_input)
            response = result["message"]
            
        elif intent == "CONVERSACIÓN":
            system_prompt = self.prompts["system_prompt"]
            if memory_context:
                system_prompt += f"\n\n{memory_context}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
            response = self.ollama.chat(messages)
            
        else:
            response = f"Función '{intent}' detectada pero aún no implementada. Estoy trabajando en ello, señor."
        
        # Aprender y guardar
        self.learning.extract_and_learn(user_input, response, intent)
        self.memory.store_conversation(user_input, response, intent)
        self.db.log_conversation(user_input, response, intent)
        
        return response
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Iniciar servidor"""
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  JARVIS Server API{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Escuchando en: http://{host}:{port}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Modelo: {self.config['ollama']['model']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        self.socketio.run(self.app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


def main():
    """Punto de entrada"""
    import argparse
    
    parser = argparse.ArgumentParser(description='JARVIS Server API')
    parser.add_argument('--host', default='0.0.0.0', help='Host para el servidor')
    parser.add_argument('--port', type=int, default=5000, help='Puerto para el servidor')
    parser.add_argument('--debug', action='store_true', help='Modo debug')
    
    args = parser.parse_args()
    
    try:
        server = JarvisServer()
        server.run(host=args.host, port=args.port, debug=args.debug)
    except Exception as e:
        print(f"{Fore.RED}❌ Error fatal: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
