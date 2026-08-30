"""
Gestor de base de datos SQLite para Jarvis
"""
import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any


class JarvisDatabase:
    """Maneja todas las operaciones de base de datos"""
    
    def __init__(self, db_path: str = "../data/jarvis.db"):
        self.db_path = db_path
        self._ensure_db_directory()
        self._initialize_database()
    
    def _ensure_db_directory(self):
        """Crea el directorio de la BD si no existe"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def _get_connection(self) -> sqlite3.Connection:
        """Obtiene una conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
        return conn
    
    def _initialize_database(self):
        """Crea las tablas si no existen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Tabla de recordatorios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                reminder_date TEXT NOT NULL,
                reminder_time TEXT,
                created_at TEXT NOT NULL,
                completed BOOLEAN DEFAULT 0,
                notified BOOLEAN DEFAULT 0
            )
        """)
        
        # Tabla de eventos del calendario
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calendar_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                event_date TEXT NOT NULL,
                start_time TEXT,
                end_time TEXT,
                description TEXT,
                created_at TEXT NOT NULL,
                completed BOOLEAN DEFAULT 0
            )
        """)
        
        # Tabla de notas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                tags TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Tabla de historial de conversaciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT NOT NULL,
                jarvis_response TEXT NOT NULL,
                intent TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Base de datos inicializada")
    
    # ===== RECORDATORIOS =====
    
    def add_reminder(self, task: str, reminder_date: str, reminder_time: Optional[str] = None) -> int:
        """Agrega un nuevo recordatorio"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO reminders (task, reminder_date, reminder_time, created_at)
            VALUES (?, ?, ?, ?)
        """, (task, reminder_date, reminder_time, datetime.now().isoformat()))
        
        reminder_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return reminder_id
    
    def get_pending_reminders(self) -> List[Dict[str, Any]]:
        """Obtiene todos los recordatorios pendientes"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM reminders 
            WHERE completed = 0 
            ORDER BY reminder_date, reminder_time
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def complete_reminder(self, reminder_id: int):
        """Marca un recordatorio como completado"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE reminders SET completed = 1 WHERE id = ?
        """, (reminder_id,))
        
        conn.commit()
        conn.close()
    
    # ===== CALENDARIO =====
    
    def add_calendar_event(self, title: str, event_date: str, start_time: Optional[str] = None, 
                          end_time: Optional[str] = None, description: Optional[str] = None) -> int:
        """Agrega un evento al calendario"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO calendar_events (title, event_date, start_time, end_time, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, event_date, start_time, end_time, description, datetime.now().isoformat()))
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return event_id
    
    def get_calendar_events(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtiene eventos del calendario en un rango de fechas"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if start_date and end_date:
            cursor.execute("""
                SELECT * FROM calendar_events 
                WHERE event_date BETWEEN ? AND ?
                ORDER BY event_date, start_time
            """, (start_date, end_date))
        else:
            cursor.execute("""
                SELECT * FROM calendar_events 
                ORDER BY event_date, start_time
            """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ===== NOTAS =====
    
    def add_note(self, title: str, content: str, category: str = "general", tags: Optional[str] = None) -> int:
        """Agrega una nueva nota"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO notes (title, content, category, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, content, category, tags, now, now))
        
        note_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return note_id
    
    def search_notes(self, query: str) -> List[Dict[str, Any]]:
        """Busca notas por título o contenido"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM notes 
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY updated_at DESC
        """, (f"%{query}%", f"%{query}%"))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ===== HISTORIAL =====
    
    def log_conversation(self, user_input: str, jarvis_response: str, intent: str):
        """Registra una conversación en el historial"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO conversation_history (user_input, jarvis_response, intent, timestamp)
            VALUES (?, ?, ?, ?)
        """, (user_input, jarvis_response, intent, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()


if __name__ == "__main__":
    # Prueba de la base de datos
    print("🧪 Probando JarvisDatabase...\n")
    
    db = JarvisDatabase("../../data/jarvis.db")
    
    # Prueba de recordatorio
    reminder_id = db.add_reminder("Comprar leche", "2024-12-25", "10:00")
    print(f"✅ Recordatorio creado con ID: {reminder_id}")
    
    # Listar recordatorios
    reminders = db.get_pending_reminders()
    print(f"📋 Recordatorios pendientes: {len(reminders)}")
    for r in reminders:
        print(f"  - {r['task']} - {r['reminder_date']} {r['reminder_time']}")
