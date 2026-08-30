"""
Script de prueba rápida para el servidor JARVIS
Ejecuta esto para verificar que el servidor funciona correctamente
"""
import requests
import time
from colorama import init, Fore, Style

init()

SERVER_URL = "http://localhost:5000"

def test_health():
    """Probar endpoint de salud"""
    print(f"\n{Fore.CYAN}🔍 Probando /api/health...{Style.RESET_ALL}")
    try:
        response = requests.get(f"{SERVER_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"{Fore.GREEN}✅ Servidor online{Style.RESET_ALL}")
            print(f"   Modelo: {data['model']}")
            print(f"   Ollama: {'✅ Conectado' if data['ollama_connected'] else '❌ Desconectado'}")
            return True
        else:
            print(f"{Fore.RED}❌ Error: {response.status_code}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
        return False

def test_chat():
    """Probar endpoint de chat"""
    print(f"\n{Fore.CYAN}🔍 Probando /api/chat...{Style.RESET_ALL}")
    try:
        response = requests.post(
            f"{SERVER_URL}/api/chat",
            json={"message": "Hola JARVIS, ¿cómo estás?"},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"{Fore.GREEN}✅ Chat funcionando{Style.RESET_ALL}")
            print(f"   Respuesta: {data['response'][:100]}...")
            return True
        else:
            print(f"{Fore.RED}❌ Error: {response.status_code}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
        return False

def test_memory():
    """Probar endpoint de memoria"""
    print(f"\n{Fore.CYAN}🔍 Probando /api/memory/stats...{Style.RESET_ALL}")
    try:
        response = requests.get(f"{SERVER_URL}/api/memory/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"{Fore.GREEN}✅ Memoria funcionando{Style.RESET_ALL}")
            print(f"   Conversaciones: {data.get('total_conversations', 0)}")
            print(f"   Hechos: {data.get('user_facts', 0)}")
            return True
        else:
            print(f"{Fore.RED}❌ Error: {response.status_code}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  JARVIS Server - Pruebas de Funcionalidad{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"\nServidor: {SERVER_URL}")
    
    results = []
    
    # Prueba 1: Health Check
    results.append(("Health Check", test_health()))
    time.sleep(1)
    
    # Prueba 2: Chat
    results.append(("Chat", test_chat()))
    time.sleep(1)
    
    # Prueba 3: Memoria
    results.append(("Memoria", test_memory()))
    
    # Resumen
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  Resumen de Pruebas{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Fore.GREEN}✅ PASS" if result else f"{Fore.RED}❌ FAIL"
        print(f"{status}{Style.RESET_ALL} - {name}")
    
    print(f"\n{Fore.CYAN}Total: {passed}/{total} pruebas pasadas{Style.RESET_ALL}\n")
    
    if passed == total:
        print(f"{Fore.GREEN}🎉 ¡Todas las pruebas pasaron!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}El servidor está listo para usar{Style.RESET_ALL}\n")
    else:
        print(f"{Fore.YELLOW}⚠️ Algunas pruebas fallaron{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Verifica que el servidor esté corriendo y que Ollama esté activo{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main()
