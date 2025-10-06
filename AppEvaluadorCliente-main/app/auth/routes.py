from flask import Blueprint, request, jsonify, session, url_for, render_template, redirect, current_app
from werkzeug.security import check_password_hash
import secrets
from datetime import datetime, timedelta
from app import limiter
from app.services.sheets_service import SheetsService
from app.services.email_service import send_reset_email
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data = request.json
    correo = data.get('correo')
    password = data.get('password')

    sheets = SheetsService()
    user = sheets.find_user_by_email(correo)

    if user and check_password_hash(user.get('Password', ''), password):
        session.clear()
        session['logged_in'] = True
        session['user_email'] = user.get('Correo')
        session['user_name'] = user.get('Nombre')
        session['user_position'] = user.get('Posicion')
        session['last_activity'] = datetime.utcnow().isoformat()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Credenciales incorrectas'}), 401

@auth_bp.route('/check-session')
def check_session():
    # print("Contenido de la sesión:", session) # ¿Qué hay dentro de la sesión?
    # user_id = session.get('user_id')
    # print("User ID obtenido de la sesión:", user_id)
    # if user_id:
    #     print("Usuario encontrado. Devolviendo logged_in = True")
    #     return jsonify(logged_in=True, user_id=user_id)
    # else:
    #     print("Usuario NO encontrado. Devolviendo logged_in = False")
    #     return jsonify(logged_in=False), 401 # Es buena práctica devolver un 401
    
    user_email = session.get('user_email') 
    if user_email:
        # Si quieres, puedes devolver más datos al frontend.
        return jsonify(logged_in=True, user_email=user_email, user_name=session.get('user_name'))
    else:
        return jsonify(logged_in=False), 401
    
    # return jsonify({'logged_in': session.get('logged_in', False)})

@auth_bp.route('/logout')
def logout():
    session.clear()
    # return jsonify({'success': True}), redirect(url_for('main.home'))
    return redirect(url_for('main.home'))

@auth_bp.route('/get-user-info')
def get_user_info():
    if not session.get('logged_in'):
        return jsonify({'error': 'No autorizado'}), 401
    is_admin = session.get('user_position') in current_app.config['ADMIN_POSITIONS']
    return jsonify({
        'name': session.get('user_name', 'Usuario'), 
        'position': session.get('user_position', 'Sin Posicion'), 
        'email': session.get('user_email', 'Sin correo'), 
        'is_admin': is_admin
    })

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def request_password_reset():
    if request.method == 'GET':
        return render_template('request_reset.html')

    correo = request.json.get('correo')
    sheets = SheetsService()
    # user = sheets.find_user_by_email(correo)
    if sheets.find_user_by_email(correo):
        token = secrets.token_urlsafe(32)
        expiry_time = datetime.utcnow() + timedelta(minutes=15)
        
        
        if sheets.update_user_token(correo, token, expiry_time.timestamp()):
            reset_link = url_for('auth.reset_with_token', token=token, _external=True)
            send_reset_email(correo, reset_link)

    return jsonify({'success': True, 'message': 'Si tu correo está registrado, recibirás un enlace.'})

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    sheets = SheetsService()
    user = sheets.find_user_by_token(token)

    if not user:
        return "Enlace inválido o expirado.", 404

    expiry_timestamp_str = user.get('token_expiry')
    
    if not expiry_timestamp_str:
        return "El enlace de restablecimiento ha expirado (código 1).", 400
        
    try:
        expiry_timestamp = float(expiry_timestamp_str)
    except ValueError:
        return "El enlace de restablecimiento es inválido (código 2).", 400

    if datetime.fromtimestamp(expiry_timestamp) < datetime.utcnow():
        return "El enlace de restablecimiento ha expirado (código 3). Por favor, solicita uno nuevo.", 400

    if request.method == 'GET':
        return render_template('reset_password.html', token=token)

    data = request.json
    pin = data.get('pin')
    new_password = data.get('nueva_password')
    if not new_password:
         return jsonify({'success': False, 'message': 'La nueva contraseña no puede estar vacía.'}), 400

    if str(user.get('PIN')) != str(pin):
        return jsonify({'success': False, 'message': 'El PIN es incorrecto.'}), 401

    if sheets.update_user_password(user.get('Correo'), new_password):
        return jsonify({'success': True, 'message': '¡Contraseña actualizada con éxito!'})
    else:
        return jsonify({'success': False, 'message': 'Error al guardar la nueva contraseña.'}), 500
