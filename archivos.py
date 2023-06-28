# archivos.py
import os
from registros import configurar_logger

class Archivos:
    def __init__( self, config=None ):

        # Manejador de registros
        self.archivos_registrar = configurar_logger( "archivos", "archivos.log" )
        self.config = config

        self.TIPOS_AUDIO = ["mp3","m4a","wav"]
        self.TIPO_NO_PERMITIDO = '2'
        self.NOMBRE_NO_VALIDO = '3'
        self.ARCHIVO_YA_EXISTE = '4'

    # Función para validar y cargar archivo
    def cargar_archivo( self, archivo ):
        import re
        from werkzeug.utils import secure_filename
        try:
            ruta = f"{self.config.RUTA.get('ARCHIVOS')}/{self.config.CARPETA}"

            # Evalua si archivo cumple requisitos
            filename = secure_filename( archivo.filename )
            if not self._es_tipo_permitido( filename ):
                return self.TIPO_NO_PERMITIDO

            # Evalua el nombre del archivo
            nombre_base, extension = os.path.splitext( self._limpiar_nombre_archivo( filename, 200 ) )
            if not nombre_base:
                return self.NOMBRE_NO_VALIDO

            nombre_base = re.sub( r"\.", "", nombre_base )
            nombre_disponible = self._encontrar_nombre_disponible( ruta, nombre_base, extension[1:], True )
            if nombre_disponible is None:
                return self.ARCHIVO_YA_EXISTE

            # Guarda el archivo en la ubicacion indicada
            archivo.save( f"{ruta}/{nombre_disponible}" )
            return nombre_disponible

        except Exception as e:
            self.archivos_registrar.error( f"{e}" )
            return "0"

    # Función para borrar un archivo, si existe
    def borrar_archivo( self, ruta ):
        if os.path.isfile( ruta ):
            os.remove( ruta )
            return True
        return False

    # Función para borrar una carpeta, si existe
    def borrar_carpeta( self, ruta ):
        import shutil
        borrado = False
        if os.path.isdir( ruta ):
            try:
                shutil.rmtree(ruta)
                borrado = True
            except Exception as e:
                borrado = False
        return borrado

    # Función para comprobar si un archivo existe
    def comprobar_archivo( self, ruta ):
        if os.path.isfile( ruta ):
            return True
        return False

    # Función para comprobar si una carpeta existe
    def comprobar_carpeta( self, ruta ):
        if os.path.isdir( ruta ):
            return True
        return False

    # Función para crear una carpeta en una ruta, si no existe
    def crear_carpeta( self, ruta ):
        if not os.path.isdir( ruta ):
            os.makedirs( ruta )
            return True
        return False

    # Función para obtener los atributos de un archivo (nombre, extensión, peso, ruta)
    def obtener_atributos( self, archivo="" ):
        atributos = []
        ruta_directorio = f"{self.config.RUTA.get('ARCHIVOS')}/{self.config.CARPETA}"
        ruta_completa = f"{ruta_directorio}/{archivo}"
        if os.path.exists( ruta_completa ):
            archivo_nombre, archivo_extension = os.path.splitext( os.path.basename( ruta_completa ) )
            archivo_extension = str( archivo_extension ).replace( ".", "" )
            archivo_peso_bytes = os.path.getsize( ruta_completa )
            archivo_peso_kb = round(( archivo_peso_bytes / 1024 ), None)
            atributos = [ archivo_nombre, archivo_extension, archivo_peso_kb, ruta_completa, ruta_directorio ]
        return atributos

    # Función para obtener la ruta de un tipo de recurso
    def obtener_ruta( self, tipo_recurso ):
        ruta = None
        if tipo_recurso:

            if tipo_recurso == "INDICES":
                ruta = f"{self.config.RUTA.get('INDICES')}/{self.config.CARPETA}"

            elif tipo_recurso == "ARCHIVOS":
                ruta = f"{self.config.RUTA.get('ARCHIVOS')}/{self.config.CARPETA}"

            elif tipo_recurso == "TEMP":
                ruta = f"{self.config.RUTA.get('TEMP')}"

            elif tipo_recurso == "SESIONES":
                ruta = f"{self.config.RUTA.get('SESIONES')}"

            elif tipo_recurso == "DATOS":
                ruta = f"{self.config.RUTA.get('DATOS')}"

            elif tipo_recurso == "CONFIG":
                ruta = f"{self.config.RUTA.get('CONFIG')}"

        return ruta

    # Función para cargar imagen y guardarla en diferentes formatos
    def cargar_imagen( self, archivo, aplicacion ):
        from PIL import Image

        if aplicacion and archivo:
            try:
                sizes = [ 32, 48, 64, 72, 96, 128, 144, 152, 192, 256, 384, 512 ]
                image = Image.open( archivo.stream )
                if image.format != 'PNG' or image.size != (512, 512):
                    return False
                
                aux = self.config.COLECCION
                self.config.COLECCION = aplicacion
                resized_images = []
                for size in sizes:
                    new_image = image.resize( (size, size), Image.LANCZOS )
                    resized_images.append( new_image )
                for size, resized_image in zip( sizes, resized_images ):
                    if size in [ 32, 48 ]:
                        resized_image.save( f"{self.config.RUTA.get('PWA')}/favicon-{size}x{size}.ico", format='ICO' )
                    elif size in [ 64 ]:
                        resized_image.save( f"{self.config.RUTA.get('PWA')}/favicon.ico", format='ICO' )
                    else:
                        resized_image.save( f"{self.config.RUTA.get('PWA')}/icon-{size}x{size}.png" )
                self.config.COLECCION = aux
                return True

            except Exception as e:
                self.archivos_registrar.error( f"{e}" )

        return False

    # Función para guardar un archivo subido en una ruta
    def guardar_archivo( self, archivo, nombre, directorio ):
        try:
            ruta = self.obtener_ruta( directorio )
            archivo.save( f"{ruta}/{nombre}" )
            return True
        except Exception as e:
            self.archivos_registrar.error( f"{e}" )
        return False

    # Función para obtener lista de nombres de archivo de una extensión en una ruta
    def obtener_lista_archivos( self, extension, ruta ):
        import glob
        try:
            archivos_filtrados = []
            archivos_filtrados.extend( glob.glob(f"{ruta}/*.{extension}") )
            lista = [ os.path.splitext( os.path.basename(archivo))[0] for archivo in archivos_filtrados ]
        except Exception as e:
            lista = []

        return lista

    # Función para validar y cargar archivo de audio
    def cargar_audio( self, archivo, ruta, nombre ):
        from werkzeug.utils import secure_filename
        try:
            ruta_destino = self.obtener_ruta(ruta)

            # Evalua si archivo cumple requisitos
            filename = secure_filename( archivo.filename )
            if not self._es_audio_permitido( filename ):
                return self.TIPO_NO_PERMITIDO

            original, extension = os.path.splitext( self._limpiar_nombre_archivo( filename, 200 ) )
            ruta_final = f"{ruta_destino}/{nombre}{extension}"

            # Guarda el archivo en la ubicacion indicada
            archivo.save( ruta_final )
            return ruta_final

        except Exception as e:
            self.archivos_registrar.error( f"{e}" )
            return "0"

######################################################
# FUNCIONES PRIVADAS
######################################################

    # Funcion para evaluar tipo de archivo
    def _es_tipo_permitido( self, archivo='' ):
        return '.' in archivo and archivo.rsplit( '.', 1 )[1].lower() in self.config.TIPOS_ARCHIVO

    # Funcion para evaluar tipo de archivo
    def _es_audio_permitido( self, archivo='' ):
        return '.' in archivo and archivo.rsplit( '.', 1 )[1].lower() in self.TIPOS_AUDIO

    # Funcion para limpiar el nombre del archivo
    def _limpiar_nombre_archivo( self, nombre='', largo=200 ):
        import re, unicodedata
        try:
            archivo, extension = os.path.splitext( nombre )
            archivo = unicodedata.normalize( 'NFD', archivo ).encode( 'ascii', 'ignore' ).decode( 'utf-8' )
            archivo = archivo.lower()
            archivo = re.sub( r" ", "-", archivo )
            archivo = re.sub( r"_", "-", archivo )
            archivo = re.sub( r"---", "-", archivo )
            archivo = re.sub( r"--", "-", archivo )
            archivo = re.sub( r'[\\/:"*?<>|°ºª~!#$%&=¿¡+\[\]{};.,\']', '', archivo )
            archivo = f"{archivo[:largo]}{extension}"
            return archivo
        except Exception as e:
            self.archivos_registrar.error( f"{e}" )
            return None

    # Funcion para comprobar si nombre de archivo esta disponible
    def _encontrar_nombre_disponible( self, ruta='', nombre_base='', extension='', estricto=True ):
        if estricto:
            nombre_nuevo = f"{nombre_base}.{extension}"
            ruta_completa = f"{ruta}/{nombre_nuevo}"
            if not os.path.exists( ruta_completa ):
                return nombre_nuevo
        else:
            for i in range( 1, 100 ):
                if i == 1:
                    nombre_nuevo = f"{nombre_base}.{extension}"
                else:
                    nombre_nuevo = f"{nombre_base}({i}).{extension}"
                ruta_completa = f"{ruta}/{nombre_nuevo}"
                if not os.path.exists( ruta_completa ):
                    return nombre_nuevo
        return None
