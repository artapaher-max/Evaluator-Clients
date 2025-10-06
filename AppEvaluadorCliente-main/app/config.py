import os
from dotenv import load_dotenv
from datetime import timedelta
import socket


# Cargar variables de entorno desde el archivo .env
load_dotenv()

class Config:
    """Clase de configuración para la aplicación Flask."""
    
    # Clave secreta para la sesión de Flask
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "una_clave_secreta_por_defecto_muy_segura")

    # Credenciales de APIs
    GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
    SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID")
    SHEETS_CREDENTIALS_PATH = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
    
    # Credenciales de correo
    GMAIL_USER = os.getenv("EMAIL_HOST_USER")
    GMAIL_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
    
    # Roles de administrador (limpia espacios en blanco)
    ADMIN_POSITIONS = [pos.strip() for pos in os.getenv("ADMIN_POSITIONS", "").split(',')]
    
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=20)
    
    # NAMEHOST = socket.gethostname()
    # HOST = socket.gethostbyname(NAMEHOST)
    
    # PORT = 5000