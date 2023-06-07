# registros.py
import logging
from flask import request

# Clase para agregar "url" y "remote_addr" al formato de registro
class RequestFormatter( logging.Formatter ):
    def format( self, record ):
        if request:
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.method = request.method
        else:
            record.url = ''
            record.remote_addr = ''
            record.method = ''
        return super().format( record )

# Configuración de formato común para todos los registros
FORMATO_LOGS = RequestFormatter( '%(asctime)s - %(levelname)s - %(url)s [%(method)s] %(message)s', "%d/%m/%Y %H:%M" )

# Función para configurar el archivo donde se guardan los registros de cada módulo
def configurar_logger( logger_name, log_file ):

    # Establece el nivel de registro
    logger = logging.getLogger( logger_name )
    logger.setLevel( logging.INFO )

    # Crea un manejador de archivos y configura el formato
    file_handler = logging.FileHandler( f"./logs/{log_file}" )
    file_handler.setFormatter( FORMATO_LOGS )

    # Agrega el manejador de archivos al registrador
    logger.addHandler( file_handler )
    return logger
