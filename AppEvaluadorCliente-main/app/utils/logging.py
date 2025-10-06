from datetime import datetime
import os

def log_sesion(correo, exito):
    """Registra los intentos de inicio de sesión."""
    # Construye la ruta al archivo de log desde la raíz del proyecto
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    log_file = os.path.join(base_path, 'log_sesiones.txt')
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    estado = "exito" if exito else "Fallo"
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] - Intento de inicio de sesion de: {correo} - Estado: {estado}\n")
    except Exception as e:
        print(f"Error al escribir en log_sesiones.txt: {e}")

def log_evaluacion(evaluador, nombre_cliente, conclusion_gemini):
    """Registra las evaluaciones de clientes."""
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    log_file = os.path.join(base_path, 'log_evaluaciones.txt')
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] - Evaluador: {evaluador}, Cliente: {nombre_cliente}\n")
            f.write(f"--- Conclusion de Gemini ---\n{conclusion_gemini}\n\n")
    except Exception as e:
        print(f"Error al escribir en log_evaluaciones.txt: {e}")
        
def log_admin_action(admin_email, action):
    """Registra una acción realizada en el panel de administración."""
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    log_file = os.path.join(base_path, 'log_admin.txt')
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] - Admin: {admin_email} - Accion: {action}\n")
    except Exception as e:
        print(f"Error al escribir en log_admin.txt: {e}")