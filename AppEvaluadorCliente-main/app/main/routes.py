from flask import Blueprint, render_template, redirect, url_for, session, jsonify
from app.services.settings_service import SettingsService

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    if session.get('logged_in'):
        return redirect(url_for('main.dashboard'))
    return render_template('login.html')

@main_bp.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('main.home'))
    
    settings_service = SettingsService()
    current_settings = settings_service.load_settings()
    
    return render_template('index.html', settings=current_settings)

@main_bp.route('/get-user-info')
def get_user_info():
    if not session.get('logged_in'):
        return jsonify({'error': 'No autorizado'}), 401
    
    from flask import current_app
    user_position = session.get('user_position', 'Sin Posicion')
    is_admin = user_position in current_app.config['ADMIN_POSITIONS']
    
    return jsonify({
        'name': session.get('user_name', 'Usuario'), 
        'position': user_position, 
        'email': session.get('user_email', 'Sin correo'), 
        'is_admin': is_admin
    })
