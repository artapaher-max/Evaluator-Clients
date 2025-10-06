from flask import Blueprint, request, jsonify, session
from .services import evaluate_client_profile
from app.utils.logging import log_evaluacion
import pandas as pd
import io
# from app.services.settings_service import SettingsService

evaluation_bp = Blueprint('evaluation', __name__)

@evaluation_bp.route('/evaluar-cliente', methods=['POST'])
def evaluar_cliente():
    if not session.get('logged_in'):
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    
    # settings_service = SettingsService()
    # settings = settings_service.load_settings()
    
    # Llamar al servicio de evaluación
    conclusion = evaluate_client_profile(data)
    
    # Registrar la evaluación
    evaluador = session.get('user_email', 'Desconocido')
    log_evaluacion(evaluador, data.get('nombre', 'N/A'), conclusion)

    return jsonify({'analisis': conclusion})

@evaluation_bp.route('/evaluar-csv', methods=['POST'])
def evaluar_csv():
    if not session.get('logged_in'):
        return jsonify({'error': 'No autorizado'}), 401

    if 'csv_file' not in request.files:
        return jsonify({'error': 'No se encontró el archivo CSV'}), 400

    file = request.files['csv_file']
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'El archivo debe ser de tipo CSV'}), 400

    try:
        stream = io.StringIO(file.stream.read().decode("UTF-8"))
        df = pd.read_csv(stream)
        
        resultados = []
        evaluador = session.get('user_email', 'Desconocido')

        for index, row in df.iterrows():
            conclusion = evaluate_client_profile(row.to_dict())
            nombre_cliente = row.get('Nombre', f'Cliente #{index+1}')
            log_evaluacion(evaluador, nombre_cliente, conclusion)
            resultados.append(f"--- Análisis para {nombre_cliente} ---\n{conclusion}\n\n")
            
        analisis_completo = "\n".join(resultados)
        return jsonify({'analisis': analisis_completo})

    except Exception as e:
        print(f"Error al procesar el archivo CSV: {e}")
        return jsonify({'analisis': f'Error: Ocurrió un problema. Detalles: {e}'}), 500
