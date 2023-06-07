# usuarios.py
import json
import jwt
from registros import configurar_logger
from basedatos import BaseDatos

class Usuarios:
    def __init__( self, config=None ):

        # Manejador de registros
        self.usuarios_registrar = configurar_logger( "usuarios", "usuarios.log" )
        self.config = config

######################################################
# FUNCIONES PUBLICAS
######################################################

    # Función para iniciar sesión de usuario
    def iniciar_sesion( self, login, password ):
        token = None
        try:
            bd = BaseDatos(self.config)
            password_cifrada = self.config.cifrar_texto( password )
            datos_usuario = bd.comprobar_usuario( usuario=login, password=password_cifrada )
            resultado = True if datos_usuario is not None else False
            if resultado:
                id_usuario, alias, email, roles = datos_usuario
                token = self._crear_token( id_usuario )
                if token:
                    archivo_usuario = f"{self.config.RUTA.get('SESIONES')}/{id_usuario}.json"
                    try:
                        with open( archivo_usuario, 'r', encoding='utf-8' ) as f:
                            self.config.USUARIO = json.load( f )
                    except Exception as e:
                        self.config.USUARIO['id'] = id_usuario
                    self.config.USUARIO['id'] = id_usuario
                    self.config.USUARIO['alias'] = alias
                    self.config.USUARIO['email'] = email
                    self.config.USUARIO['roles'] = roles
                    with open( archivo_usuario, 'w', encoding='utf-8' ) as f:
                        json.dump( self.config.USUARIO, f )
        except Exception as e:
            token = None
            self.usuarios_registrar.error( f"{e}" )

        return token

    # Función para recuperar valores de la sesión del usuario a partir de su token
    def recuperar_sesion( self, token ):
        sesion = self._validar_token( token=token )
        if sesion:
            try:
                id_usuario = sesion.get('sub')
                archivo_usuario = f"{self.config.RUTA.get('SESIONES')}/{id_usuario}.json"
                with open( archivo_usuario, 'r', encoding='utf-8' ) as f:
                    self.config.USUARIO = json.load( f )
                if not self.config.APP.get('openai_api_key', None):
                    if self.config.USUARIO.get('openai_api_key', None):
                        self.config.APP['openai_api_key'] = self.config.USUARIO.get('openai_api_key')
                return True

            except Exception as e:
                self.usuarios_registrar.error( f"{e}" )

        return False

    # Función para crear un nuevo usuario
    def crear_usuario( self, parametros={} ):
        uid = 0
        bd = BaseDatos(self.config)
        if parametros:
            clave = parametros.get('clave', None)
            email = parametros.get('email', None)
            if clave:
                if not bd.verificar_email( email=email ):
                    clave_encriptada = self.config.cifrar_texto( clave )
                    parametros['clave'] = clave_encriptada
                    uid = bd.agregar_usuario( parametros=parametros )
        return uid

    # Función para consultar la nómina de usuarios en la BD
    def consultar_usuarios( self, parametros={} ):
        resultados = None
        if parametros:
            try:
                nav = 1
                aux = parametros.get('nav', 1)
                if aux:
                    nav = int(aux)
                max = 100
                aux = parametros.get('max', 100)
                if aux:
                    max = int(aux)

                bd = BaseDatos(self.config)
                resultados = bd.buscar_usuarios( parametros=parametros, pagina=nav, casos=max )

            except KeyError as e:
                self.gestor_registrar.error( f"{e}" )

            except Exception as e:
                self.gestor_registrar.error( f"{e}" )

        return resultados

    # Función para obtener los datos de un usuario
    def abrir_usuario( self, uid=0 ):
        resultados = None
        if uid:
            try:
                bd = BaseDatos(self.config)
                resultados = bd.abrir_usuario( uid=uid )

            except KeyError as e:
                self.usuarios_registrar.error( f"{e}" )

            except Exception as e:
                self.usuarios_registrar.error( f"{e}" )

        return resultados

    # Función para actualizar los datos de un usuario
    def guardar_usuario( self, uid=0, parametros={} ):
        bd = BaseDatos(self.config)
        guardado = bd.actualizar_usuario(
            uid = uid,
            parametros = parametros
        )
        return guardado

    # Función para borrar un usuario
    def borrar_usuario( self, uid=0 ):
        bd = BaseDatos(self.config)
        borrado = bd.borrar_usuario(
            uid = uid
        )
        return borrado

    # Función para guardar variables en archivo de sesión
    def guardar_variable( self, variable=None, valor=None ):
        if variable and valor:
            try:
                archivo_usuario = f"{self.config.RUTA.get('SESIONES')}/{self.config.USUARIO.get('id')}.json"
                with open( archivo_usuario, 'r', encoding='utf-8' ) as f:
                    self.config.USUARIO = json.load( f )
                self.config.USUARIO[variable] = str(valor)
                with open( archivo_usuario, 'w', encoding='utf-8' ) as f:
                    json.dump( self.config.USUARIO, f )
                return True
            except Exception as e:
                self.usuarios_registrar.error( f"{e}" )
                return False
        return False


######################################################
# FUNCIONES PRIVADAS
######################################################

    # Función para crear un token de sesión
    def _crear_token( self, usuario, duracion=8 ):
        import datetime
        if usuario:
            try:
                payload = {
                    'exp': datetime.datetime.utcnow() + datetime.timedelta( hours = duracion ),
                    'iat': datetime.datetime.utcnow(),
                    'sub': usuario
                }
                return jwt.encode( payload, self.config.APP.get('token_key'), algorithm = 'HS256' )
            except Exception as e:
                self.usuarios_registrar.error( f"{e}" )

        return None

    # Función para validar un token de sesión
    def _validar_token( self, token ):
        try:
            payload = jwt.decode( token, self.config.APP.get('token_key'), algorithms = ['HS256'] )
            return payload
        except ( jwt.ExpiredSignatureError, jwt.InvalidTokenError ):
            return None

