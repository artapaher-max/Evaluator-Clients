from flask import Flask, request, session, redirect, url_for, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .config import Config
from datetime import datetime, timedelta

# Inicializa el limiter pero sin asociarlo a una app todavía
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="redis://localhost:6379" # storage_uri="memory://" # Usa 'redis://localhost:6379' si tienes Redis instalado
)

def create_app():
    """
    Factory function para crear y configurar la aplicación Flask.
    """
    app = Flask(__name__)
    
    # 1. Cargar la configuración desde el objeto Config
    app.config.from_object(Config)
    
    # leer jasons como utf-8
    app.config['JSON_AS_ASCII'] = False
    
    # para no bloquearme a mi mismo si lo intent mucho
    app.config['LIMITER_EXEMPT_WHEN'] = lambda: request.remote_addr in ('127.0.0.1', '172.30.1.108', '0.0.0.0')
    
    # Timeout despues de 20 min
    app.permanent_session_lifetime = app.config['PERMANENT_SESSION_LIFETIME']

    @app.before_request
    def before_request_check():
        # Hacemos la sesión "permanente" para que respete el tiempo de vida
        session.permanent = True
        
        # Solo verificamos si el usuario está logueado
        if 'logged_in' in session:
            # No aplicamos el timeout a la ruta de logout
            if request.endpoint and 'logout' in request.endpoint:
                return

            last_activity_str = session.get('last_activity')
            
            if last_activity_str:
                last_activity = datetime.fromisoformat(last_activity_str)
                now = datetime.utcnow()
                
                # Si ha pasado más tiempo del permitido
                if now - last_activity > app.permanent_session_lifetime:
                    session.clear() # Limpiar la sesión
                    
                    # Si la petición es de JavaScript (AJAX), devolver un error JSON
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify(error="SESSION_TIMEOUT", message="Tu sesión ha expirado."), 401
                    
                    # Si es una petición normal del navegador, redirigir al login
                    # Apunta a la ruta 'home' del blueprint 'main'
                    return redirect(url_for('main.home'))
            
            # Si la sesión es válida, actualizamos la marca de tiempo de la última actividad
            session['last_activity'] = datetime.utcnow().isoformat()
    
    # 2. Inicializar extensiones
    limiter.init_app(app)

    # 3. Registrar los Blueprints (módulos de la aplicación)
    from .main.routes import main_bp
    app.register_blueprint(main_bp)

    from .auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    from .admin.routes import admin_bp
    app.register_blueprint(admin_bp)

    from .evaluation.routes import evaluation_bp
    app.register_blueprint(evaluation_bp)

    return app
