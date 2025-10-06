from functools import wraps
from flask import session, redirect, url_for, current_app

def admin_required(f):
    """
    Decorador que verifica si el usuario en sesión tiene un rol de administrador.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('main.home'))
        
        user_position = session.get('user_position')
        if user_position not in current_app.config['ADMIN_POSITIONS']:
            # Podrías redirigir a una página de 'no autorizado' o al dashboard
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function
