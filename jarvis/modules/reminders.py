"""
Módulo de Recordatorios
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import re


class ReminderModule:
    """Gestiona recordatorios con lenguaje natural"""
    
    def __init__(self, database, intent_router):
        self.db = database
        self.router = intent_router
    
    def process_reminder(self, user_input: str) -> Dict[str, Any]:
        """
        Procesa una solicitud de recordatorio
        
        Returns:
            Dict con 'success', 'message', 'reminder_id'
        """
        # Extraer datos usando IA
        data = self.router.extract_reminder_data(user_input)
        
        if not data:
            return {
                "success": False,
                "message": "No pude entender el recordatorio. Intenta de nuevo."
            }
        
        # Procesar fecha
        fecha = self._parse_date(data.get("fecha", "hoy"))
        if not fecha:
            return {
                "success": False,
                "message": "No pude interpretar la fecha del recordatorio."
            }
        
        # Guardar en BD
        try:
            reminder_id = self.db.add_reminder(
                task=data.get("tarea", "Sin descripción"),
                reminder_date=fecha,
                reminder_time=data.get("hora")
            )
            
            # Generar confirmación natural
            action_desc = f"recordatorio '{data.get('tarea')}' para {fecha}"
            if data.get("hora"):
                action_desc += f" a las {data.get('hora')}"
            
            confirmation = self.router.generate_confirmation(action_desc)
            
            return {
                "success": True,
                "message": confirmation,
                "reminder_id": reminder_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al guardar el recordatorio: {str(e)}"
            }
    
    def list_reminders(self) -> str:
        """Lista todos los recordatorios pendientes"""
        reminders = self.db.get_pending_reminders()
        
        if not reminders:
            return "No tienes recordatorios pendientes, señor."
        
        response = f"Tienes {len(reminders)} recordatorio(s) pendiente(s):\n\n"
        
        for i, reminder in enumerate(reminders, 1):
            time_str = f" a las {reminder['reminder_time']}" if reminder['reminder_time'] else ""
            response += f"{i}. {reminder['task']} - {reminder['reminder_date']}{time_str}\n"
        
        return response.strip()
    
    def complete_reminder(self, reminder_id: int) -> str:
        """Marca un recordatorio como completado"""
        try:
            self.db.complete_reminder(reminder_id)
            return "Recordatorio marcado como completado."
        except Exception as e:
            return f"Error al completar el recordatorio: {str(e)}"
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Convierte expresiones de fecha a formato YYYY-MM-DD
        Soporta: hoy, mañana, YYYY-MM-DD
        """
        date_str = date_str.lower().strip()
        today = datetime.now()
        
        if date_str == "hoy":
            return today.strftime("%Y-%m-%d")
        elif date_str == "mañana":
            tomorrow = today + timedelta(days=1)
            return tomorrow.strftime("%Y-%m-%d")
        elif re.match(r"\d{4}-\d{2}-\d{2}", date_str):
            # Ya está en formato correcto
            return date_str
        else:
            # Intentar parsear otros formatos
            try:
                parsed = datetime.strptime(date_str, "%d/%m/%Y")
                return parsed.strftime("%Y-%m-%d")
            except:
                return None


if __name__ == "__main__":
    print("🧪 Módulo de Recordatorios cargado correctamente")
