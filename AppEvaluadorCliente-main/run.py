from app import create_app
from waitress import serve
import os

# 1. Creamos la instancia de TU aplicación evaluador_credito
app = create_app()

if __name__ == '__main__':
    # 2. Definimos la ruta a los archivos del certificado que creaste
    cert_path = 'cert.pem'
    key_path = 'key.pem'
    
    namehost = app.config.get('NAMEHOST', "PC-HOST")
    host = app.config.get('HOST', '0.0.0.0')
    port = app.config.get('PORT', 5000)
    
    # # 3. Comprobamos si las llaves existen
    # if os.path.exists(cert_path) and os.path.exists(key_path):
    #     # Si existen, iniciamos el servidor en MODO SEGURO (HTTPS)
    #     print(f"--> Certificados encontrados. Iniciando servidor en MODO SEGURO (HTTPS).")
    #     print(f"--> Accede a tu aplicación en: https://{host}:{port} o https://127.0.0.1:{port}")
    #     serve(
    #         app, 
    #         host=host, 
    #         port=port, 
    #         ssl_certificate=cert_path, 
    #         ssl_private_key=key_path
    #     )
    # else:
    #     # Si no, iniciamos en modo normal (HTTP) con una advertencia
    #     print("--> ADVERTENCIA: No se encontraron los archivos cert.pem y key.pem.")
    #     print("--> Iniciando servidor en MODO INSEGURO (HTTP).")
    #     print(f"--> Accede a tu aplicación en: http://{host}:{port}")
    #     serve(app, host=host, port=port)
    print("--> ADVERTENCIA: No se encontraron los archivos cert.pem y key.pem.")
    print("--> Iniciando servidor en MODO INSEGURO (HTTP).")
    print(f"--> HOST PRINCIPAL: {host}")
    print(f"--> URL ACCESO PRINCIPAL: http://{host}:{port}")
    serve(app, host=host, port=port)