import unicodedata
import math
import numpy_financial as npf
import google.generativeai as genai
from flask import current_app

from app.evaluation.prompt_generator import generar_prompt_cliente 

# Carga de los DataFrames una sola vez para eficiencia
from app.utils.data_loaders import load_csv_data
from app.services.settings_service import SettingsService

df_perfiles, df_moto, df_cast, df_facil, df_emprendedor, df_especial, df_auto, df_riesgos, df_indices = load_csv_data()

model = None

numero_facil = df_facil['Numero_de_Clientes'].sum()
numero_moto = df_perfiles['Numero_de_Clientes'].sum()
numero_emprendedor = df_emprendedor['Numero_de_Clientes'].sum()
numero_especial = df_especial['Numero_de_Clientes'].sum()
numero_auto = df_auto['Numero_de_Clientes'].sum()
numero_riesgos_facil = df_riesgos[df_riesgos['Producto'] == 'C-FACIL']['Numero_de_Clientes'].sum()
numero_riesgos_moto = df_riesgos[df_riesgos['Producto'] == 'C-MOVIL']['Numero_de_Clientes'].sum()
numero_riesgos_emprendedor = df_riesgos[df_riesgos['Producto'] == 'C-EMPRENDEDOR NUEVO']['Numero_de_Clientes'].sum()
numero_riesgos_especial = df_riesgos[df_riesgos['Producto'] == 'C-ESPECIAL']['Numero_de_Clientes'].sum()
numero_riesgos_auto = df_riesgos[df_riesgos['Producto'] == 'C-AUTO']['Numero_de_Clientes'].sum()

def init_gemini():
    """
    Inicializa el modelo de Gemini de forma segura dentro del contexto de la app.
    Se ejecuta una sola vez gracias a la variable global 'model'.
    """
    global model
    if model is None:
        try:
            api_key = current_app.config.get('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("La API Key de Gemini no está configurada en .env")
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            print("Modelo de Gemini inicializado exitosamente.")
        except Exception as e:
            print(f"Error fatal al configurar Gemini: {e}")

def evaluate_client_profile(data):
    """
    Función principal que orquesta la evaluación de un cliente.
    """
    # Se asegura de que el modelo esté inicializado antes de usarlo.
    settings_service = SettingsService()
    settings = settings_service.load_settings()
    
    utilizar_ia = data.get('utilizar_ia', "SI")
    
    if utilizar_ia == "SI":
        init_gemini()
        if not model:
            return "El servicio de IA no está configurado correctamente. Revisa la API Key."
    elif utilizar_ia == "NO":
        pass
    
    producto = data.get('producto', '').strip().lower()
    
    if producto in ["c-movil", "c-mototaxista"]:
        perfil_encontrado = find_closest_profile(data, df_perfiles)
        moto_profile = find_moto_profile_mototaxi(data, df_moto)
        cast_profile = find_cast_profile(data, df_cast)
        riesgos_profile = find_riesgos_profile(data, df_riesgos)
        indice_paz = find_indice_paz_profile(data, df_indices)
        try:
            numero = numero_moto
            numero_riesgos = numero_riesgos_moto
            
        except:
            numero = 0
            numero_riesgos = 0
            
        
        utilizar_ia = data.get('utilizar_ia', "SI")
        
        prompt = generar_prompt_cliente(data, perfil_encontrado, moto_profile, cast_profile, riesgos_profile, numero, numero_riesgos, indice_paz)
        
        if utilizar_ia == "SI":
            try:
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                print(f"Error en la llamada a la API de Gemini: {e}")
                return "Ocurrió un error al contactar al servicio de IA. Intentalo denuevo en 5 minuto o Contacta con TI."
            
        elif utilizar_ia == "NO":
            return prompt
        
    elif producto == "c-facil":
        perfil_encontrado = find_closest_profile(data, df_perfiles)
        facil_profile = find_facil_profile_mototaxi(data, df_facil)
        cast_profile = find_cast_profile(data, df_cast)
        riesgos_profile = find_riesgos_profile(data, df_riesgos)
        indice_paz = find_indice_paz_profile(data, df_indices)
        
        numero = numero_facil
        numero_riesgos = numero_riesgos_facil
            
        
        settings_service = SettingsService()
        settings = settings_service.load_settings()
        
        utilizar_ia = data.get('utilizar_ia', "SI")
        
        prompt = generar_prompt_cliente(data, perfil_encontrado, facil_profile, cast_profile, riesgos_profile, numero, numero_riesgos, indice_paz)
        
        if utilizar_ia == "SI":
            try:
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                print(f"Error en la llamada a la API de Gemini: {e}")
                return "Ocurrió un error al contactar al servicio de IA. Intentalo denuevo en 5 minuto o Contacta con TI."
            
        elif utilizar_ia == "NO":
            return prompt      
        
    elif producto == "c-emprendedor nuevo":
        perfil_encontrado = find_closest_profile(data, df_perfiles)
        cast_profile = find_cast_profile(data, df_cast)
        emprendedor_profile = find_emprendedor_profile_mototaxi(data, df_emprendedor)
        riesgos_profile = find_riesgos_profile(data, df_riesgos)
        indice_paz = find_indice_paz_profile(data, df_indices)
        try:
            numero = numero_emprendedor
            numero_riesgos = numero_riesgos_emprendedor
            
        except:
            numero = 0
            numero_riesgos = 0
            
        
        settings_service = SettingsService()
        settings = settings_service.load_settings()
        
        utilizar_ia = data.get('utilizar_ia', "SI")
        
        prompt = generar_prompt_cliente(data, perfil_encontrado, emprendedor_profile, cast_profile, riesgos_profile, numero, numero_riesgos, indice_paz)
        
        if utilizar_ia == "SI":
            try:
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                print(f"Error en la llamada a la API de Gemini: {e}")
                return "Ocurrió un error al contactar al servicio de IA. Intentalo denuevo en 5 minuto o Contacta con TI."
            
        elif utilizar_ia == "NO":
            return prompt      
        
    elif producto == "c-auto":
        perfil_encontrado = find_closest_profile(data, df_perfiles)
        cast_profile = find_cast_profile(data, df_cast)
        auto_profile = find_auto_profile_mototaxi(data, df_emprendedor)
        riesgos_profile = find_riesgos_profile(data, df_riesgos)
        indice_paz = find_indice_paz_profile(data, df_indices)
        try:
            numero = numero_auto
            numero_riesgos = numero_riesgos_auto
            
        except:
            numero = 0
            numero_riesgos = 0
            
        
        settings_service = SettingsService()
        settings = settings_service.load_settings()
        
        utilizar_ia = data.get('utilizar_ia', "SI")
        
        prompt = generar_prompt_cliente(data, perfil_encontrado, auto_profile, cast_profile, riesgos_profile, numero, numero_riesgos, indice_paz)
        
        if utilizar_ia == "SI":
            try:
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                print(f"Error en la llamada a la API de Gemini: {e}")
                return "Ocurrió un error al contactar al servicio de IA. Intentalo denuevo en 5 minuto o Contacta con TI."
            
        elif utilizar_ia == "NO":
            return prompt      

    elif producto == "c-especial":
        perfil_encontrado = find_closest_profile(data, df_perfiles)
        cast_profile = find_cast_profile(data, df_cast)
        especial_profile = find_especial_profile_mototaxi(data, df_emprendedor)
        riesgos_profile = find_riesgos_profile(data, df_riesgos)
        indice_paz = find_indice_paz_profile(data, df_indices)
        try:
            numero = numero_especial
            numero_riesgos = numero_riesgos_especial
            
        except:
            numero = 0
            numero_riesgos = 0
            
        
        settings_service = SettingsService()
        settings = settings_service.load_settings()
        
        utilizar_ia = data.get('utilizar_ia', "SI")
        
        prompt = generar_prompt_cliente(data, perfil_encontrado, especial_profile, cast_profile, riesgos_profile, numero, numero_riesgos, indice_paz)
        print(settings)
        if utilizar_ia == "SI":
            try:
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                print(f"Error en la llamada a la API de Gemini: {e}")
                return "Ocurrió un error al contactar al servicio de IA. Intentalo denuevo en 5 minuto o Contacta con TI."
            
        elif utilizar_ia == "NO":
            return prompt      

# (find_closest_profile, normalize_text, generar_prompt_cliente, etc.)

def normalize_text(text):
    if not isinstance(text, str): return ''
    text = unicodedata.normalize('NFD', text)
    text = "".join(c for c in text if unicodedata.category(c) != 'Mn')
    return text.lower().strip()

def find_closest_profile(data, df):
    if df.empty: return None
    best_score = -1
    best_match_index = -1
    cliente_producto = data.get('producto', '').strip().lower()
    cliente_estado = data.get('estado', '').strip().lower()
    cliente_sucursal = data.get('sucursal', '').strip().lower()
    cliente_edad = int(data.get('edad', 0))
    cliente_monto = float(data.get('monto_credito', 0))
    cliente_plazo = float(data.get('plazo_credito', 24))
    cliente_genero = data.get('genero','').strip().lower()

    for index, row in df.iterrows():
        score = 0
        # csv_producto = str(row.get('Producto', '')).strip().lower()
        if str(row.get('Entidad', '')).strip().lower() == cliente_estado:
            # csv_producto = str(row.get('Producto', '')).strip().lower()
            # if csv_producto.startswith(cliente_producto): score += 10
            # if str(row.get('Producto', '')).strip().lower() == cliente_producto: 
            score += 10
            try:
                rango = str(row.get('Edad', '')).split('-')
                if len(rango) == 2 and int(rango[0]) <= cliente_edad <= int(rango[1]): score += 5
            except (ValueError, TypeError): pass
            if str(row.get('Producto', '')).strip().lower() == cliente_producto: score += 10
            if str(row.get('Sucursal', '')).strip().lower() == cliente_sucursal: score += 3
            if str(row.get('Genero', '')).strip().lower() == cliente_genero: score += 2
            # try:
            #     rango = str(row.get('Edad', '')).split('-')
            #     if len(rango) == 2 and int(rango[0]) <= cliente_edad <= int(rango[1]): score += 2
            # except (ValueError, TypeError): pass
            try:
                rango = float(row.get('Promedio_de_Edad', 0))
                if abs(cliente_edad - rango) <= 5: score += 1
            except (ValueError, TypeError): pass
            try:
                monto_comun = float(row.get('Monto_Comun', 0))
                if abs(monto_comun - cliente_monto) <= 35000: score += 2
            except (ValueError, TypeError): pass
            try:
                plazo_comun = float(row.get('Plazo_Promedio_Meses', 22))
                if abs(plazo_comun - cliente_plazo) <= 4: score += 2
            except (ValueError, TypeError): pass
        # elif csv_producto.startswith(cliente_producto): 
        #     score += 1
        #     try:
        #         rango = str(row.get('Edad', '')).split('-')
        #         if len(rango) == 2 and int(rango[0]) <= cliente_edad <= int(rango[1]): score += 6
        #     except (ValueError, TypeError): pass
        #     if str(row.get('Entidad', '')).strip().lower() == cliente_estado: score += 2
        #     if str(row.get('Sucursal', '')).strip().lower() == cliente_sucursal: score += 3
        #     if str(row.get('Genero_Comun', '')).strip().lower() == cliente_genero: score += 2
        #     try:
        #         rango = float(row.get('Promedio_de_Edad', 0))
        #         if abs(cliente_edad - rango) <= 5: score += 1
        #     except (ValueError, TypeError): pass
        #     try:
        #         monto_comun = float(row.get('Monto_Comun', 0))
        #         if abs(monto_comun - cliente_monto) <= 35000: score += 2
        #     except (ValueError, TypeError): pass
        #     try:
        #         plazo_comun = float(row.get('Plazo_Promedio_Meses', 22))
        #         if abs(plazo_comun - cliente_plazo) <= 4: score += 2
        #     except (ValueError, TypeError): pass
        
        if score > best_score:
            best_score = score
            best_match_index = index
    
    if best_match_index != -1:
        return df.loc[best_match_index].to_dict()
    return None

def find_moto_profile_mototaxi(data, df_mototaxi):
    
    if df_mototaxi.empty: return None
    best_score = -1
    best_match_index = -1
    cliente_sucursal_norm = normalize_text(data.get('sucursal', ''))
    cliente_estado_norm = normalize_text(data.get('estado', ''))
    location_column = 'EntidadSucursal'
    for index, row in df_mototaxi.iterrows():
        score = 0
        csv_location_norm = normalize_text(row.get(location_column, ''))
        if cliente_sucursal_norm and cliente_sucursal_norm in csv_location_norm: score += 2
        elif cliente_estado_norm and cliente_estado_norm in csv_location_norm: score += 1
        if score > best_score:
            best_score = score
            best_match_index = index
    if best_score > 0:
        return df_mototaxi.iloc[best_match_index].to_dict()
    return None

def find_facil_profile_mototaxi(data, df_mototaxi):
    
    if df_mototaxi.empty: return None
    best_score = -1
    best_match_index = -1
    cliente_producto = data.get('producto', '').strip().lower()
    cliente_estado = data.get('estado', '').strip().lower()
    cliente_sucursal = data.get('sucursal', '').strip().lower()
    cliente_edad = int(data.get('edad', 0))
    cliente_monto = float(data.get('monto_credito', 0))
    cliente_plazo = float(data.get('plazo_credito', 24))
    cliente_genero = data.get('genero','').strip().lower()
    for index, row in df_mototaxi.iterrows():
        score = 0
        csv_producto = str(row.get('Producto', '')).strip().lower()
        if str(row.get('Producto', '')).strip().lower() == cliente_producto:
            # csv_producto = str(row.get('Producto', '')).strip().lower()
            # if csv_producto.startswith(cliente_producto): score += 10
            # if str(row.get('Producto', '')).strip().lower() == cliente_producto: 
            score += 10
            # try:
            #     rango = str(row.get('Edad', '')).split('-')
            #     if len(rango) == 2 and int(rango[0]) <= cliente_edad <= int(rango[1]): score += 6
            # except (ValueError, TypeError): pass
            if str(row.get('Entidad', '')).strip().lower() == cliente_estado: score += 5
            if str(row.get('Sucursal', '')).strip().lower() == cliente_sucursal: score += 3
            if str(row.get('Genero', '')).strip().lower() == cliente_genero: score += 2
            # try:
            #     rango = str(row.get('Edad', '')).split('-')
            #     if len(rango) == 2 and int(rango[0]) <= cliente_edad <= int(rango[1]): score += 2
            # except (ValueError, TypeError): pass
            try:
                rango = float(row.get('Promedio_de_Edad', 0))
                if abs(cliente_edad - rango) <= 5: score += 1
            except (ValueError, TypeError): pass
            try:
                monto_comun = float(row.get('Monto_Comun', 0))
                if abs(monto_comun - cliente_monto) <= 35000: score += 2
            except (ValueError, TypeError): pass
            try:
                plazo_comun = float(row.get('Plazo_Promedio_Meses', 22))
                if abs(plazo_comun - cliente_plazo) <= 4: score += 2
            except (ValueError, TypeError): pass
        elif csv_producto.startswith(cliente_producto): 
            score += 1
            # try:
            #     rango = str(row.get('Edad', '')).split('-')
            #     if len(rango) == 2 and int(rango[0]) <= cliente_edad <= int(rango[1]): score += 6
            # except (ValueError, TypeError): pass
            if str(row.get('Entidad', '')).strip().lower() == cliente_estado: score += 2
            if str(row.get('Sucursal', '')).strip().lower() == cliente_sucursal: score += 3
            if str(row.get('Genero_Comun', '')).strip().lower() == cliente_genero: score += 2
            try:
                rango = float(row.get('Promedio_de_Edad', 0))
                if abs(cliente_edad - rango) <= 5: score += 1
            except (ValueError, TypeError): pass
            try:
                monto_comun = float(row.get('Monto_Comun', 0))
                if abs(monto_comun - cliente_monto) <= 35000: score += 2
            except (ValueError, TypeError): pass
            try:
                plazo_comun = float(row.get('Plazo_Promedio_Meses', 22))
                if abs(plazo_comun - cliente_plazo) <= 4: score += 2
            except (ValueError, TypeError): pass
        
        if score > best_score:
            best_score = score
            best_match_index = index
    
    if best_match_index != -1:
        return df_mototaxi.loc[best_match_index].to_dict()
    return None

def find_auto_profile_mototaxi(data, df_mototaxi):
    
    if df_mototaxi.empty: return None
    best_score = -1
    best_match_index = -1
    cliente_producto = data.get('producto', '').strip().lower()
    cliente_estado = data.get('estado', '').strip().lower()
    cliente_sucursal = data.get('sucursal', '').strip().lower()
    cliente_edad = int(data.get('edad', 0))
    cliente_monto = float(data.get('monto_credito', 0))
    cliente_plazo = float(data.get('plazo_credito', 24))
    cliente_genero = data.get('genero','').strip().lower()
    for index, row in df_mototaxi.iterrows():
        score = 0
        csv_producto = str(row.get('Producto', '')).strip().lower()
        if str(row.get('Producto', '')).strip().lower() == cliente_producto:
            # csv_producto = str(row.get('Producto', '')).strip().lower()
            # if csv_producto.startswith(cliente_producto): score += 10
            # if str(row.get('Producto', '')).strip().lower() == cliente_producto: 
            score += 10
            # try:
            #     rango = str(row.get('Edad', '')).split('-')
            #     if len(rango) == 2 and int(rango[0]) <= cliente_edad <= int(rango[1]): score += 6
            # except (ValueError, TypeError): pass
            if str(row.get('Entidad', '')).strip().lower() == cliente_estado: score += 5
            if str(row.get('Sucursal', '')).strip().lower() == cliente_sucursal: score += 3
            if str(row.get('Genero', '')).strip().lower() == cliente_genero: score += 2
            # try:
            #     rango = str(row.get('Edad', '')).split('-')
            #     if len(rango) == 2 and int(rango[0]) <= cliente_edad <= int(rango[1]): score += 2
            # except (ValueError, TypeError): pass
            try:
                rango = float(row.get('Promedio_de_Edad', 0))
                if abs(cliente_edad - rango) <= 5: score += 1
            except (ValueError, TypeError): pass
            try:
                monto_comun = float(row.get('Monto_Comun', 0))
                if abs(monto_comun - cliente_monto) <= 35000: score += 2
            except (ValueError, TypeError): pass
            try:
                plazo_comun = float(row.get('Plazo_Promedio_Meses', 22))
                if abs(plazo_comun - cliente_plazo) <= 4: score += 2
            except (ValueError, TypeError): pass
        elif csv_producto.startswith(cliente_producto): 
            score += 1
            # try:
            #     rango = str(row.get('Edad', '')).split('-')
            #     if len(rango) == 2 and int(rango[0]) <= cliente_edad <= int(rango[1]): score += 6
            # except (ValueError, TypeError): pass
            if str(row.get('Entidad', '')).strip().lower() == cliente_estado: score += 2
            if str(row.get('Sucursal', '')).strip().lower() == cliente_sucursal: score += 3
            if str(row.get('Genero_Comun', '')).strip().lower() == cliente_genero: score += 2
            try:
                rango = float(row.get('Promedio_de_Edad', 0))
                if abs(cliente_edad - rango) <= 5: score += 1
            except (ValueError, TypeError): pass
            try:
                monto_comun = float(row.get('Monto_Comun', 0))
                if abs(monto_comun - cliente_monto) <= 35000: score += 2
            except (ValueError, TypeError): pass
            try:
                plazo_comun = float(row.get('Plazo_Promedio_Meses', 22))
                if abs(plazo_comun - cliente_plazo) <= 4: score += 2
            except (ValueError, TypeError): pass
        
        if score > best_score:
            best_score = score
            best_match_index = index
    
    if best_match_index != -1:
        return df_mototaxi.loc[best_match_index].to_dict()
    return None

def find_emprendedor_profile_mototaxi(data, df_mototaxi):
    
    if df_mototaxi.empty: return None
    best_score = -1
    best_match_index = -1
    cliente_producto = data.get('producto', '').strip().lower()
    cliente_estado = data.get('estado', '').strip().lower()
    cliente_sucursal = data.get('sucursal', '').strip().lower()
    cliente_edad = int(data.get('edad', 0))
    cliente_monto = float(data.get('monto_credito', 0))
    cliente_plazo = float(data.get('plazo_credito', 24))
    cliente_genero = data.get('genero','').strip().lower()
    for index, row in df_mototaxi.iterrows():
        score = 0
        csv_producto = str(row.get('Producto', '')).strip().lower()
        if str(row.get('Producto', '')).strip().lower() == cliente_producto:
            # csv_producto = str(row.get('Producto', '')).strip().lower()
            # if csv_producto.startswith(cliente_producto): score += 10
            # if str(row.get('Producto', '')).strip().lower() == cliente_producto: 
            score += 10
            # try:
            #     rango = str(row.get('Edad', '')).split('-')
            #     if len(rango) == 2 and int(rango[0]) <= cliente_edad <= int(rango[1]): score += 6
            # except (ValueError, TypeError): pass
            if str(row.get('Entidad', '')).strip().lower() == cliente_estado: score += 5
            if str(row.get('Sucursal', '')).strip().lower() == cliente_sucursal: score += 3
            if str(row.get('Genero', '')).strip().lower() == cliente_genero: score += 2
            # try:
            #     rango = str(row.get('Edad', '')).split('-')
            #     if len(rango) == 2 and int(rango[0]) <= cliente_edad <= int(rango[1]): score += 2
            # except (ValueError, TypeError): pass
            try:
                rango = float(row.get('Promedio_de_Edad', 0))
                if abs(cliente_edad - rango) <= 5: score += 1
            except (ValueError, TypeError): pass
            try:
                monto_comun = float(row.get('Monto_Comun', 0))
                if abs(monto_comun - cliente_monto) <= 35000: score += 2
            except (ValueError, TypeError): pass
            try:
                plazo_comun = float(row.get('Plazo_Promedio_Meses', 22))
                if abs(plazo_comun - cliente_plazo) <= 4: score += 2
            except (ValueError, TypeError): pass
        elif csv_producto.startswith(cliente_producto): 
            score += 1
            # try:
            #     rango = str(row.get('Edad', '')).split('-')
            #     if len(rango) == 2 and int(rango[0]) <= cliente_edad <= int(rango[1]): score += 6
            # except (ValueError, TypeError): pass
            if str(row.get('Entidad', '')).strip().lower() == cliente_estado: score += 2
            if str(row.get('Sucursal', '')).strip().lower() == cliente_sucursal: score += 3
            if str(row.get('Genero_Comun', '')).strip().lower() == cliente_genero: score += 2
            try:
                rango = float(row.get('Promedio_de_Edad', 0))
                if abs(cliente_edad - rango) <= 5: score += 1
            except (ValueError, TypeError): pass
            try:
                monto_comun = float(row.get('Monto_Comun', 0))
                if abs(monto_comun - cliente_monto) <= 35000: score += 2
            except (ValueError, TypeError): pass
            try:
                plazo_comun = float(row.get('Plazo_Promedio_Meses', 22))
                if abs(plazo_comun - cliente_plazo) <= 4: score += 2
            except (ValueError, TypeError): pass
        
        if score > best_score:
            best_score = score
            best_match_index = index
    
    if best_match_index != -1:
        return df_mototaxi.loc[best_match_index].to_dict()
    return None

def find_especial_profile_mototaxi(data, df_mototaxi):
    
    if df_mototaxi.empty: return None
    best_score = -1
    best_match_index = -1
    cliente_producto = data.get('producto', '').strip().lower()
    cliente_estado = data.get('estado', '').strip().lower()
    cliente_sucursal = data.get('sucursal', '').strip().lower()
    cliente_edad = int(data.get('edad', 0))
    cliente_monto = float(data.get('monto_credito', 0))
    cliente_plazo = float(data.get('plazo_credito', 24))
    cliente_genero = data.get('genero','').strip().lower()
    for index, row in df_mototaxi.iterrows():
        score = 0
        csv_producto = str(row.get('Producto', '')).strip().lower()
        if str(row.get('Producto', '')).strip().lower() == cliente_producto:
            # csv_producto = str(row.get('Producto', '')).strip().lower()
            # if csv_producto.startswith(cliente_producto): score += 10
            # if str(row.get('Producto', '')).strip().lower() == cliente_producto: 
            score += 10
            # try:
            #     rango = str(row.get('Edad', '')).split('-')
            #     if len(rango) == 2 and int(rango[0]) <= cliente_edad <= int(rango[1]): score += 6
            # except (ValueError, TypeError): pass
            if str(row.get('Entidad', '')).strip().lower() == cliente_estado: score += 5
            if str(row.get('Sucursal', '')).strip().lower() == cliente_sucursal: score += 3
            if str(row.get('Genero', '')).strip().lower() == cliente_genero: score += 2
            # try:
            #     rango = str(row.get('Edad', '')).split('-')
            #     if len(rango) == 2 and int(rango[0]) <= cliente_edad <= int(rango[1]): score += 2
            # except (ValueError, TypeError): pass
            try:
                rango = float(row.get('Promedio_de_Edad', 0))
                if abs(cliente_edad - rango) <= 5: score += 1
            except (ValueError, TypeError): pass
            try:
                monto_comun = float(row.get('Monto_Comun', 0))
                if abs(monto_comun - cliente_monto) <= 35000: score += 2
            except (ValueError, TypeError): pass
            try:
                plazo_comun = float(row.get('Plazo_Promedio_Meses', 22))
                if abs(plazo_comun - cliente_plazo) <= 4: score += 2
            except (ValueError, TypeError): pass
        elif csv_producto.startswith(cliente_producto): 
            score += 1
            # try:
            #     rango = str(row.get('Edad', '')).split('-')
            #     if len(rango) == 2 and int(rango[0]) <= cliente_edad <= int(rango[1]): score += 6
            # except (ValueError, TypeError): pass
            if str(row.get('Entidad', '')).strip().lower() == cliente_estado: score += 2
            if str(row.get('Sucursal', '')).strip().lower() == cliente_sucursal: score += 3
            if str(row.get('Genero_Comun', '')).strip().lower() == cliente_genero: score += 2
            try:
                rango = float(row.get('Promedio_de_Edad', 0))
                if abs(cliente_edad - rango) <= 5: score += 1
            except (ValueError, TypeError): pass
            try:
                monto_comun = float(row.get('Monto_Comun', 0))
                if abs(monto_comun - cliente_monto) <= 35000: score += 2
            except (ValueError, TypeError): pass
            try:
                plazo_comun = float(row.get('Plazo_Promedio_Meses', 22))
                if abs(plazo_comun - cliente_plazo) <= 4: score += 2
            except (ValueError, TypeError): pass
        
        if score > best_score:
            best_score = score
            best_match_index = index
    
    if best_match_index != -1:
        return df_mototaxi.loc[best_match_index].to_dict()
    return None

def find_cast_profile(data, df_cast):
    if df_cast.empty: return None
    best_score = -1
    best_match_index = -1
    cliente_municipio_norm = normalize_text(data.get('municipio', ''))
    cliente_estado_norm = normalize_text(data.get('estado', ''))
    cliente_genero_norm = normalize_text(data.get('genero', ''))
    for index, row in df_cast.iterrows():
        score = 0
        csv_municipio_norm = normalize_text(row.get('Municipio', ''))
        csv_estado_norm = normalize_text(row.get('Estado', ''))
        csv_genero_norm = normalize_text(row.get('Genero', ''))
        if cliente_municipio_norm and cliente_municipio_norm == csv_municipio_norm: score += 2
        if cliente_estado_norm and cliente_estado_norm == csv_estado_norm: score += 1
        if cliente_genero_norm and cliente_genero_norm == csv_genero_norm: score += 2
        if score > best_score:
            best_score = score
            best_match_index = index
    if best_score > 0:
        return df_cast.iloc[best_match_index].to_dict()
    return None

def find_riesgos_profile(data, df_riesgos):
    if df_riesgos.empty: return None
    best_score = -1
    best_match_index = -1
    cliente_producto = data.get('producto', '').strip().lower()
    cliente_estado = data.get('estado', '').strip().lower()
    cliente_sucursal = data.get('sucursal', '').strip().lower()
    cliente_edad = int(data.get('edad', 0))
    cliente_monto = float(data.get('monto_credito', 0))
    cliente_plazo = float(data.get('plazo_credito', 24))
    cliente_genero = data.get('genero','').strip().lower()
    for index, row in df_riesgos.iterrows():
        score = 0
        # csv_producto = str(row.get('Entidad', '')).strip().lower()
        if str(row.get('Entidad', '')).strip().lower() == cliente_estado:
            # csv_producto = str(row.get('Producto', '')).strip().lower()
            # if csv_producto.startswith(cliente_producto): score += 10
            # if str(row.get('Producto', '')).strip().lower() == cliente_producto: 
            score += 10
            # try:
            #     rango = str(row.get('Edad', '')).split('-')
            #     if len(rango) == 2 and int(rango[0]) <= cliente_edad <= int(rango[1]): score += 6
            # except (ValueError, TypeError): pass
            if str(row.get('Producto', '')).strip().lower() == cliente_producto: score += 2
            if str(row.get('Sucursal', '')).strip().lower() == cliente_sucursal: score += 3
            if str(row.get('Genero', '')).strip().lower() == cliente_genero: score += 2
            # try:
            #     rango = str(row.get('Edad', '')).split('-')
            #     if len(rango) == 2 and int(rango[0]) <= cliente_edad <= int(rango[1]): score += 2
            # except (ValueError, TypeError): pass
            try:
                rango = float(row.get('Promedio_de_Edad', 0))
                if abs(cliente_edad - rango) <= 5: score += 1
            except (ValueError, TypeError): pass
            try:
                monto_comun = float(row.get('Monto_Comun', 0))
                if abs(monto_comun - cliente_monto) <= 35000: score += 2
            except (ValueError, TypeError): pass
            try:
                plazo_comun = float(row.get('Plazo_Promedio_Meses', 22))
                if abs(plazo_comun - cliente_plazo) <= 4: score += 2
            except (ValueError, TypeError): pass
        elif str(row.get('Producto', '')).strip().lower() == cliente_producto: 
            score += 5
            # try:
            #     rango = str(row.get('Edad', '')).split('-')
            #     if len(rango) == 2 and int(rango[0]) <= cliente_edad <= int(rango[1]): score += 6
            # except (ValueError, TypeError): pass
            if str(row.get('Entidad', '')).strip().lower() == cliente_estado: score += 2
            if str(row.get('Sucursal', '')).strip().lower() == cliente_sucursal: score += 3
            if str(row.get('Genero_Comun', '')).strip().lower() == cliente_genero: score += 2
            try:
                rango = float(row.get('Promedio_de_Edad', 0))
                if abs(cliente_edad - rango) <= 5: score += 1
            except (ValueError, TypeError): pass
            try:
                monto_comun = float(row.get('Monto_Comun', 0))
                if abs(monto_comun - cliente_monto) <= 35000: score += 2
            except (ValueError, TypeError): pass
            try:
                plazo_comun = float(row.get('Plazo_Promedio_Meses', 22))
                if abs(plazo_comun - cliente_plazo) <= 4: score += 2
            except (ValueError, TypeError): pass
        
        if score > best_score:
            best_score = score
            best_match_index = index
    
    if best_match_index != -1:
        return df_riesgos.loc[best_match_index].to_dict()
    return None

def find_indice_paz_profile(data, df_indices):
    if df_indices.empty: return None
    best_score = -1
    best_match_index = -1
    cliente_estado = data.get('estado', '').strip().lower()
    cliente_monto = float(data.get('monto_credito', 0))/12
    for index, row in df_indices.iterrows():
        score = 0
        if str(row.get('Estado', '')).strip().lower() == cliente_estado:
            score += 10
            if str(row.get('Entidad', '')).strip().lower() == cliente_estado: score += 2
            try:
                monto_comun = float(row.get('ImpactoAnualPersona', 0))
                if abs(monto_comun - cliente_monto) <= 7000: score += 5
            except (ValueError, TypeError): pass     
        if score > best_score:
            best_score = score
            best_match_index = index
    
    if best_match_index != -1:
        return df_indices.loc[best_match_index].to_dict()
    return None