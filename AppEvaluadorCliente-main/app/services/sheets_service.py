import gspread
from oauth2client.service_account import ServiceAccountCredentials
from werkzeug.security import generate_password_hash
from flask import current_app

class SheetsService:
    """Encapsula toda la interacción con la API de Google Sheets."""
    
    def __init__(self):
        try:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                current_app.config['SHEETS_CREDENTIALS_PATH'], scope
            )
            client = gspread.authorize(creds)
            self.sheet = client.open_by_key(current_app.config['SHEETS_ID']).sheet1
        except Exception as e:
            print(f"Error fatal al conectar con Google Sheets: {e}")
            self.sheet = None

    def get_all_users(self):
        if not self.sheet: return []
        return self.sheet.get_all_records()
        # if self.sheet:
        #     return self.sheet.get_all_records()
        # return []

    def find_user_by_email(self, email):
        """
        Busca un usuario por su correo electrónico.
        Devuelve un diccionario con los datos del usuario si lo encuentra, o None si no.
        """
        if not self.sheet: return None
        try:
            cell = self.sheet.find(email)
            return self._get_user_data_from_row(cell.row) if cell else None
        except gspread.CellNotFound:
            return None
            # if cell is None:
            #     return None
            
            # return self._get_user_data_from_row(cell.row)
        
        # except gspread.CellNotFound:
        #     return None
        # except Exception as e:
        #     print(f"Ocurrió un error inesperado al buscar en Sheets: {e}")
        #     return None

    def find_user_by_token(self, token):
        
        if not self.sheet: return None
        try:
            cell = self.sheet.find(token)
            return self._get_user_data_from_row(cell.row) if cell else None
        except gspread.CellNotFound: # <-- Se usa el nombre de excepción correcto
            return None
        # try:
        #     cell = self.sheet.find(token)            
        #     if cell is None:
        #         return None            
        #     return self._get_user_data_from_row(cell.row)        
        # except gspread.CellNotFound:
        #     return None

    def create_user(self, user_data):
        """Añade un nuevo usuario a la hoja de cálculo."""
        if not self.sheet: return False
        try:
            hashed_password = generate_password_hash(user_data['Password'], method='pbkdf2:sha256', salt_length=16)
            
            headers = self.sheet.row_values(1)
            # Construir la fila dinámicamente según las cabeceras
            new_row_data = {
                'Nombre': user_data.get('Nombre'),
                'Posicion': user_data.get('Posicion'),
                'Correo': user_data.get('Correo'),
                'Password': hashed_password,
                'PIN': user_data.get('PIN')
            }
            new_row = [new_row_data.get(h, '') for h in headers]
            
            self.sheet.append_row(new_row)
            return True
        except Exception as e:
            print(f"Error al crear usuario en Sheets: {e}")
            return False

    def delete_user(self, email):
        """Elimina a un usuario por su email."""
        if not self.sheet: return False
        try:
            cell = self.sheet.find(email)
            if cell:
                self.sheet.delete_rows(cell.row)
                return True
            return False
        except gspread.CellNotFound:
            return False

    def update_user_token(self, email, token, expiry_time):
        """Actualiza el token y la fecha de expiración de un usuario."""
        
        
        
        if not self.sheet: return False
        try:
            cell = self.sheet.find(email)
            if cell:
                headers = self.sheet.row_values(1)
                token_col = headers.index('reset_token') + 1
                expiry_col = headers.index('token_expiry') + 1
                self.sheet.update_cell(cell.row, token_col, token)
                self.sheet.update_cell(cell.row, expiry_col, expiry_time)
                return True
            return False
        except gspread.CellNotFound:
            return False

    def update_user_password(self, email, new_password):
        """Actualiza la contraseña de un usuario y limpia los tokens."""
        if not self.sheet: return False
        try:
            cell = self.sheet.find(email)
            if cell:
                headers = self.sheet.row_values(1)
                new_hash = generate_password_hash(new_password)
                
                # Columnas a actualizar
                password_col = headers.index('Password') + 1
                token_col = headers.index('reset_token') + 1
                expiry_col = headers.index('token_expiry') + 1
                
                self.sheet.update_cell(cell.row, password_col, new_hash)
                self.sheet.update_cell(cell.row, token_col, "")
                self.sheet.update_cell(cell.row, expiry_col, "")
                return True
            return False
        except gspread.CellNotFound:
            return False

    def _get_user_data_from_row(self, row_index):
        """Función auxiliar para obtener datos de usuario de una fila específica."""
        if not self.sheet: return None
        headers = self.sheet.row_values(1)
        user_values = self.sheet.row_values(row_index)
        return dict(zip(headers, user_values))
    
    
    
    
