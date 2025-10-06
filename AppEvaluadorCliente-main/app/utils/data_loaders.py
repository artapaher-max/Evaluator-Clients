import pandas as pd
import os

def load_csv_data():
    """Carga todos los DataFrames desde archivos CSV."""
    
    # La ruta base es la raíz de la aplicación (donde está run.py)
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    try:
        df_perfiles = pd.read_csv(os.path.join(base_path, 'perfiles_clientes.csv'))
    except FileNotFoundError:
        print("ADVERTENCIA: No se encontró 'perfiles_clientes.csv'.")
        df_perfiles = pd.DataFrame()
        
    try:
        df_moto = pd.read_csv(os.path.join(base_path, 'info_mototaxi.csv'))
    except FileNotFoundError:
        print("ADVERTENCIA: No se encontró 'info_mototaxi.csv'.")
        df_moto = pd.DataFrame()
        
    try:
        df_cast = pd.read_csv(os.path.join(base_path, 'castigados.csv'))
    except FileNotFoundError:
        print("ADVERTENCIA: No se encontró 'castigados.csv'.")
        df_cast = pd.DataFrame()
        
    try:
        df_facil = pd.read_csv(os.path.join(base_path, 'facil.csv'))
    except FileNotFoundError:
        print("ADVERTENCIA: No se encontró 'facil.csv'.")
        df_facil = pd.DataFrame()
        
    try:
        df_emprendedor = pd.read_csv(os.path.join(base_path, 'emprendedor.csv'))
    except FileNotFoundError:
        print("ADVERTENCIA: No se encontró 'emprendedor.csv'.")
        df_emprendedor = pd.DataFrame()
        
    try:
        df_especial = pd.read_csv(os.path.join(base_path, 'especial.csv'))
    except FileNotFoundError:
        print("ADVERTENCIA: No se encontró 'especial.csv'.")
        df_especial = pd.DataFrame()
        
    try:
        df_auto = pd.read_csv(os.path.join(base_path, 'auto.csv'))
    except FileNotFoundError:
        print("ADVERTENCIA: No se encontró 'auto.csv'.")
        df_auto = pd.DataFrame()
    
    try:
        df_riesgos = pd.read_csv(os.path.join(base_path, 'riesgos.csv'))
    except FileNotFoundError:
        print("ADVERTENCIA: No se encontró 'riesgos.csv'.")
        df_riesgos = pd.DataFrame()
        
    try:
        df_indices = pd.read_csv(os.path.join(base_path, 'indices.csv'))
    except FileNotFoundError:
        print("ADVERTENCIA: No se encontró 'indices.csv'.")
        df_indices = pd.DataFrame()
    
        
    return df_perfiles, df_moto, df_cast, df_facil, df_emprendedor, df_especial, df_auto, df_riesgos, df_indices
