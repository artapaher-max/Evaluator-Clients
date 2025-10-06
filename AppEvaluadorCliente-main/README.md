# AppEvaluadorCliente
Evaluador de clientes Asefimex para poder preautorizar a los clientes prospectos, en base a bases de datos segun el analisis hecho de la cartera de clientes que se importan a la app para mayor control sobre la actualizacion de la base de datos, teniendo en control todos los datos de la aplicacion.

Estructura de la app:

.env
requirements.txt
run.bat
run.py
|--app
    |--admin
        |--__init__.py
        |--decorators.py
        |--routes.py
    |--auth
        |--__init__.py
        |--routes.py
    |--evaluation
        |--__init__.py
        |--prompt_generator.py
        |--routes.py
        |--services.py
    |--main
        |--__init__.py
        |--routes.py
    |--services
        |--__init__.py
        |--email_service.py
        |--settings_service.py
        |--sheets_service.py
    |--static
        |--iconos, logos, imagenes, etc...
    |--templates
        |--index.html
        |--login.html
        |--reset_password.html
        |--admin.html
    |--utils
        |--__init__.py
        |--data_loaders.py
        |--logging.py
    |--db # para propositos locales y de prueba
        |--castigados.csv
    |--__init__.py
    |--config.py

Scripts:

root/run.py
Este script es el boton de arranque de toda la aplicacion web; es el entry point oficial. Su unica mision es poner a trabajar el servidor. Primero, importa la funcion create_app para construir y dejar lista la aplicacion de Flask. Despues, se importa del config el host y el puerto donde va a correr. Y para terminar, usa waitress, un servidor web, para lanzar la aplicacion y que este disponible en la red.

root/app/config.py
Este script es basicamente el centro de control de todo el proyecto. Su mision es juntar y organizar todos los parametros, variables y secretos que la aplicacion necesita para trabajar. Para empezar, usa la libreria dotenv para cargar de forma segura cualquier dato sensible (como API keys o contraseñas) desde un archivo .env, manteniendo esa info fuera del codigo fuente por seguridad. Todo esta empaquetado dentro de la clase Config, donde se define la SECRET_KEY para proteger las sesiones de usuario, las credenciales para los servicios de Google (Gemini y Sheets), los datos para el envio de emails y hasta una lista que especifica que puestos son de administrador. Tambien configura detalles mas tecnicos, como el tiempo que dura una sesion activa y detecta automaticamente la direccion IP local para que el servidor sepa donde correr. En pocas palabras, este archivo le pasa a toda la app la configuracion que necesita para encender y operar correctamente.

root/app/admin/decorators.py

root/app/admin/routes.py

root/app/auth/routes.py

root/app/evaluation/prmpt_generator.py

root/app/evaluation/routes.py

root/app/evaluation/services.py

root/app/main/routes.py

root/app/services/email_service.py

root/app/services/settings_service.py

root/app/services/sheets_service.py

root/app/utils/data_loaders.py

root/app/utils/logging.py
