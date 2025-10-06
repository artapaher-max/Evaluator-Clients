import json
import os
# from flask import current_app

class SettingsService:
    def __init__(self):
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.filepath = os.path.join(base_path, 'settings.json')

    def load_settings(self):
        """Carga las configuraciones desde el archivo JSON."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Si el archivo no existe o está corrupto, devuelve un diccionario vacío.
            return {}

    def save_settings(self, settings_data):
        """Guarda las configuraciones en el archivo JSON."""
        try:
            processed_data = {}
            for key, value in settings_data.items():
                # --- LÓGICA CONDICIONAL ---
                # Si la clave es NEGATIVOS, la guardamos como texto (string)
                if key == 'NEGATIVOS':
                    processed_data[key] = str(value)
                else:
                    # Para las demás, intentamos convertirlas a número como antes
                    try:
                        if '.' in str(value):
                            processed_data[key] = float(value)
                        else:
                            processed_data[key] = int(value)
                    except (ValueError, TypeError):
                        processed_data[key] = value # Si falla, lo deja como está

            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error al guardar las configuraciones: {e}")
            return False
