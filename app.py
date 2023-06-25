# app.py
#######################################################
# CHAT EXPERTO (Back-end) - Actualizado el: 23/06/2023
#######################################################
"""
Aplicación WEB-REST en Python para implementar un back-end para múltiples servicios de Chat inteligentes que responden preguntas sobre bases de conocimiento personalizadas.
Diseñado y desarrollado por Rubén Araya Tagle (rubenarayatagle@gmail.com), con la asistencia de GPT (el modelo de generación de lenguaje a gran escala de OpenAI).
Licencia: MIT (2023).
"""
import os, sys, time
from flask import Flask, jsonify, request, render_template, redirect, make_response
from flask_cors import CORS, cross_origin
from registros import configurar_logger
from config import Config
from gestor import GestorColeccion

######################################################
# 1. SECUENCIA DE COMANDOS DE INICIO
######################################################

# Configura el manejador de registros "app_registrar"
sys.path.insert( 0, os.path.dirname( __file__ ) )
app_registrar = configurar_logger( "app", "app.log" )

# Crea y configura la Aplicación Web-REST con Flask y Cors
app = Flask( __name__ )
cors = CORS( app )
app.config[ 'CORS_HEADERS' ] = 'Content-Type'

# Configura manejador de encabezados para respuestas JSON
@app.after_request
def set_response_headers( response ):
    if response.content_type == 'application/json':
        response.headers[ 'Content-Type' ] = 'application/json; charset=utf-8'
    return response

# Configura los manejadores de errores de la App
@app.errorhandler( 500 )
def error_500( error ):
    app_registrar.error( error )
    return jsonify( {'error': str(error)} ), 500
@app.errorhandler( 503 )
def error_503( error ):
    app_registrar.error( error )
    return jsonify( {'error': str(error)} ), 503
@app.errorhandler( 400 )
def error_400( error ):
    app_registrar.error( error )
    return jsonify( {'error': str(error)} ), 400
@app.errorhandler( 401 )
def error_401( error ):
    app_registrar.error( error )
    return jsonify( {'error': str(error)} ), 401
@app.errorhandler( 403 )
def error_403( error ):
    app_registrar.error( error )
    return jsonify( {'error': str(error)} ), 403
@app.errorhandler( 404 )
def error_404( error ):
    return jsonify( {'error': str(error)} ), 404
@app.errorhandler( 405 )
def error_405( error ):
    app_registrar.error( error )
    return jsonify( {'error': str(error)} ), 405
@app.errorhandler( Exception )
def global_exception_handler( error ):
    app_registrar.error( error )
    return jsonify( {'error': str(error)} ), 500


######################################################
# 2. RUTEADOR DE LA APLICACION WEB-REST
######################################################

######################################################
# API REST PARA APLICACIONES EXTERNAS (5)
# "/<coleccion>/chat_bot" (POST) [K]
# "/<coleccion>/chat/<int:uid>" (POST) [K]
# "/<coleccion>/mibiblioteca" (GET) [K]
# "/<coleccion>/mibiblioteca" (POST) [K]
# "/<coleccion>/misdestacados" (GET) [K]
######################################################
# APLICACION WEB GENERICA (5):
# "/<coleccion>" (GET)
# "/<coleccion>/login" (GET)
# "/<coleccion>/login" (POST)
# "/<coleccion>/inicio" (GET) [T]
# "/<coleccion>/pwa/<path:recurso>" (GET)
######################################################
# APLICACION WEB PARA ADMINISTRAR COLECCIONES (28):
# "/<coleccion>/chat" (GET) [T]
# "/<coleccion>/chat" (POST) [T]
# "/<coleccion>/revisar" (GET) [T]
# "/<coleccion>/revisar" (POST) [T]
# "/<coleccion>/subir" (GET) [T]
# "/<coleccion>/subir" (POST) [T]
# "/<coleccion>/actualizar" (GET) [T]
# "/<coleccion>/actualizar" (POST) [T]
# "/<coleccion>/admin" (GET) [T]
# "/<coleccion>/admin" (POST) [T]
# "/<coleccion>/imagen" (GET) [T]
# "/<coleccion>/imagen" (POST) [T]
# "/<coleccion>/carpetas" (GET) [T]
# "/<coleccion>/carpetas" (POST) [T]
# "/<coleccion>/carpetas/<carpeta>" (DELETE) [T]
# "/<coleccion>/usuarios" (GET) [T]
# "/<coleccion>/usuarios" (POST) [T]
# "/<coleccion>/usuario/<int:uid>" (GET) [T]
# "/<coleccion>/usuario/<int:uid>" (POST) [T]
# "/<coleccion>/usuario/<int:uid>" (DELETE) [T]
# "/<coleccion>/archivos" (GET) [T]
# "/<coleccion>/archivos" (POST) [T]
# "/<coleccion>/archivo/<int:uid>" (GET) [T]
# "/<coleccion>/archivo/<int:uid>" (POST) [T]
# "/<coleccion>/archivo/<int:uid>" (DELETE) [T]
# "/<coleccion>/descarga/<codigo>" (GET) [T]
# "/<coleccion>/metadatos/<int:uid>" (GET) [T]
# "/<coleccion>/metadatos/<int:uid>" (POST) [T]
######################################################
# APLICACION WEB PARA USAR COLECCIONES (32):
# "/<coleccion>/cargar" (GET) [T]
# "/<coleccion>/cargar" (POST) [T]
# "/<coleccion>/miscarpetas" (GET) [T]
# "/<coleccion>/documentos" (POST) [T]
# "/<coleccion>/documentos" (GET) [T]
# "/<coleccion>/documento/<int:uid>" (GET) [T]
# "/<coleccion>/asistente" (GET) [T]
# "/<coleccion>/chatdoc" (GET) [T]
# "/<coleccion>/chatdoc" (POST) [T]
# "/<coleccion>/biblioteca" (GET) [T]
# "/<coleccion>/biblioteca" (POST) [T]
# "/<coleccion>/biblioteca" (PUT)
# "/<coleccion>/tutor" (GET) [T]
# "/<coleccion>/apikey" (POST) [T]
# "/<coleccion>/chatdoc/<carpeta>" (GET) [T]
# "/<coleccion>/chatdoc/<carpeta>" (POST) [T]
# "/<coleccion>/importar" (GET) [T]
# "/<coleccion>/importar" (POST) [T]
# "/<coleccion>/exportar/<carpeta>" (GET) [T]
# "/<coleccion>/indexar" (POST) [T]
# "/<coleccion>/destacados" (GET) [T]
# "/<coleccion>/prompts" (GET) [T]
# "/<coleccion>/prompts" (POST) [T]
# "/<coleccion>/prompts" (DELETE) [T]
# "/<coleccion>/guardarchat" (GET) [T]
# "/<coleccion>/plantillas" (POST) [T]
# "/<coleccion>/plantillas" (GET) [T]
# "/<coleccion>/plantilla" (POST)
# "/<coleccion>/plantilla/<int:uid>" (GET)
# "/<coleccion>/plantilla/<int:uid>" (PUT)
# "/<coleccion>/plantilla/<int:uid>" (DELETE)
# "/<coleccion>/audio" (POST)

######################################################
# URL: "/<coleccion>" (GET)
# Página pública que se muestra al abrir el EntryPoint de la App en el navegador
@app.route( '/<coleccion>', methods=['GET'] )
def interfaz_raiz( coleccion ):
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Entrega la interfaz HTML
    return render_template( 'raiz.html', app=config.APP, dir_base=request.script_root )

######################################################
# URL: "/<coleccion>/" (GET)
# Redirecciona a interfaz_raiz
@app.route( '/<coleccion>/', methods=['GET'] )
def redirector_raiz( coleccion ):
    return redirect( f"{request.script_root}/{coleccion}" )

######################################################
# URL: "/<coleccion>/pwa/<path:recurso>" (GET)
# Proporciona una ruta para acceder a recursos en la carpeta "pwa"
@app.route( '/<coleccion>/pwa/<path:recurso>' )
def archivos_pwa( coleccion, recurso ):
    from flask import send_from_directory
    from flask import render_template_string
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    pwa_directory = config.RUTA.get('PWA')
    if recurso == "manifest.json":
        dir_base=request.script_root
        with open( f"{pwa_directory}/manifest.txt", "r", encoding="utf-8" ) as f:
            manifest_template = f.read()

        manifest = render_template_string(
            manifest_template,
            short_name = config.APP.get('app_nombre'),
            name = config.APP.get('app_nombre'),
            description = config.APP.get('descripcion'),
            start_url = f"{dir_base}/{config.COLECCION}/inicio",
            scope = f"{dir_base}/{config.COLECCION}",
            app_id = config.APP.get('app_id'),
            icons_src = f"{dir_base}/{config.COLECCION}/pwa",
        )
        response = make_response( manifest )
        response.headers.set("Content-Type", "application/json; charset=utf-8")
        return response
    else:
        return send_from_directory(pwa_directory, recurso)

######################################################
# URL: "/<coleccion>/inicio" (GET) [T]
# Proporciona una interfaz HTML con la página principal de la app-web
@app.route( '/<coleccion>/inicio', methods=['GET'] )
def interfaz_inicio( coleccion ):
    roles = ["Admin", "Editor", "Usuario"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Entrega la interfaz HTML
    return render_template( 'inicio.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, menus = config.cargar_valores( 'menus.json' ) )

######################################################
# URL: "/<coleccion>/login" (GET)
# Proporciona una interfaz HTML con un formulario para iniciar sesión
@app.route( '/<coleccion>/login', methods=['GET'] )
def interfaz_login( coleccion ):
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Entrega la interfaz HTML
    return render_template( 'login.html', app=config.APP, dir_base=request.script_root,
            menu = traspasar_menu( 'login', config )
        )

######################################################
# URL: "/<coleccion>/chat" (GET) [T]
# Proporciona una interfaz HTML con un cliente de chat para interactuar
@app.route( '/<coleccion>/chat', methods=['GET'] )
def interfaz_chat( coleccion ):
    roles = ["Admin"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Entrega la interfaz HTML
    html = render_template( 'chat.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO,
            menu = traspasar_menu( 'chat', config ), 
            CHAT_MSG_SALUDO = config.MENSAJES.get('CHAT_MSG_SALUDO'),
            CHAT_MSG_TUPREGUNTA = config.MENSAJES.get('CHAT_MSG_TUPREGUNTA'),
            opciones_carpetas = config.cargar_valores( 'carpetas.json' ),
            diccionario = config.cargar_valores( 'diccionario.json' )
        )

    # Lee el valor de la cookie de sesión, si no existe lo crea y asigna
    import uuid
    id_sesion = request.cookies.get('id_sesion')
    if not id_sesion:
        id_sesion = str(uuid.uuid4())

    # Crea una respuesta a partir del HTML y configura la cookie
    response = make_response( html )
    response.set_cookie(
        key = 'id_sesion',
        value= id_sesion,
        httponly = False
    ) 
    return response

######################################################
# URL: "/<coleccion>/subir" (GET) [T]
# Proporciona una interfaz HTML con un formulario para subir un archivo
@app.route( '/<coleccion>/subir', methods=['GET'] )
def interfaz_subir( coleccion ):
    roles = ["Admin"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Entrega la interfaz HTML
    return render_template( 'subir.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO,
            menu = traspasar_menu( 'subir', config ), 
            opciones_carpetas = config.cargar_valores( 'carpetas.json' )
        )

######################################################
# URL: "/<coleccion>/login" (POST)
# valida al usuario e inicia su sesión
@app.route( '/<coleccion>/login', methods=['POST'] )
def funcion_login( coleccion ):
    from usuarios import Usuarios
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Comprueba las credenciales del usuario
    username = request.form.get( 'username' )
    password = request.form.get( 'password' )

    usuario = Usuarios(config)
    token = usuario.iniciar_sesion( login=username, password=password )
    if token:
        response = make_response( redirect( f"{request.script_root}/{coleccion}/inicio" ) )
        response.set_cookie(
            key = 'token',
            value = token,
            httponly = False
        )
        return response
    else:
        return redirect( f"{request.script_root}/{coleccion}/login" )

######################################################
# URL: "/<coleccion>/actualizar" (GET) [T]
# Proporciona una interfaz HTML con un formulario para solicitar actualización de la base de conocimiento
@app.route( '/<coleccion>/actualizar', methods=['GET'] )
def interfaz_actualizar( coleccion ):
    roles = ["Admin"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Entrega la interfaz HTML
    return render_template('actualizar.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO,
            menu = traspasar_menu( 'actualizar', config ), 
            opciones_carpetas = config.cargar_valores( 'carpetas.json' )
        )

######################################################
# URL: "/<coleccion>/admin" (GET) [T]
# Proporciona una interfaz HTML para revisar la lista de colecciones y crear nueva colección
@app.route( '/<coleccion>/admin', methods=['GET'] )
def interfaz_admin( coleccion ):
    roles = ["Admin"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Entrega la interfaz HTML
    return render_template( 'admin.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            menu = traspasar_menu( 'admin', config ),
            opciones_colecciones = config.cargar_valores( 'colecciones.json' )
        )

######################################################
# URL: "/<coleccion>/carpetas" (GET) [T]
# Proporciona una interfaz HTML para revisar la lista de carpetas
@app.route( '/<coleccion>/carpetas', methods=['GET'] )
def interfaz_carpetas( coleccion ):
    roles = ["Admin"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Entrega la interfaz HTML
    return render_template( 'carpetas.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            menu = traspasar_menu( 'carpetas', config ),
            lista_carpetas = config.cargar_valores( 'carpetas.json' ),
            diccionario = config.cargar_valores( 'diccionario.json' )
        )

######################################################
# URL: "/<coleccion>/usuarios" (GET) [T]
# Proporciona una interfaz HTML para revisar la lista de usuarios
@app.route( '/<coleccion>/usuarios', methods=['GET'] )
def interfaz_usuarios( coleccion ):
    from usuarios import Usuarios
    roles = ["Admin"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Lee y asigna los parámetros de la consulta
    parametros = {
        "alias": obtener_parametro( 'alias' ),
        "email": obtener_parametro( 'email' ),
        "estado": obtener_parametro( 'estado' ),
        "max": obtener_parametro( 'max' ),
        "nav": obtener_parametro( 'nav' )
    }

    # Realiza la consulta con los parámetros
    usuarios = Usuarios(config)
    resultados = usuarios.consultar_usuarios( parametros=parametros )

    # Entrega la interfaz HTML
    return render_template( 'usuarios.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            menu = traspasar_menu( 'usuarios', config ),
            diccionario = config.cargar_valores( 'diccionario.json' ),
            lista_usuarios = resultados
        )

######################################################
# URL: "/<coleccion>/archivos" (GET) [T]
# Proporciona una interfaz HTML para gestionar los archivos
@app.route( '/<coleccion>/archivos', methods=['GET'] )
def interfaz_archivos( coleccion ):
    roles = ["Admin"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Entrega la interfaz HTML
    return render_template( 'archivos.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            menu = traspasar_menu( 'archivos', config ),
            diccionario = config.cargar_valores( 'diccionario.json' ),
            opciones_carpetas = config.cargar_valores( 'carpetas.json' ),
        )

######################################################
# URL: "/<coleccion>/imagen" (GET) [T]
# Proporciona una interfaz HTML con un formulario para subir una imagen
@app.route( '/<coleccion>/imagen', methods=['GET'] )
def interfaz_imagen( coleccion ):
    roles = ["Admin"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    aplicacion = obtener_parametro( 'aplicacion' )

    # Entrega la interfaz HTML
    return render_template( 'imagen.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            menu = traspasar_menu( 'imagen', config ),
            aplicacion = aplicacion
        )

######################################################
# URL: "/<coleccion>/usuarios" (POST) [T]
# Recibe instrucciones para crear un nuevo usuario
@app.route( '/<coleccion>/usuarios', methods=['POST'] )
def funcion_usuarios( coleccion ):
    from usuarios import Usuarios
    roles = ["Admin"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Asigna los parámetros recibidos
    alias = obtener_parametro( 'alias' )
    email = obtener_parametro( 'email' )
    clave = obtener_parametro( 'clave' )
    roles = obtener_parametro( 'roles' )
    parametros = {
        "alias": alias,
        "email": email,
        "clave": clave,
        "roles": roles
    }
    usuario = Usuarios(config)
    resultado = usuario.crear_usuario( parametros=parametros )

    if resultado:
        mensaje = config.MENSAJES.get('EXITO_USUARIO_CREADO')
    else:
        mensaje = config.MENSAJES.get('ERROR_USUARIO_NOCREADO')
    return jsonify( {'respuesta': mensaje} ), 200

######################################################
# URL: "/<coleccion>/miscarpetas" (GET) [T]
# Proporciona una interfaz HTML para revisar la lista de carpetas
@app.route( '/<coleccion>/miscarpetas', methods=['GET'] )
def interfaz_miscarpetas( coleccion ):
    roles = ["Editor"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Entrega la interfaz HTML
    return render_template( 'miscarpetas.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            menu = traspasar_menu( 'miscarpetas', config ),
            lista_carpetas = config.cargar_valores( 'carpetas.json' ),
            diccionario = config.cargar_valores( 'diccionario.json' )
        )

######################################################
# URL: "/<coleccion>/documentos" (GET) [T]
# Proporciona una interfaz HTML para gestionar los documentos
@app.route( '/<coleccion>/documentos', methods=['GET'] )
def interfaz_documentos( coleccion ):
    roles = ["Editor","Usuario"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    carpeta = obtener_parametro( 'carpeta' )

    # Entrega la interfaz HTML
    return render_template( 'documentos.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            menu = traspasar_menu( 'documentos', config ),
            diccionario = config.cargar_valores( 'diccionario.json' ),
            opciones_carpetas = config.cargar_valores( 'carpetas.json' ),
            carpeta = carpeta
        )

######################################################
# URL: "/<coleccion>/cargar" (GET) [T]
# Proporciona una interfaz HTML con un formulario para cargar un archivo
@app.route( '/<coleccion>/cargar', methods=['GET'] )
def interfaz_cargar( coleccion ):
    roles = ["Editor"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Entrega la interfaz HTML
    return render_template( 'cargar.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO,
            menu = traspasar_menu( 'cargar', config ), 
            opciones_carpetas = config.cargar_valores( 'carpetas.json' )
        )

######################################################
# URL: "/<coleccion>/usuario/<int:uid>" (GET) [T]
# Proporciona una interfaz HTML con un formulario para editar un usuario
@app.route( '/<coleccion>/usuario/<int:uid>', methods=['GET'] )
def interfaz_editar_usuario( coleccion, uid ):
    from usuarios import Usuarios
    roles = ["Admin"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Realiza la consulta con el uid
    usuario = Usuarios(config)
    resultados = usuario.abrir_usuario( uid=uid )

    # Entrega la interfaz HTML
    return render_template( 'usuario.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            diccionario = config.cargar_valores( 'diccionario.json' ),
            opciones_carpetas = config.cargar_valores( 'carpetas.json' ),
            datos_usuario = resultados
        )

######################################################
# URL: "/<coleccion>/usuario/<int:uid>" (POST) [T]
# Guarda los datos del usuario recibidos del formulario en la BD
@app.route( '/<coleccion>/usuario/<int:uid>', methods=['POST'] )
def funcion_guardar_usuario( coleccion, uid ):
    from usuarios import Usuarios
    roles = ["Admin"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    parametros = {}
    for campo in request.form:
        parametros[campo] = request.form[campo]

    # Ejecuta la actualización de la BD con el uid
    usuario = Usuarios(config)
    resultado = usuario.guardar_usuario( uid=uid, parametros=parametros )
 
    # Entrega el resultado
    if resultado:
        return jsonify( {'respuesta': f"{config.MENSAJES.get('EXITO_USUARIO_GUARDADO')}"} ), 200
    else:
        return jsonify( {'error': config.MENSAJES.get('ERROR_USUARIO_NOGUARDADO')} ), 200

######################################################
# URL: "/<coleccion>/usuario/<int:uid>" (DELETE) [T]
# Borra un usuario de la BD
@app.route( '/<coleccion>/usuario/<int:uid>', methods=['DELETE'] )
def funcion_borrar_usuario( coleccion, uid ):
    from usuarios import Usuarios
    roles = ["Admin"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Ejecuta la actualización de la BD con el uid
    usuario = Usuarios(config)
    resultado = usuario.borrar_usuario( uid=uid )
 
    # Entrega el resultado
    if resultado:
        return jsonify( {'respuesta': f"{config.MENSAJES.get('EXITO_USUARIO_BORRADO')}"} ), 200
    else:
        return jsonify( {'error': config.MENSAJES.get('ERROR_USUARIO_NOBORRADO')} ), 200

######################################################
# URL: "/<coleccion>/apikey" (POST) [T]
# Recibe api key para guardarla en sesión del usuario
@app.route( '/<coleccion>/apikey', methods=['POST'] )
def funcion_apikey( coleccion ):
    from usuarios import Usuarios
    roles = ["Admin","Editor","Usuario"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    apikey = obtener_parametro( 'api_key' )
    usuario = Usuarios(config)
    resultado = usuario.guardar_variable( 'openai_api_key', apikey )
    if resultado:
        return jsonify( {'respuesta': config.MENSAJES.get('EXITO_APIKEY_GUARDADA')} ), 200
    else:
        return jsonify( {'error': config.MENSAJES.get('ERROR_APIKEY_NOGUARDADA')} ), 400

######################################################
# URL: "/<coleccion>/biblioteca" (GET) [T]
# Proporciona una interfaz HTML para el buscador de documentos
@app.route( '/<coleccion>/biblioteca', methods=['GET'] )
def interfaz_biblioteca( coleccion ):
    roles = ["Editor","Usuario"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Entrega la interfaz HTML
    return render_template( 'biblioteca.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            menu = traspasar_menu( 'biblioteca', config ),
            diccionario = config.cargar_valores( 'diccionario.json' ),
            opciones_carpetas = config.cargar_valores( 'carpetas.json' ),
        )

######################################################
# URL: "/<coleccion>/tutor" (GET) [T]
# Proporciona una interfaz HTML para el tutor virtual
@app.route( '/<coleccion>/tutor', methods=['GET'] )
def interfaz_tutor( coleccion ):
    roles = ["Editor","Usuario"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Entrega la interfaz HTML
    return render_template( 'tutor.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            menu = traspasar_menu( 'tutor', config ),
            diccionario = config.cargar_valores( 'diccionario.json' ),
            opciones_carpetas = config.cargar_valores( 'carpetas.json' ),
        )

######################################################
# URL: "/<coleccion>/chat" (POST) [T]
# Recibe una pregunta desde un cliente de chat y devuelve la respuesta en formato JSON
@app.route( '/<coleccion>/chat', methods=['POST'] )
def funcion_chat( coleccion ):
    roles = ["Admin"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Validadores de la petición del usuario
    peticion = request.args.get( "p" )
    if not peticion:
        data = request.get_json()
        if data and "p" in data:
            peticion = data.get( "p" )
    if not peticion:
        return jsonify( {'respuesta': config.MENSAJES.get('CHAT_PREGUNTA_VACIA'), 'peticion': peticion} ), 200
    if len( peticion ) < 4:
        return jsonify( {'respuesta': config.MENSAJES.get('CHAT_PREGUNTA_MUYCORTA'), 'peticion': peticion} ), 200
    if len( peticion ) > 200:
        return jsonify( {'respuesta': config.MENSAJES.get('CHAT_PREGUNTA_MUYLARGA'), 'peticion': peticion} ), 200

    # Recupera parámetros de ajuste
    carpeta = obtener_parametro( 'carpeta' )
    if carpeta:
        config.CARPETA = carpeta
        parametros = {
            "llm": obtener_parametro( 'llm' ),
            "max_tokens": obtener_parametro( 'max_tokens' ),
            "temperature": obtener_parametro( 'temperature' ),
            "chain_type": obtener_parametro( 'chain_type' ),
            "num_docs": obtener_parametro( 'num_docs' )
        }

    # Crea instancia del Gestor de la Colección
    gestor = GestorColeccion(config)

    # Configura y abre el ejecutor
    if parametros:
        gestor.configurar_ejecutor( parametros=parametros )
    gestor.abrir_ejecutor()

    try:
        # Envía la solicitud al LLM y recibe la respuesta
        ini_time = time.time()
        id_sesion = request.cookies.get('id_sesion')
        respuesta = gestor.ejecutar_instruccion( peticion=peticion, id_sesion=id_sesion )
        respuesta = str( respuesta ).strip()
        tiempo = round( time.time() - ini_time, None )

        # Procesa la respuesta y devuelve el resultado
        resultado = gestor.procesar_respuesta(
            respuesta= respuesta,
            peticion = peticion,
            coleccion = config.CARPETA,
            tiempo = tiempo
        )
        respuesta = resultado.get("respuesta", "")
        uid = int(resultado.get("uid", 0))

    # Si se produce un error
    except Exception as e:
        return jsonify( {'error': config.MENSAJES.get('ERROR_GENERAL')} ), 500
    # Si no se recibe respuesta
    if not respuesta:
        return jsonify( {'respuesta': config.MENSAJES.get('CHAT_RESPUESTA_NOSE'), 'peticion': peticion} ), 200
    
    # Si todo está bien, devuelve el resultado de la interacción en formato JSON
    return jsonify({
            'respuesta': respuesta, 
            'peticion': peticion, 
            'id': uid, 'tiempo': tiempo
        }), 200

######################################################
# URL: "/<coleccion>/chat_bot" (POST) [K]
# Recibe una pregunta desde un cliente de chat y devuelve la respuesta en formato JSON
@app.route( '/<coleccion>/chat_bot', methods=['POST'] )
@cross_origin()
def funcion_chat_bot( coleccion ):
    import re
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=True, config=config ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Validadores de la petición del usuario
    peticion = request.args.get( "mensaje" )
    if not peticion:
        data = request.get_json()
        if data and "mensaje" in data:
            peticion = data.get( "mensaje" )
    if not peticion:
        return jsonify( {'respuesta': config.MENSAJES.get('CHAT_PREGUNTA_VACIA'), 'peticion': peticion} ), 200
    if len( peticion ) < 4:
        return jsonify( {'respuesta': config.MENSAJES.get('CHAT_PREGUNTA_MUYCORTA'), 'peticion': peticion} ), 200
    if len( peticion ) > 200:
        return jsonify( {'respuesta': config.MENSAJES.get('CHAT_PREGUNTA_MUYLARGA'), 'peticion': peticion} ), 200

    # Recupera id del usuario para guardar el historial
    usuario = request.headers.get( "usuario" )

    # Recupera parámetros de ajuste
    carpeta = obtener_parametro( 'carpeta' )
    if carpeta:
        config.CARPETA = carpeta

    # Crea instancia del Gestor de la Colección con la carpeta seleccionada
    gestor = GestorColeccion(config)

    try:
        # Envía la solicitud al LLM y recibe la respuesta
        gestor.abrir_ejecutor()
        respuesta = gestor.ejecutar_instruccion( peticion=peticion, id_sesion=usuario )
        respuesta = re.sub( r"\n", "", respuesta )
        respuesta = respuesta.strip()

    # Si se produce un error
    except Exception as e:
        return jsonify( {'error': config.MENSAJES.get('ERROR_GENERAL')} ), 500
    # Si no se recibe respuesta
    if not respuesta:
        return jsonify( {'respuesta': config.MENSAJES.get('CHAT_RESPUESTA_NOSE'), 'peticion': peticion} ), 200
    
    # Si todo está bien, devuelve el resultado de la interacción en formato JSON
    return jsonify({
            'respuesta': respuesta, 
            'peticion': peticion 
        }), 200

######################################################
# URL: "/<coleccion>/chat/<int:uid>" (POST) [K]
# Recibe la evaluación del usuario sobre la respuesta proporcionada en el chat
@app.route( '/<coleccion>/chat/<int:uid>', methods=['POST'] )
@cross_origin()
def funcion_evaluar( coleccion, uid ):
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=True, config=config ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Registra la evaluación de la interacción en la base de datos
    evaluacion = obtener_parametro( 'evaluacion' )
    gestor = GestorColeccion(config)
    gestor.registrar_evaluacion( uid=uid, evaluacion=evaluacion )

    # Entrega la respuesta en formato JSON
    return jsonify( {'respuesta': 'OK'} ), 200

######################################################
# URL: "/<coleccion>/revisar" (GET) [T]
# Proporciona una interfaz HTML con un formulario para revisar la base de datos de interacciones
@app.route( '/<coleccion>/revisar', methods=['GET'] )
def interfaz_revisar( coleccion ):
    roles = ["Admin"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Entrega la interfaz HTML
    return render_template( 'revisar.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            menu = traspasar_menu( 'revisar', config ) ,
            diccionario = config.cargar_valores( 'diccionario.json' )
        )

######################################################
# URL: "/<coleccion>/revisar" (POST) [T]
# Recibe peticiones de consulta sobre la base de datos de interacciones y entrega los resultados en JSON
@app.route( '/<coleccion>/revisar', methods=['POST'] )
def funcion_revisar( coleccion ):
    roles = ["Admin"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Lee y asigna los parámetros de la consulta
    parametros = {
        "palabras": obtener_parametro( 'palabras' ),
        "fecha": obtener_parametro( 'fecha' ),
        "evaluacion": obtener_parametro( 'evaluacion' ),
        "max": obtener_parametro( 'max' ),
        "nav": obtener_parametro( 'nav' )
    }

    # Realiza la consulta con los parámetros
    gestor = GestorColeccion(config)
    resultados = gestor.revisar_interacciones( parametros=parametros )

    # Entrega la respuesta en formato JSON
    return jsonify( resultados ), 200

######################################################
# URL: "/<coleccion>/subir" (POST) [T]
# Recibe el archivo subido por el usuario y lo guarda en la colección
@app.route( '/<coleccion>/subir', methods=['POST'] )
def funcion_subir( coleccion ):
    roles = ["Admin"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Comprueba si se ha seleccionado un archivo
    if 'archivo' not in request.files:
        return jsonify( {'error': config.MENSAJES.get('ERROR_DATOS_INCOMPLETOS')} ), 400

    # Valida datos de entrada y ruta
    ini_time = time.time()
    mensaje = ""
    archivo = request.files[ 'archivo' ]
    config.CARPETA = request.form.get( 'carpeta' )
    if not archivo or not config.CARPETA:
        return jsonify( {'error': config.MENSAJES.get('ERROR_DATOS_INCOMPLETOS')} ), 400

    # Crea instancia del Gestor de la Colección
    gestor = GestorColeccion(config)
    subir = gestor.subir_archivo( archivo=archivo )
    if subir:
        resultado = subir.get('resultado')
        mensaje = f"{subir.get('mensaje')}. "
        nombre = subir.get('nombre')
        if resultado == 'ERROR':
            return jsonify( {'error': mensaje} ), 400
    else:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ARCHIVO_NOSUBIDO')} ), 400

    # Recupera opciones para indexar y catalogar el archivo
    ingresar = request.form.get( 'ingresar' )
    indexar = request.form.get( 'indexar' )
    catalogar = request.form.get( 'catalogar' )

    # Ingresa el archivo en BD si se solicitó
    if ingresar == '1':
        id_doc = gestor.ingresar_documento( archivo = nombre )
        if id_doc > 0:
            mensaje = f"{mensaje}{config.MENSAJES.get('EXITO_ARCHIVO_INGRESADO')}. "

            # Indexa el archivo si se solicitó
            if indexar == '1':
                indexado = gestor.almacenar_documento( id_doc = id_doc )
                if indexado:
                    mensaje = f"{mensaje}{config.MENSAJES.get('EXITO_ARCHIVO_INDEXADO')}. "
            
                    # Cataloga el archivo si se solicitó
                    if catalogar == '1':
                        campos = [ "titulo", "resumen", "sugerencias" ]
                        catalogado = gestor.catalogar_documento( id_doc=id_doc, campos=campos )
                        if catalogado:
                            mensaje = f"{mensaje}{config.MENSAJES.get('EXITO_ARCHIVO_CATALOGADO')}. "
                        else:
                            mensaje = f"{mensaje}{config.MENSAJES.get('ERROR_ARCHIVO_NOCATALOGADO')}. "
                else:
                    mensaje = f"{mensaje}{config.MENSAJES.get('ERROR_ARCHIVO_NOINDEXADO')}. "
        else:
            mensaje = f"{mensaje}{config.MENSAJES.get('ERROR_ARCHIVO_NOINGRESADO')}. "
    
    tiempo = round( time.time() - ini_time, None )
    respuesta = f"{mensaje} Tiempo: {tiempo} segundos"
    return jsonify( {'respuesta': respuesta} ), 200

######################################################
# URL: "/<coleccion>/actualizar" (POST) [T]
# Actualiza el índice vectorial de una carpeta
@app.route( '/<coleccion>/actualizar', methods=['POST'] )
def funcion_actualizar( coleccion ):
    roles = ["Admin","Editor"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Actualiza base de conocimiento con los parámetros recibidos
    config.CARPETA = obtener_parametro( 'carpeta' )
    metodo = obtener_parametro( 'metodo' )
    if not metodo:
        metodo = 'crear'

    # Crea instancia del Gestor de la Colección
    gestor = GestorColeccion(config)

    resultado = gestor.almacenar_directorio( metodo=metodo )
    if resultado:
        mensaje = f"{config.MENSAJES.get('EXITO_BC_ACTUALIZADA')}: {config.CARPETA}"
    else:
        mensaje = f"{config.MENSAJES.get('ERROR_BC_NOACTUALIZADA')}: {config.CARPETA}"

    return jsonify( {'respuesta': mensaje} ), 200

######################################################
# URL: "/<coleccion>/admin" (POST) [T]
# Recibe instrucciones para crear una nueva colección
@app.route( '/<coleccion>/admin', methods=['POST'] )
def funcion_admin( coleccion ):
    roles = ["Admin"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Asigna los parámetros recibidos
    coleccion = obtener_parametro( 'coleccion' )
    nombre = obtener_parametro( 'app_nombre' )
    descripcion = obtener_parametro( 'descripcion' )
    api_key = obtener_parametro( 'openai_api_key' )
    carpetas = obtener_parametro( 'carpetas' )
    chatgpt = obtener_parametro( 'chatgpt' )

    # Crea instancia del Gestor de la Colección
    gestor = GestorColeccion(config)
    resultado = gestor.crear_coleccion(
        coleccion = coleccion,
        nombre = nombre,
        descripcion = descripcion,
        api_key = api_key,
        carpetas = carpetas,
        chatgpt=chatgpt
    )

    return jsonify( {'respuesta': resultado} ), 200

######################################################
# URL: "/<coleccion>/archivo/<int:uid>" (GET) [T]
# Proporciona una interfaz HTML con un formulario para editar un archivo
@app.route( '/<coleccion>/archivo/<int:uid>', methods=['GET'] )
def interfaz_editar_archivo( coleccion, uid ):
    roles = ["Admin"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Realiza la consulta con el uid
    gestor = GestorColeccion(config)
    resultados = gestor.abrir_documento( id_doc=uid )

    # Entrega la interfaz HTML
    return render_template( 'archivo.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            diccionario = config.cargar_valores( 'diccionario.json' ),
            opciones_carpetas = config.cargar_valores( 'carpetas.json' ),
            datos_archivo = resultados
        )

######################################################
# URL: "/<coleccion>/descarga/<codigo>" (GET) [T]
# Descarga un archivo local, que corresponde a un documento por codigo
@app.route( '/<coleccion>/descarga/<codigo>', methods=['GET'] )
def descargar_archivo( coleccion, codigo ):
    from flask import send_from_directory
    roles = ["Admin","Editor","Usuario"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    """
    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401
    """

    gestor = GestorColeccion(config)
    datos_archivo = gestor.descargar_documento( codigo=codigo )
    if datos_archivo:
        ruta_archivo = datos_archivo.get('ruta', '')
        nombre_archivo = datos_archivo.get('archivo', '')
        tipo_archivo = datos_archivo.get('tipo', '')
        nombre = f"{nombre_archivo}.{tipo_archivo}"
    else:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ARCHIVO_NOEXISTE')} ), 404

    return send_from_directory( ruta_archivo, nombre )

######################################################
# URL: "/<coleccion>/imagen" (POST) [T]
# Recibe la imagen subida por el usuario y la guarda en diferentes tamaños y formatos
@app.route( '/<coleccion>/imagen', methods=['POST'] )
def funcion_imagen( coleccion ):
    roles = ["Admin"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Comprueba si se ha enviado un archivo de imagen
    if 'imagen' not in request.files:
        return jsonify( {'error': config.MENSAJES.get('ERROR_DATOS_INCOMPLETOS')} ), 400
    archivo = request.files[ 'imagen' ]
    aplicacion = request.form.get( 'aplicacion' )
    if not archivo:
        return jsonify( {'error': config.MENSAJES.get('ERROR_DATOS_INCOMPLETOS')} ), 400

    # Crea instancia del Gestor de la Colección
    gestor = GestorColeccion(config)
    resultado = gestor.cargar_imagen( archivo=archivo, aplicacion=aplicacion )

    if resultado:
        respuesta = config.MENSAJES.get('EXITO_IMAGEN_SUBIDA')
    else:
        respuesta = config.MENSAJES.get('ERROR_IMAGEN_NOSUBIDA')
    return jsonify( {'respuesta': respuesta} ), 200

######################################################
# URL: "/<coleccion>/cargar" (POST) [T]
# Recibe el archivo cargado por el usuario y lo guarda en la colección
@app.route( '/<coleccion>/cargar', methods=['POST'] )
def funcion_cargar( coleccion ):
    roles = ["Editor"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Comprueba si se ha seleccionado un archivo
    if 'archivo' not in request.files:
        return jsonify( {'error': config.MENSAJES.get('ERROR_DATOS_INCOMPLETOS')} ), 400

    # Valida datos de entrada y ruta
    ini_time = time.time()
    mensaje = ""
    archivo = request.files[ 'archivo' ]
    config.CARPETA = request.form.get( 'carpeta' )
    if not archivo or not config.CARPETA:
        return jsonify( {'error': config.MENSAJES.get('ERROR_DATOS_INCOMPLETOS')} ), 400

    gestor = GestorColeccion(config)
    subir = gestor.subir_archivo( archivo=archivo )
    if subir:
        resultado = subir.get('resultado')
        mensaje = f"{subir.get('mensaje')}. "
        nombre = subir.get('nombre')
        if resultado == 'ERROR':
            return jsonify( {'error': mensaje} ), 400
    else:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ARCHIVO_NOSUBIDO')} ), 400

    # Ingresa el archivo en BD
    id_doc = gestor.ingresar_documento( archivo = nombre )
    if id_doc > 0:
        mensaje = f"{mensaje}{config.MENSAJES.get('EXITO_ARCHIVO_INGRESADO')}. "

        # Indexa el archivo
        indexado = gestor.almacenar_documento( id_doc = id_doc )
        if indexado:
            mensaje = f"{mensaje}{config.MENSAJES.get('EXITO_ARCHIVO_INDEXADO')}. "
        else:
            mensaje = f"{mensaje}{config.MENSAJES.get('ERROR_ARCHIVO_NOINDEXADO')}. "
    else:
        mensaje = f"{mensaje}{config.MENSAJES.get('ERROR_ARCHIVO_NOINGRESADO')}. "
    
    tiempo = round( time.time() - ini_time, None )
    respuesta = f"{mensaje} Tiempo: {tiempo} segundos"
    return jsonify( {'respuesta': respuesta, 'id_doc': id_doc } ), 200

######################################################
# URL: "/<coleccion>/archivo/<int:uid>" (DELETE) [T]
# Borra un archivo de la BD y el disco
@app.route( '/<coleccion>/archivo/<int:uid>', methods=['DELETE'] )
def funcion_borrar_archivo( coleccion, uid ):
    roles = ["Admin","Editor"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Ejecuta la actualización de la BD con el uid
    gestor = GestorColeccion(config)
    resultado = gestor.borrar_documento( id_doc=uid )
 
    # Entrega el resultado
    if resultado:
        return jsonify( {'respuesta': f"{config.MENSAJES.get('EXITO_ARCHIVO_BORRADO')}"} ), 200
    else:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ARCHIVO_NOBORRADO')} ), 200

######################################################
# URL: "/<coleccion>/documento/<int:uid>" (GET) [T]
# Proporciona una interfaz HTML con un formulario para editar un documento
@app.route( '/<coleccion>/documento/<int:uid>', methods=['GET'] )
def interfaz_editar_documento( coleccion, uid ):
    roles = ["Editor"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Realiza la consulta con el uid
    gestor = GestorColeccion(config)
    resultados = gestor.abrir_documento( id_doc=uid )

    # Entrega la interfaz HTML
    return render_template( 'documento.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            diccionario = config.cargar_valores( 'diccionario.json' ),
            opciones_carpetas = config.cargar_valores( 'carpetas.json' ),
            datos_archivo = resultados
        )

######################################################
# URL: "/<coleccion>/archivo/<int:uid>" (POST) [T]
# Guarda los datos del archivo recibido del formulario en la BD
@app.route( '/<coleccion>/archivo/<int:uid>', methods=['POST'] )
def funcion_guardar_archivo( coleccion, uid ):
    roles = ["Admin","Editor"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    parametros = {}
    for campo in request.form:
        parametros[campo] = request.form[campo]

    # Ejecuta la actualización de la BD con el uid
    gestor = GestorColeccion(config)
    resultado = gestor.guardar_documento( id_doc=uid, parametros=parametros )
 
    # Entrega el resultado
    if resultado:
        return jsonify( {'respuesta': f"{config.MENSAJES.get('EXITO_ARCHIVO_GUARDADO')}"} ), 200
    else:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ARCHIVO_NOGUARDADO')} ), 200

######################################################
# URL: "/<coleccion>/carpetas/<carpeta>" (DELETE) [T]
# Borra una carpeta y su contenido
@app.route( '/<coleccion>/carpetas/<carpeta>', methods=['DELETE'] )
def funcion_borrar_carpeta( coleccion, carpeta ):
    roles = ["Admin","Editor"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    gestor = GestorColeccion(config)
    resultado = gestor.borrar_carpeta( nombre_carpeta=carpeta )
    
    # Entrega el resultado
    if resultado:
        return jsonify( {'respuesta': f"{config.MENSAJES.get('EXITO_CARPETA_BORRADA')}"} ), 200
    else:
        return jsonify( {'error': config.MENSAJES.get('ERROR_CARPETA_NOBORRADA')} ), 200

######################################################
# URL: "/<coleccion>/carpetas" (POST) [T]
# Crea una nueva carpeta
@app.route( '/<coleccion>/carpetas', methods=['POST'] )
def funcion_carpetas( coleccion ):
    roles = ["Admin","Editor"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Asigna los parámetros recibidos
    nombre_carpeta = obtener_parametro( 'carpeta' )
    etiqueta_carpeta = obtener_parametro( 'etiqueta' )
    tipos_archivo = obtener_parametro( 'tipos_archivo' )
    modulos = obtener_parametro( 'modulos' )

    # Crea instancia del Gestor de la Colección
    gestor = GestorColeccion(config)
    resultado = gestor.crear_carpeta( nombre_carpeta=nombre_carpeta, etiqueta_carpeta=etiqueta_carpeta, tipos_archivo=tipos_archivo, modulos=modulos )

    return jsonify( {'respuesta': resultado} ), 200

######################################################
# URL: "/<coleccion>/documentos" (POST) [T]
# Muestra la lista de documentos encontrados en una consulta
@app.route( '/<coleccion>/documentos', methods=['POST'] )
def funcion_documentos( coleccion ):
    roles = ["Editor","Usuario"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Lee y asigna los parámetros de la consulta
    parametros = {
        "tipo": obtener_parametro( 'tipo' ),
        "carpeta": obtener_parametro( 'carpeta' ),
        "texto": obtener_parametro( 'texto' ),
        "estado": obtener_parametro( 'estado' ),
        "max": obtener_parametro( 'max' ),
        "nav": obtener_parametro( 'nav' )
    }

    # Realiza la consulta con los parámetros
    gestor = GestorColeccion(config)
    resultados = gestor.consultar_documentos( parametros=parametros )
    paginas = []
    for pagina in range(int(resultados.get('paginas','1'))):
        paginas.append(pagina + 1)

    # Entrega la interfaz HTML
    return render_template( 'lista_documentos.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            diccionario = config.cargar_valores( 'diccionario.json' ),
            opciones_carpetas = config.cargar_valores( 'carpetas.json' ),
            lista_archivos = resultados,
            paginas = paginas
        )

######################################################
# URL: "/<coleccion>/archivos" (POST) [T]
# Muestra la lista de archivos encontrados en una consulta
@app.route( '/<coleccion>/archivos', methods=['POST'] )
def funcion_archivos( coleccion ):
    roles = ["Admin"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Lee y asigna los parámetros de la consulta
    parametros = {
        "tipo": obtener_parametro( 'tipo' ),
        "carpeta": obtener_parametro( 'carpeta' ),
        "texto": obtener_parametro( 'texto' ),
        "estado": obtener_parametro( 'estado' ),
        "max": obtener_parametro( 'max' ),
        "nav": obtener_parametro( 'nav' )
    }

    # Realiza la consulta con los parámetros
    gestor = GestorColeccion(config)
    resultados = gestor.consultar_documentos( parametros=parametros )
    paginas = []
    for pagina in range(int(resultados.get('paginas','1'))):
        paginas.append(pagina + 1)

    # Entrega la interfaz HTML
    return render_template( 'lista_archivos.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            diccionario = config.cargar_valores( 'diccionario.json' ),
            opciones_carpetas = config.cargar_valores( 'carpetas.json' ),
            lista_archivos = resultados,
            paginas = paginas
        )

######################################################
# URL: "/<coleccion>/metadatos/<int:uid>" (GET) [T]
# Proporciona una interfaz HTML con un formulario para editar metadatos
@app.route( '/<coleccion>/metadatos/<int:uid>', methods=['GET'] )
def interfaz_metadatos( coleccion, uid ):
    roles = ["Admin","Editor"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Realiza la consulta con el uid
    gestor = GestorColeccion(config)
    resultados = gestor.abrir_documento( id_doc=uid )

    # Entrega la interfaz HTML
    return render_template( 'metadatos.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            diccionario = config.cargar_valores( 'diccionario.json' ),
            opciones_carpetas = config.cargar_valores( 'carpetas.json' ),
            datos_archivo = resultados
        )

######################################################
# URL: "/<coleccion>/metadatos/<int:uid>" (POST) [T]
# Genera los metadatos solicitados del documento y los guarda en la BD
@app.route( '/<coleccion>/metadatos/<int:uid>', methods=['POST'] )
def funcion_metadatos( coleccion, uid ):
    roles = ["Admin","Editor"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Recibe y comprueba los parámetros
    parametros = []
    for campo in request.form:
        parametros.append( request.form[campo] )
    if not parametros:
        return jsonify( {'error': config.MENSAJES.get('ERROR_DATOS_INCOMPLETOS')} ), 400

    # Ejecuta la actualización de la BD con el uid
    gestor = GestorColeccion(config)
    resultado = gestor.catalogar_documento( id_doc=uid, campos=parametros )
 
    # Entrega el resultado
    if resultado:
        return jsonify( {'respuesta': f"{config.MENSAJES.get('EXITO_METADATOS_GENERADOS')}"} ), 200
    else:
        return jsonify( {'error': config.MENSAJES.get('ERROR_METADATOS_NOGENERADOS')} ), 200

######################################################
# URL: "/<coleccion>/asistente" (GET) [T]
# Proporciona una interfaz HTML para el asistente de documentos
@app.route( '/<coleccion>/asistente', methods=['GET'] )
def interfaz_asistente( coleccion ):
    roles = ["Editor","Usuario"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    gestor = GestorColeccion(config)
    carpetas = gestor.obtener_carpetas()
    documentos = gestor.obtener_documentos()

    # Entrega la interfaz HTML
    return render_template( 'asistente.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            menu = traspasar_menu( 'asistente', config ),
            diccionario = config.cargar_valores( 'diccionario.json' ),
            opciones_carpetas = config.cargar_valores( 'carpetas.json' ),
            lista_carpetas = carpetas,
            lista_documentos = documentos
        )

######################################################
# URL: "/<coleccion>/chatdoc" (GET) [T]
# Proporciona una interfaz HTML con un cliente de chat para interactuar
@app.route( '/<coleccion>/chatdoc', methods=['GET'] )
def interfaz_chatdoc( coleccion ):
    roles = ["Editor","Usuario"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    config.CARPETA = obtener_parametro( 'carpeta' )
    doc = obtener_parametro( 'doc' )
    if not doc:
        doc = 0
    preguntas = {}
    historial = []
    gestor = GestorColeccion(config)
    documento = gestor.abrir_documento( id_doc=doc )
    if documento:
        sugerencias = documento.get('sugerencias', None)
        if sugerencias:
            preguntas = str(sugerencias).split(" | ")
    else:
        documento = {}
    historial = gestor.obtener_interacciones( id_doc=doc )

    # Entrega la interfaz HTML
    return render_template( 'chatdoc.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            diccionario = config.cargar_valores( 'diccionario.json' ),
            opciones_carpetas = config.cargar_valores( 'carpetas.json' ),
            carpeta = config.CARPETA,
            doc = doc,
            documento = documento,
            preguntas = preguntas,
            historial = historial
        )

######################################################
# URL: "/<coleccion>/chatdoc" (POST) [T]
# Recibe una consulta desde un chat y devuelve la respuesta en formato JSON
@app.route( '/<coleccion>/chatdoc', methods=['POST'] )
def funcion_chatdoc( coleccion ):
    roles = ["Editor","Usuario"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Validadores de la petición del usuario
    peticion = request.args.get( "mensaje" )
    if not peticion:
        data = request.get_json()
        if data and "mensaje" in data:
            peticion = data.get( "mensaje" )
    if not peticion:
        return jsonify( {'respuesta': config.MENSAJES.get('CHAT_PREGUNTA_VACIA'), 'peticion': peticion} ), 200
    if len( peticion ) < 4:
        return jsonify( {'respuesta': config.MENSAJES.get('CHAT_PREGUNTA_MUYCORTA'), 'peticion': peticion} ), 200
    if len( peticion ) > 5000:
        return jsonify( {'respuesta': config.MENSAJES.get('CHAT_PREGUNTA_MUYLARGA'), 'peticion': peticion} ), 200

    # Recupera datos
    usuario = config.USUARIO.get('email')
    carpeta = obtener_parametro( 'carpeta' )
    doc = obtener_parametro( 'doc' )
    if not doc:
        doc = 0
    if not usuario or not carpeta:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Crea instancia del Gestor de la Colección con la carpeta seleccionada
    id_sesion = f"{usuario}-{doc}"
    config.CARPETA = carpeta
    gestor = GestorColeccion(config)
    try:
        # Envía la solicitud al LLM y recibe la respuesta
        ini_time = time.time()
        
        if not gestor.abrir_ejecutor( id_doc=doc ):
            return jsonify( {'error': config.MENSAJES.get('ERROR_INDICE_NOEXISTE'), "codigo": "10"} ), 400

        respuesta = gestor.ejecutar_instruccion( peticion=peticion, id_sesion=id_sesion )
        respuesta = str( respuesta ).strip()
        tiempo = round( time.time() - ini_time, None )

        # Procesa la respuesta y devuelve el resultado
        resultado = gestor.procesar_respuesta(
            respuesta= respuesta,
            peticion = peticion,
            coleccion = f"{id_sesion}-{config.CARPETA}",
            tiempo = tiempo
        )
        respuesta = resultado.get("respuesta", "")
        uid = int(resultado.get("uid", 0))

    # Si se produce un error
    except Exception as e:
        return jsonify( {'error': config.MENSAJES.get('ERROR_GENERAL')} ), 500
    # Si no se recibe respuesta
    if not respuesta:
        return jsonify( {'respuesta': config.MENSAJES.get('CHAT_RESPUESTA_NOSE'), 'peticion': peticion} ), 200
    
    # Si todo está bien, devuelve el resultado en formato JSON
    return jsonify({
            'respuesta': respuesta, 
            'peticion': peticion, 
            'id': uid,
            'tiempo': tiempo
        }), 200

######################################################
# URL: "/<coleccion>/chatdoc/<carpeta>" (GET) [T]
# Exporta el historial de consultas de un asistente
@app.route( '/<coleccion>/chatdoc/<carpeta>', methods=['GET'] )
def interfaz_chatdoc_carpeta( coleccion, carpeta ):
    roles = ["Editor","Usuario"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    config.CARPETA = carpeta
    doc = obtener_parametro( 'doc' )
    if not doc:
        doc = 0
    gestor = GestorColeccion(config)
    historial = gestor.obtener_interacciones( id_doc=doc )
    documento = gestor.abrir_documento( id_doc=doc )
    html = render_template( 'chatdoc.txt', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            opciones_carpetas = config.cargar_valores( 'carpetas.json' ),
            carpeta = config.CARPETA,
            doc = doc,
            documento = documento,
            historial = historial
        )
    response = make_response( html )
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    response.headers['Content-Disposition'] = f"attachment; filename=chatexperto_{coleccion}_{config.CARPETA}-{doc}.txt"
    return response

######################################################
# URL: "/<coleccion>/chatdoc/<carpeta>" (POST) [T]
# Borra el historial de consultas de un asistente
@app.route( '/<coleccion>/chatdoc/<carpeta>', methods=['POST'] )
def funcion_chatdoc_carpeta( coleccion, carpeta ):
    roles = ["Editor","Usuario"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    config.CARPETA = carpeta
    doc = obtener_parametro( 'doc' )
    if not doc:
        doc = 0
    gestor = GestorColeccion(config)
    resultado = gestor.vaciar_interacciones( id_doc=doc )
    if resultado:
        return jsonify( {'respuesta': config.MENSAJES.get('EXITO_INTERACCIONES_BORRADAS')} ), 200
    else:
        return jsonify( {'respuesta': config.MENSAJES.get('ERROR_INTERACCIONES_NOBORRADAS')} ), 200

######################################################
# URL: "/<coleccion>/biblioteca" (POST) [T]
# Muestra la lista de documentos encontrados en la biblioteca
@app.route( '/<coleccion>/biblioteca', methods=['POST'] )
def funcion_biblioteca( coleccion ):
    roles = ["Editor","Usuario"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Lee y asigna los parámetros de la consulta
    config.CARPETA = obtener_parametro( 'carpeta' )
    parametros = {}
    for campo in request.form:
        parametros[campo] = request.form[campo]

    gestor = GestorColeccion(config)
    datos = gestor.buscar_textos_documentos( parametros=parametros )

    # Entrega la interfaz HTML
    return render_template( 'lista_biblioteca.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            diccionario = config.cargar_valores( 'diccionario.json' ),
            opciones_carpetas = config.cargar_valores( 'carpetas.json' ),
            datos = datos
        )

######################################################
# URL: "/<coleccion>/biblioteca" (PUT) [T]
# Recibe una expresión de búsqueda y devuelve la respuesta en formato JSON
@app.route( '/<coleccion>/biblioteca', methods=['PUT'] )
def funcion_consultar_busqueda( coleccion ):
    roles = ["Editor","Usuario"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Validadores de la petición del usuario
    buscar = request.args.get( "buscar" )
    if not buscar:
        data = request.get_json()
        if data and "buscar" in data:
            buscar = data.get( "buscar" )
    if not buscar:
        return jsonify( {'respuesta': config.MENSAJES.get('CHAT_PREGUNTA_VACIA'), 'peticion': buscar} ), 200
    if len( buscar ) < 4:
        return jsonify( {'respuesta': config.MENSAJES.get('CHAT_PREGUNTA_MUYCORTA'), 'peticion': buscar} ), 200
    if len( buscar ) > 200:
        return jsonify( {'respuesta': config.MENSAJES.get('CHAT_PREGUNTA_MUYLARGA'), 'peticion': buscar} ), 200

    # Crea instancia del Gestor de la Colección con la carpeta seleccionada
    config.CARPETA = obtener_parametro( 'carpeta' )
    gestor = GestorColeccion(config)
    try:
        # Envía la solicitud al LLM y recibe la respuesta
        resultado = gestor.consultar_busqueda( texto=buscar )
        respuesta = resultado["result"]

    except Exception as e:
        return jsonify( {'error': config.MENSAJES.get('ERROR_GENERAL')} ), 500
    if not respuesta:
        return jsonify( {'respuesta': config.MENSAJES.get('CHAT_RESPUESTA_NOSE'), 'peticion': buscar} ), 200
    
    # Si todo está bien, devuelve el resultado en formato JSON
    return jsonify({
            'respuesta': respuesta, 
        }), 200

######################################################
# URL: "/<coleccion>/importar" (GET) [T]
# Proporciona una interfaz HTML con un formulario para importar un archivo Excel
@app.route( '/<coleccion>/importar', methods=['GET'] )
def interfaz_importar( coleccion ):
    roles = ["Editor"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    carpeta = obtener_parametro( 'carpeta' )
    config.CARPETA = carpeta

    # Entrega la interfaz HTML
    return render_template( 'importar.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            menu = traspasar_menu( 'importar', config ),
            carpeta = carpeta
        )

######################################################
# URL: "/<coleccion>/importar" (POST) [T]
# Recibe archivo Excel subido por el usuario y actualiza metadatos de documentos
@app.route( '/<coleccion>/importar', methods=['POST'] )
def funcion_importar( coleccion ):
    roles = ["Editor"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Comprueba si se ha enviado un archivo
    if 'archivo' not in request.files:
        return jsonify( {'error': config.MENSAJES.get('ERROR_DATOS_INCOMPLETOS')} ), 400
    archivo = request.files[ 'archivo' ]
    if not archivo:
        return jsonify( {'error': config.MENSAJES.get('ERROR_DATOS_INCOMPLETOS')} ), 400

    config.CARPETA = obtener_parametro( 'carpeta' )
    nombre = f"metadatos-{config.CARPETA}.xlsx"
    gestor = GestorColeccion(config)
    resultado = gestor.importar_metadatos( archivo=archivo, nombre=nombre )

    if resultado:
        respuesta = config.MENSAJES.get('EXITO_METADATOS_IMPORTADOS')
    else:
        respuesta = config.MENSAJES.get('ERROR_METADATOS_NOIMPORTADOS')
    return jsonify( {'respuesta': respuesta} ), 200

######################################################
# URL: "/<coleccion>/exportar/<carpeta>" (GET) [T]
# Exporta metadatos de documentos de una carpeta en un archivo Excel y lo descarga
@app.route( '/<coleccion>/exportar/<carpeta>', methods=['GET'] )
def funcion_exportar( coleccion, carpeta ):
    from flask import send_from_directory
    roles = ["Admin","Editor"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401
    
    config.CARPETA = carpeta
    nombre = f"metadatos-{carpeta}.xlsx"
    gestor = GestorColeccion(config)
    ruta_archivo = gestor.exportar_metadatos( nombre=nombre )
    if not ruta_archivo:
        return jsonify( {'error': config.MENSAJES.get('ERROR_METADATOS_NOEXPORTADOS')} ), 500

    return send_from_directory( ruta_archivo, nombre )

######################################################
# URL: "/<coleccion>/indexar" (POST) [T]
# Actualiza el índice vectorial de un documento identificado por id
@app.route( '/<coleccion>/indexar', methods=['POST'] )
def funcion_indexar( coleccion ):
    roles = ["Admin", "Editor"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    doc = obtener_parametro( 'doc' )
    carpeta = obtener_parametro( 'carpeta' )
    if carpeta and doc:
        config.CARPETA = carpeta
        gestor = GestorColeccion(config)
        indexado = gestor.almacenar_documento( id_doc = doc )
        if indexado:
            mensaje = config.MENSAJES.get('EXITO_ARCHIVO_INDEXADO')
        else:
            mensaje = config.MENSAJES.get('ERROR_ARCHIVO_NOINDEXADO')
        return jsonify( {'respuesta': mensaje} ), 200
    else:
        return jsonify( {'error': config.MENSAJES.get('ERROR_DATOS_INCOMPLETOS')} ), 400

######################################################
# URL: "/<coleccion>/mibiblioteca" (GET) [K]
# Devuelve la lista de documentos encontrados en la biblioteca en formato HTML
@app.route( '/<coleccion>/mibiblioteca', methods=['GET'] )
@cross_origin()
def interfaz_mibiblioteca( coleccion ):
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=True, config=config ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Lee y asigna los parámetros de la consulta
    config.CARPETA = obtener_parametro( 'carpeta' )
    parametros = {}
    for campo in request.args:
        parametros[campo] = request.args[campo]

    gestor = GestorColeccion(config)
    datos = gestor.buscar_textos_documentos( parametros=parametros )

    # Entrega la interfaz HTML
    return render_template( 'mibiblioteca.html', app=config.APP, dir_base=request.script_root, 
            diccionario = config.cargar_valores( 'diccionario.json' ),
            opciones_carpetas = config.cargar_valores( 'carpetas.json' ),
            datos = datos
        )

######################################################
# URL: "/<coleccion>/mibiblioteca" (POST) [K]
# Devuelve la lista de documentos encontrados en la biblioteca en formato JSON
@app.route( '/<coleccion>/mibiblioteca', methods=['POST'] )
@cross_origin()
def funcion_mibiblioteca( coleccion ):
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=True, config=config ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Lee y asigna los parámetros de la consulta
    config.CARPETA = obtener_parametro( 'carpeta' )
    parametros = {}
    for campo in request.form:
        parametros[campo] = request.form[campo]

    gestor = GestorColeccion(config)
    datos = gestor.buscar_textos_documentos( parametros=parametros )
    if datos:
        return jsonify( {'resultados': datos} ), 200
    else:
        return jsonify( {'error': config.MENSAJES.get('ERROR_GENERAL')} ), 500

######################################################
# URL: "/<coleccion>/destacados" (GET) [T]
# Muestra una interfaz HTML con listas de documentos destacados
@app.route( '/<coleccion>/destacados', methods=['GET'] )
def interfaz_destacados( coleccion ):
    roles = ["Editor","Usuario"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    gestor = GestorColeccion(config)
    resultados = gestor.consultar_destacados( total=5, modulo='biblioteca' )

    # Entrega la interfaz HTML
    return render_template( 'destacados.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            lista_archivos = resultados
        )

######################################################
# URL: "/<coleccion>/misdestacados" (GET) [K]
# Muestra una interfaz HTML con listas de documentos destacados
@app.route( '/<coleccion>/misdestacados', methods=['GET'] )
@cross_origin()
def interfaz_misdestacados( coleccion ):
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=True, config=config ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    numero = obtener_parametro( 'numero' )
    gestor = GestorColeccion(config)
    resultados = gestor.consultar_destacados( total=numero, modulo='biblioteca' )

    # Entrega la interfaz HTML
    return render_template( 'misdestacados.html', app=config.APP, dir_base=request.script_root, 
            lista_archivos = resultados
        )

######################################################
# URL: "/<coleccion>/prompts" (GET) [T]
# Proporciona una interfaz HTML con un formulario para construir un prompt para GPT
@app.route( '/<coleccion>/prompts', methods=['GET'] )
def interfaz_prompts( coleccion ):
    roles = ["Editor","Usuario"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    historial = []
    config.CARPETA = "chatgpt"
    gestor = GestorColeccion(config)
    historial = gestor.obtener_interacciones( id_doc=0 )
    datos = gestor.consultar_prompts()

    # Entrega la interfaz HTML
    return render_template( 'prompts.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            diccionario = config.cargar_valores( 'prompts.json' ),
            historial = historial,
            datos = datos
        )

######################################################
# URL: "/<coleccion>/prompts" (POST) [T]
# Recibe una pregunta para enviar a GPT y devuelve la respuesta recibida en formato JSON
@app.route( '/<coleccion>/prompts', methods=['POST'] )
def funcion_prompts( coleccion ):
    import re
    roles = ["Editor","Usuario"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    mensaje = obtener_parametro( 'mensaje' )
    if not mensaje:
        return jsonify( {'respuesta': config.MENSAJES.get('CHAT_PREGUNTA_VACIA'), 'peticion': mensaje} ), 200
    if len( mensaje ) < 20:
        return jsonify( {'respuesta': config.MENSAJES.get('CHAT_PREGUNTA_MUYCORTA'), 'peticion': mensaje} ), 200
    if len( mensaje ) > 10000:
        return jsonify( {'respuesta': config.MENSAJES.get('CHAT_PREGUNTA_MUYLARGA'), 'peticion': mensaje} ), 200

    # Recupera parametros
    parametros = {
        "llm": obtener_parametro( 'modelo' ),
        "max_tokens": obtener_parametro( 'longitud' ),
        "temperature": obtener_parametro( 'expresion' ),
        "num_docs": '0'
    }

    # Crea instancia del Gestor de la Colección con la carpeta seleccionada
    config.CARPETA = "chatgpt"
    gestor = GestorColeccion(config)
    gestor.configurar_ejecutor( parametros=parametros )
    try:
        # Envía la solicitud a OpenAI y recibe la respuesta
        ini_time = time.time()
        gestor.CFG['clase_interaccion'] = "Peticion"
        gestor.abrir_ejecutor()
        respuesta = gestor.ejecutar_instruccion( peticion=mensaje, id_sesion=f"{config.USUARIO.get('email')}-0" )
        if not respuesta:
            return jsonify( {'error': config.MENSAJES.get('ERROR_RESPUESTA_LLM')} ), 500
        
        respuesta = str( respuesta ).strip()
        tiempo = round( time.time() - ini_time, None )
        #if '"""' in mensaje:
        #    mensaje = mensaje[:mensaje.index('"""')]
        mensaje = re.sub(r'\n', ' ', mensaje)
        resultado = gestor.procesar_respuesta(
            respuesta = respuesta,
            peticion = mensaje,
            coleccion = f"{config.USUARIO.get('email')}-0-{config.CARPETA}",
            tiempo = tiempo
        )
        respuesta = resultado.get("respuesta", "")
        uid = int(resultado.get("uid", 0))

    # Si se produce un error
    except Exception as e:
        return jsonify( {'error': config.MENSAJES.get('ERROR_GENERAL')} ), 500
    # Si no se recibe respuesta
    if not respuesta:
        return jsonify( {'respuesta': config.MENSAJES.get('CHAT_RESPUESTA_NOSE'), 'peticion': mensaje} ), 200
    
    # Si todo está bien, devuelve el resultado en formato JSON
    return jsonify({
            'respuesta': respuesta, 
            'peticion': mensaje, 
            'id': uid,
            'tiempo': tiempo
        }), 200

######################################################
# URL: "/<coleccion>/prompts" (DELETE) [T]
# Borra el historial de conversación del usuario con chatGPT
@app.route( '/<coleccion>/prompts', methods=['DELETE'] )
def funcion_vaciar( coleccion ):
    roles = ["Editor","Usuario"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    config.CARPETA = "chatgpt"
    gestor = GestorColeccion(config)
    resultado = gestor.vaciar_interacciones( id_doc=0 )
    if resultado:
        return jsonify( {'respuesta': config.MENSAJES.get('EXITO_INTERACCIONES_BORRADAS')} ), 200
    else:
        return jsonify( {'respuesta': config.MENSAJES.get('ERROR_INTERACCIONES_NOBORRADAS')} ), 200

######################################################
# URL: "/<coleccion>/guardarchat" (GET) [T]
# Exporta el historial de conversación del usuario con chatGPT
@app.route( '/<coleccion>/guardarchat', methods=['GET'] )
def interfaz_guardarchat( coleccion ):
    roles = ["Editor","Usuario"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    historial = []
    config.CARPETA = "chatgpt"
    gestor = GestorColeccion(config)
    historial = gestor.obtener_interacciones( id_doc=0 )
    html = render_template( 'chatgpt.txt', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            historial = historial
        )
    response = make_response( html )
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    response.headers['Content-Disposition'] = f"attachment; filename=chatgpt_{config.APP.get('ahora')}.txt"
    return response

######################################################
# URL: "/<coleccion>/plantillas" (GET) [T]
# Muestra una lista HTML con las plantillas de prompts almacenadas en la BD
@app.route( '/<coleccion>/plantillas', methods=['GET'] )
def interfaz_consultar_plantillas( coleccion ):
    roles = ["Editor"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Lee y asigna los parámetros de la consulta
    visible = obtener_parametro( 'visible' )
    tarea = obtener_parametro( 'tarea' )
    parametros = {
        "visible": visible,
        "tarea": tarea
    }

    gestor = GestorColeccion(config)
    datos = gestor.consultar_plantillas( parametros=parametros )
    tareas = gestor.consultar_tareas()

    # Entrega la interfaz HTML
    return render_template( 'plantillas.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            diccionario = config.cargar_valores( 'prompts.json' ),
            pla_visible = visible,
            pla_tarea = tarea,
            tareas = tareas,
            datos = datos
        )

######################################################
# URL: "/<coleccion>/plantillas" (POST) [T]
# Proporciona una interfaz HTML con un formulario para agregar una plantilla de prompt
@app.route( '/<coleccion>/plantillas', methods=['POST'] )
def interfaz_nueva_plantilla( coleccion ):
    roles = ["Editor"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    gestor = GestorColeccion(config)
    tareas = gestor.consultar_tareas()

    # Entrega la interfaz HTML
    return render_template( 'plantilla.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            diccionario = config.cargar_valores( 'prompts.json' ),
            datos = [],
            tareas = tareas,
            modo = "nueva"
        )

######################################################
# URL: "/<coleccion>/plantilla/<int:uid>" (GET)
# Proporciona una interfaz HTML con un formulario para editar una plantilla de prompt
@app.route( '/<coleccion>/plantilla/<int:uid>', methods=['GET'] )
def interfaz_abrir_plantilla( coleccion, uid ):
    roles = ["Editor"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    gestor = GestorColeccion(config)
    datos = gestor.abrir_plantilla( uid=uid )
    tareas = gestor.consultar_tareas()

    # Entrega la interfaz HTML
    return render_template( 'plantilla.html', app=config.APP, dir_base=request.script_root, usuario=config.USUARIO, 
            diccionario = config.cargar_valores( 'prompts.json' ),
            datos = datos,
            tareas = tareas,
            modo = "editar"
        )

######################################################
# URL: "/<coleccion>/plantilla/<int:uid>" (DELETE)
# Borra una plantilla de prompt de la BD
@app.route( '/<coleccion>/plantilla/<int:uid>', methods=['DELETE'] )
def funcion_borrar_plantilla( coleccion, uid ):
    roles = ["Editor"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    # Ejecuta la actualización de la BD con el uid
    gestor = GestorColeccion(config)
    resultado = gestor.borrar_plantilla( uid=uid )
 
    # Entrega el resultado
    if resultado:
        return jsonify( {'respuesta': f"{config.MENSAJES.get('EXITO_ACCION_REALIZADA')}"} ), 200
    else:
        return jsonify( {'error': config.MENSAJES.get('ERROR_GENERAL')} ), 500

######################################################
# URL: "/<coleccion>/plantilla" (POST)
# Guarda una nueva plantilla de prompt en la BD
@app.route( '/<coleccion>/plantilla', methods=['POST'] )
def funcion_ingresar_plantilla( coleccion ):
    roles = ["Editor"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    parametros = {}
    for campo in request.form:
        parametros[campo] = request.form[campo]

    # Ejecuta la actualización de la BD con el uid
    gestor = GestorColeccion(config)
    resultado = gestor.ingresar_plantilla( parametros=parametros )
 
    # Entrega el resultado
    if resultado:
        return jsonify( {'respuesta': f"{config.MENSAJES.get('EXITO_ACCION_REALIZADA')}"} ), 200
    else:
        return jsonify( {'error': config.MENSAJES.get('ERROR_GENERAL')} ), 500

######################################################
# URL: "/<coleccion>/plantilla/<int:uid>" (PUT)
# Actualiza la plantilla de prompt en la BD
@app.route( '/<coleccion>/plantilla/<int:uid>', methods=['PUT'] )
def funcion_actualizar_plantilla( coleccion, uid ):
    roles = ["Editor"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return redirect( f"{request.script_root}/{coleccion}/login" )

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    parametros = {}
    for campo in request.form:
        parametros[campo] = request.form[campo]

    # Ejecuta la actualización de la BD con el uid
    gestor = GestorColeccion(config)
    resultado = gestor.actualizar_plantilla( uid=uid, parametros=parametros )
 
    # Entrega el resultado
    if resultado:
        return jsonify( {'respuesta': f"{config.MENSAJES.get('EXITO_ACCION_REALIZADA')}"} ), 200
    else:
        return jsonify( {'error': config.MENSAJES.get('ERROR_GENERAL')} ), 500

######################################################
# URL: "/<coleccion>/audio" (POST) [T]
# Recibe el audio cargado por el usuario y lo procesa
@app.route( '/<coleccion>/audio', methods=['POST'] )
def funcion_audio( coleccion ):
    roles = ["Editor"]
    config = Config(coleccion)

    # Comprueba la colección
    if not config.comprobar_coleccion( coleccion ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_COLECCION_NOEXISTE')} ), 404

    # Valida sesión del usuario para autorizar
    if not comprobar_sesion( app_key=False, config=config ):
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    if not config.USUARIO.get('roles') in roles:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ACCESO_DENEGADO')} ), 401

    if 'audio' not in request.files:
        return jsonify( {'error': config.MENSAJES.get('ERROR_DATOS_INCOMPLETOS')} ), 400

    mensaje = ''
    gestor = GestorColeccion(config)
    audio = request.files[ 'audio' ]
    subir = gestor.subir_audio( archivo=audio )
    if subir:
        resultado = subir.get('resultado')
        mensaje = f"{subir.get('mensaje')}. "
        if resultado == 'ERROR':
            return jsonify( {'error': mensaje} ), 400
    else:
        return jsonify( {'error': config.MENSAJES.get('ERROR_ARCHIVO_NOSUBIDO')} ), 400

    return jsonify( {'respuesta': mensaje} ), 200


######################################################
# 3. FUNCIONES AUXILIARES PARA CONTROL
######################################################

# Función para obtener parámetro de la petición HTTP
def obtener_parametro( nombre='' ):
    valor = ''
    try:
        if request.method in ['POST', 'PUT']:
            if request.form:
                valor = request.form.get( nombre )
            else:
                data = request.get_json()
                if data:
                    if nombre in data:
                        valor = data.get( nombre )
        else:
            valor = request.args.get( nombre )
    except Exception as e:
        return ''
    if not valor:
        valor = ''
    return valor

# Función para validar la APP Key en las peticiones recibidas
def validar_app_key( request, config=None ):
    if config:
        x_app_key = request.headers.get( "x-app-key" )
        config.APP["app_id"] = request.headers.get( "app" )
        return all( v and v != 'None' for v in [ x_app_key, config.APP.get('app_id') ] ) and x_app_key in config.APP.get('app_keys')
    return False

# Función para comprobar sesión del usuario
def comprobar_sesion( app_key=True, config=None ):
    from usuarios import Usuarios
    usuario = Usuarios(config)
    token = request.cookies.get( "token", "" )
    x_app_key = request.headers.get( "x-app-key", "" )
    aux = request.headers.get( "app", "" )
    if aux and config:
        config.APP["app_id"] = aux
    if app_key and config:
        if x_app_key:
            if not validar_app_key( request, config ):
                return False
        elif token:
            if not usuario.recuperar_sesion( token=token ):
                return False
        else:
            return False
    else:
        if not ( token and usuario.recuperar_sesion( token=token ) ):
            return False
    return True

# Función para extraer un menú para traspasarlo a una plantilla
def traspasar_menu( uid, config ):
    menus = config.cargar_valores( 'menus.json' )
    for menu in menus:
        if menu["_uid"] == uid:
            return menu
    return None



######################################################
# 4. EJECUTOR DE LA APP (USAR SOLO EN SERVIDOR LOCAL)
######################################################
if __name__ == '__main__':
    app.run()
######################################################
