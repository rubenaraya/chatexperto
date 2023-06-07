# config.py
import os, datetime, json

class Config:
    def __init__( self, coleccion='' ):

        # Propiedades
        self.VERSION = '1.0.0'
        self.CARPETA = ''
        self.APP = {}
        self.TIPOS_ARCHIVO = []
        self.USUARIO = {
            "id": "0",
            "alias": "",
            "email": "",
            "roles": "invitado"
        }
        self.COLECCION = coleccion

        # Carga configuraciones de sistema
        self.MENSAJES = self.cargar_valores('mensajes.json')
        self.colecciones = self.cargar_valores('colecciones.json')

    # Funciones para establecer el valor de la propiedad COLECCION
    @property
    def COLECCION( self ):
        return self._coleccion
    @COLECCION.setter
    def COLECCION( self, value ):
        self._coleccion = value
        self._actualizar_rutas()

    # Función interna para actualizar el diccionario de rutas cuando se cambia de COLECCION
    def _actualizar_rutas( self ):
        self.RUTA = {
            'LOGS' : './logs',
            'DATOS': './data',
            'SISTEMA': './data/cfg',
                'BASEDATOS' : f"./data/{self._coleccion}/bd",
                'CONFIG': f"./data/{self._coleccion}/cfg",
                'PWA': f"./data/{self._coleccion}/pwa",
                'SESIONES': f"./data/{self._coleccion}/sesiones",
                'TEMP': f"./data/{self._coleccion}/temp",
                'ARCHIVOS': f"./data/{self._coleccion}/archivos",
                'INDICES': f"./data/{self._coleccion}/indices",
        }
        if len(self._coleccion) > 0:
            self.APP = self.cargar_valores('config.json')
            if self.APP:
                self.APP['coleccion'] = self._coleccion
                self.APP['version'] = self.VERSION
                self.APP['fecha'] = datetime.date.today().strftime( "%d/%m/%Y" )
                self.APP['hora'] = datetime.datetime.now().strftime( "%H:%M" )
                self.APP['ahora'] = datetime.datetime.now().strftime( "%Y%m%d%H%M%S" )
                self.CARPETA = self.APP.get('carpeta', '')

######################################################
# FUNCIONES PUBLICAS
######################################################

    # Función para cargar un conjunto de datos de configuración desde un archivo JSON
    def cargar_valores( self, archivo=None ):
        import json
        data = []
        try:
            if archivo:
                ruta_completa = f"{self.RUTA.get('CONFIG')}/{archivo}"
                if not os.path.isfile( ruta_completa ):
                    ruta_completa = f"{self.RUTA.get('SISTEMA')}/{archivo}"
                    if not os.path.isfile( ruta_completa ):
                        data = []

                with open( ruta_completa, 'r', encoding='utf-8' ) as f:
                    data = json.load( f )
        except Exception as e:
            data = []

        return data

    # Función para comprobar si una colección existe
    def comprobar_coleccion( self, nombre_coleccion ):
        try:
            existe_en_json = any( coleccion["coleccion"] == nombre_coleccion for coleccion in self.colecciones )
            existe_directorio = os.path.exists( f"{self.RUTA.get('DATOS')}/{nombre_coleccion}" )
            return existe_en_json and existe_directorio
        except Exception as e:
            return False

    # Función para agregar una nueva colección y generar su estructura en el disco
    def agregar_coleccion( self, nombre_coleccion, etiqueta_coleccion ):
        try:
            if not self.comprobar_coleccion( nombre_coleccion ):
                os.makedirs( f"{self.RUTA.get('DATOS')}/{nombre_coleccion}" )
                nombre_coleccion_data = {
                    "coleccion": nombre_coleccion,
                    "etiqueta": etiqueta_coleccion
                }
                self.colecciones.append( nombre_coleccion_data )
                self.guardar_colecciones()
                return True
            return False
        except Exception as e:
            return False

    # Función para guardar información actualizada en el archivo JSON de configuración de colecciones
    def guardar_colecciones( self ):
        try:
            with open( f"{self.RUTA.get('SISTEMA')}/colecciones.json", "w", encoding='utf-8' ) as f:
                json.dump( self.colecciones, f, indent=4 )
                return True
        except Exception as e:
            return False

    # Función para importar la estructura y sobreescribir los contenidos de una colección existente
    def importar_coleccion( self, nombre_coleccion, archivo_zip ):
        import zipfile
        try:
            if self.comprobar_coleccion( nombre_coleccion ):
                ruta_coleccion = f"{self.RUTA.get('DATOS')}/{nombre_coleccion}"

                with zipfile.ZipFile( archivo_zip, 'r' ) as zipf:
                    zipf.extractall( ruta_coleccion )
                return True
            return False
        except Exception as e:
            return False

    # Función para cifrar texto con SHA-256
    def cifrar_texto( self, texto ):
        import hashlib

        if texto:
            # Crea un objeto hash SHA-256
            sha256 = hashlib.sha256()

            # Agrega el texto en formato de bytes al objeto hash
            sha256.update( texto.encode() )

            # Obtiene y devuelve el hash en formato hexadecimal
            hash_hex = sha256.hexdigest()
            return hash_hex

        return texto
