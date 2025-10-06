from flask import Blueprint, render_template, jsonify, request, session
from .decorators import admin_required
from app.services.sheets_service import SheetsService
from app.services.settings_service import SettingsService
from app.utils.logging import log_admin_action

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@admin_required
def dashboard():
    return render_template('admin.html')

# --- RUTAS DE USUARIOS (Modificadas para añadir logging)

@admin_bp.route('/get-users')
@admin_required
def get_users():
    sheets = SheetsService()
    users = sheets.get_all_users()
    safe_users = [{
        'Nombre': u.get('Nombre', ''), 
        'Posicion': u.get('Posicion', ''), 
        'Correo': u.get('Correo', '')
    } for u in users]
    return jsonify(safe_users)

@admin_bp.route('/add-user', methods=['POST'])
@admin_required
def add_user():
    data = request.json
    sheets = SheetsService()
    
    if sheets.find_user_by_email(data.get('Correo')):
        return jsonify({'success': False, 'message': 'El correo ya está registrado.'}), 409
        
    if sheets.create_user(data):
        # Log de la acción
        admin_email = session.get('user_email', 'Desconocido')
        log_admin_action(admin_email, f"Creó al usuario: {data.get('Correo')}")
        return jsonify({'success': True, 'message': 'Usuario creado con éxito.'})
    else:
        return jsonify({'success': False, 'message': 'Error en el servidor al crear usuario.'}), 500

@admin_bp.route('/delete-user', methods=['POST'])
@admin_required
def delete_user():
    correo = request.json.get('correo')
    sheets = SheetsService()
    if sheets.delete_user(correo):
        # Log de la acción
        admin_email = session.get('user_email', 'Desconocido')
        log_admin_action(admin_email, f"Eliminó al usuario: {correo}")
        return jsonify({'success': True, 'message': f'Usuario {correo} eliminado.'})
    else:
        return jsonify({'success': False, 'message': 'Usuario no encontrado.'}), 404
    
# --- NUEVAS RUTAS PARA LA CONFIGURACIÓN (ESTAS FALTABAN) ---

@admin_bp.route('/settings', methods=['GET'])
@admin_required
def get_settings():
    """Devuelve el contenido del archivo settings.json."""
    settings_service = SettingsService()
    settings = settings_service.load_settings()
    return jsonify(settings)

@admin_bp.route('/settings', methods=['POST'])
@admin_required
def update_settings():
    """Recibe y guarda las nuevas configuraciones en settings.json."""
    new_settings = request.json
    settings_service = SettingsService()
    
    # Log de la acción
    admin_email = session.get('user_email', 'Desconocido')
    log_admin_action(admin_email, f"Actualizó las configuraciones: {new_settings}")
    
    if settings_service.save_settings(new_settings):
        return jsonify({'success': True, 'message': 'Configuraciones guardadas con éxito.'})
    else:
        return jsonify({'success': False, 'message': 'Error al guardar las configuraciones.'}), 500
    
