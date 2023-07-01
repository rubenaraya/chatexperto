# gestor.py
import json
from basedatos import BaseDatos
from almacenes import Almacenes
from modelos import Modelos
from registros import configurar_logger

class GestorColeccion:

    def __init__( self, config=None ):
        
        # Manejador de registros
        self.gestor_registrar = configurar_logger( "gestor", "gestor.log" )
        self.config = config

        # Configuración del gestor
        self.CFG = self._cargar_configuracion()

        # Componentes (objetos)
        self.MODELO = Modelos(
            config = self.config,
            emb = self.CFG.get('api_emb'),
            llm = self.CFG.get('api_llm')
        )
        self.ALMACEN = Almacenes(
            config = self.config,
            almacen_indice = self.CFG.get('almacen_indice')
        )
        self.EJECUTOR = None

        # Diccionario
        self.ESTADO_DOC = {
            "NUEVO": 0,
            "INGRESADO": 1,
            "INDEXADO": 2,
            "CATALOGADO": 3
        }

        # Propiedades
        self.API_TIMEOUT = 15
        self.config.TIPOS_ARCHIVO = self.CFG.get('tipos_archivo', '')

######################################################
# FUNCIONES PUBLICAS PARA ALMACENES DE VECTORES
######################################################

    # Función para crear un índice vectorial con todos los documentos de una carpeta en una colección
    def almacenar_directorio( self, metodo ):
        try:
            # METODO: CREAR
            if metodo == "crear":
                # Cargar documentos y extraer textos
                documentos = self.ALMACEN.cargar_documentos(
                    metodo = self.CFG.get('cargar_documentos')
                )
                if not documentos:
                    self.gestor_registrar.error( f"{self.config.MENSAJES.get('ERROR_BC_NOACTUALIZADA')}: {self.config.CARPETA}" )
                    return False

                # Procesar metadatos y/o contenido
                documentos = self.ALMACEN.procesar_documentos(
                    documentos = documentos,
                    metodo = self.CFG.get('procesar_documentos'),
                    que_procesar = self.CFG.get('que_procesar')
                )

                # Dividir en trozos
                textos_extraidos = self.ALMACEN.dividir_documentos(
                    documentos = documentos,
                    metodo = self.CFG.get('dividir_documentos'),
                    trozo = self.CFG.get('trozo')
                )

                # Definir parámetros para crear incrustaciones (embeddings)
                self.MODELO.configurar_api_emb([
                    ("chunk_size", self.CFG.get('trozo'))
                ])

                # Crear índice vectorial y almacenar
                resultado = self.ALMACEN.crear_indice(
                    documentos = textos_extraidos,
                    api_emb = self.MODELO.api_emb()
                )

                if resultado:
                    return True
                else:
                    self.gestor_registrar.error( f"{self.config.MENSAJES.get('ERROR_INDICE_NOCREADO')}: {self.config.CARPETA}" )

        except Exception as e:
            self.gestor_registrar.error( f"{e}" )

        return False

    # Función para almacenar documento en índice vectorial
    def almacenar_documento( self, id_doc ):
        try:
            # Obtener datos del documento de la BD
            bd = BaseDatos(self.config)
            datos_doc = bd.seleccionar_documento( id_doc=id_doc )
            if datos_doc:
                archivo_nombre = datos_doc.get('archivo')
                archivo_extension = datos_doc.get('tipo')
                archivo = f"{archivo_nombre}.{archivo_extension}"
            else:
                self.gestor_registrar.error( f"{self.config.MENSAJES.get('ERROR_ARCHIVO_NOENCONTRADO')}: {self.config.CARPETA} / {archivo}" )
                return False

            # Cargar documento y extraer textos
            documentos = self.ALMACEN.cargar_documentos(
                metodo = self.CFG.get('cargar_documentos'),
                archivo = archivo
            )
            if not documentos:
                self.gestor_registrar.error( f"{self.config.MENSAJES.get('ERROR_ARCHIVO_NOINDEXABLE')}: {self.config.CARPETA} / {archivo}" )
                return False

            # Procesar contenido y/o metadatos del documento
            documentos = self.ALMACEN.procesar_documentos(
                documentos = documentos,
                metodo = self.CFG.get('procesar_documentos'),
                que_procesar = self.CFG.get('que_procesar')
            )

            # Dividir documento en trozos
            textos_extraidos = self.ALMACEN.dividir_documentos(
                documentos = documentos,
                metodo = self.CFG.get('dividir_documentos'),
                trozo = self.CFG.get('trozo')
            )

            # Definir parámetros para crear incrustaciones (embeddings)
            self.MODELO.configurar_api_emb([
                ("chunk_size", self.CFG.get('trozo'))
            ])

            # Crear índice vectorial y almacenar
            resultado = self.ALMACEN.crear_indice(
                documentos = textos_extraidos,
                api_emb = self.MODELO.api_emb(),
                id_doc = id_doc
            )

            # Actualizar estado del documento en la BD
            if resultado:
                actualizar = bd.actualizar_documento( id_doc=id_doc, estado=self.ESTADO_DOC.get('INDEXADO'), parametros=[] )
                if actualizar:
                    return True
                else:
                    self.gestor_registrar.error( f"{self.config.MENSAJES.get('ERROR_ARCHIVO_NOACTUALIZADO')}: {self.config.CARPETA} / {archivo}" )

        except Exception as e:
            self.gestor_registrar.error( f"{self.config.MENSAJES.get('ERROR_ARCHIVO_NOINDEXADO')}: {self.config.CARPETA} / {archivo}: {e}" )

        return False

    # Función para cargar configuracion de LLM
    def asignar_llm( self, llm ):
        try:
            if llm:
                self.MODELO.LLM = self.MODELO.cargar_configuracion( id_modelo = llm )
                self.CFG['api_llm'] = llm
                if llm in [ "OpenAI_GPT-3.5", "OpenAI_GPT-3.5-16k", "OpenAI_GPT-4" ]:
                    self.CFG['clase_interaccion'] = "Conversacion"
                elif llm in [ "OpenAI_GPT-3" ]:
                    self.CFG['clase_interaccion'] = "Consulta"
                return True
        except Exception as e:
            self.gestor_registrar.error( f"{e}" )

        return False

######################################################
# FUNCIONES PUBLICAS PARA INSTRUCCIONES Y RESPUESTAS
######################################################

    # Función para configurar ejecutor
    def configurar_ejecutor( self, parametros ):
        asignado = False
        if parametros:
            try:
                llm = parametros.get('llm', None)
                num_docs = parametros.get('num_docs', None)
                chain_type = parametros.get('chain_type', None)
                max_tokens = parametros.get('max_tokens', None)
                temperature = parametros.get('temperature', None)
                if llm:
                    self.asignar_llm( llm = llm )
                    asignado = True
                if num_docs:
                    self.CFG['num_docs'] = str(num_docs)
                    asignado = True
                if chain_type:
                    self.CFG['chain_type'] = chain_type
                    asignado = True
                if max_tokens and temperature:
                    self.MODELO.configurar_api_llm([
                        ("temperature", str(temperature)),
                        ("max_tokens", str(max_tokens))
                    ])
                    asignado = True
                return asignado

            except KeyError as e:
                asignado = False
                self.gestor_registrar.error( f"{e}" )

            except Exception as e:
                asignado = False
                self.gestor_registrar.error( f"{e}" )

        return asignado

    # Función para configurar las APIS y recursos que usará el ejecutor
    def abrir_ejecutor( self, id_doc, instruccion ):
        try:
            # Carga el índice vectorial en almacen.INDICE
            if self.CFG.get('clase_interaccion') != "Peticion":
                self.ALMACEN.cargar_indice(
                    api_emb = self.MODELO.api_emb(),
                    id_doc = id_doc
                )

                # Si no se asignó instrucción, crea una por defecto
                if not instruccion:
                    instruccion = self.CFG.get('instruccion')

            # Crea un ejecutor y lo entrega
            self.EJECUTOR = self.MODELO.crear_cadena(
                indice = self.ALMACEN.INDICE,
                clase = self.CFG.get('clase_interaccion'),
                chain_type = str(self.CFG.get('chain_type')),
                num_docs = int( self.CFG.get('num_docs') ),
                plantilla = self._construir_plantilla( nombre=instruccion, peticion='' )
            )
            return self.EJECUTOR

        except Exception as e:
            self.gestor_registrar.error( f"{e}" )

        return None

    # Función para enviar una instruccion a LLM y recibir la respuesta
    def ejecutar_instruccion( self, peticion, id_sesion ):
        respuesta = ''
        if self.EJECUTOR and peticion:
            try:
                # Clase: Conversación
                if self.CFG.get('clase_interaccion') == "Conversacion":
                    
                    chat_history = self._abrir_historial( uuid = f"{id_sesion}-{self.config.CARPETA}" )
                    resultado = self.EJECUTOR( inputs = {
                            "question": peticion,
                            "chat_history": chat_history
                        },
                        return_only_outputs = True
                    )
                    respuesta = resultado['answer']
                    self._guardar_historial( uuid = f"{id_sesion}-{self.config.CARPETA}" )

                # Clase: Peticion
                if self.CFG.get('clase_interaccion') == "Peticion":
                    
                    chat_history = self._abrir_historial( uuid = f"{id_sesion}-{self.config.CARPETA}" )
                    resultado = self.EJECUTOR( inputs = {
                            "input": peticion,
                            "chat_history": chat_history
                        },
                        return_only_outputs = True
                    )
                    respuesta = resultado['response']
                    self._guardar_historial( uuid = f"{id_sesion}-{self.config.CARPETA}" )

                # Clase: Consulta
                elif self.CFG.get('clase_interaccion') == "Consulta":
                    respuesta = self.EJECUTOR.run( peticion )
                
                self.gestor_registrar.debug( f"peticion: {peticion}\nrespuesta: {respuesta}\ncarpeta: {self.config.CARPETA}\n")

            except Exception as e:
                self.gestor_registrar.error( f"{e}" )
            
        return respuesta

    # Función para procesar la respuesta recibida
    def procesar_respuesta( self, respuesta, peticion, coleccion, tiempo ):
        import string
        try:
            if peticion and respuesta:
                app = self.config.APP.get('app_id')
                respuesta = str( respuesta).lstrip(string.punctuation)
                bd = BaseDatos(self.config)
                id_interaccion = bd.agregar_interaccion(
                    peticion = peticion,
                    respuesta = respuesta,
                    tiempo = int(tiempo),
                    coleccion = coleccion,
                    app = app
                )
                return { "uid": str(id_interaccion), "respuesta": respuesta }

        except Exception as e:
            self.gestor_registrar.error( f"{e}" )

        return None

    # Función para registrar la evaluación del usuario en la BD
    def registrar_evaluacion( self, uid, evaluacion ):
        try:
            if uid and evaluacion:
                bd = BaseDatos(self.config)
                resultado = bd.evaluar_interaccion( uid, evaluacion )
                return resultado

        except Exception as e:
            self.gestor_registrar.error( f"{e}" )

        return False

    # Función para revisar las interacciones con usuarios en la BD
    def revisar_interacciones( self, parametros ):
        resultados = None
        if parametros:
            try:
                nav = 1
                aux = parametros.get('nav', 1)
                if aux:
                    nav = int(aux)
                max = 10
                aux = parametros.get('max', 10)
                if aux:
                    max = int(aux)

                bd = BaseDatos(self.config)
                resultados = bd.buscar_interacciones( parametros=parametros, pagina=nav, casos=max )

            except KeyError as e:
                self.gestor_registrar.error( f"{e}" )

            except Exception as e:
                self.gestor_registrar.error( f"{e}" )

        return resultados

    # Función para recuperar interacciones de un usuario
    def obtener_interacciones( self, id_doc ):
        bd = BaseDatos(self.config)
        filtro = f"{self.config.USUARIO.get('email')}-{id_doc}-{self.config.CARPETA}"
        resultados = bd.interacciones_usuario( filtro=filtro )
        return resultados

    # Función para borrar las interacciones de un usuario
    def vaciar_interacciones( self, id_doc ):
        bd = BaseDatos(self.config)
        uuid = f"{self.config.USUARIO.get('email')}-{id_doc}-{self.config.CARPETA}"
        resultado = bd.borrar_historiales( uuid )
        return resultado

    # Función para enviar busqueda a LLM y recibir la respuesta
    def consultar_busqueda( self, texto ):
        try:
            respuesta = ''
            # Carga valores de configuración
            instruccion = "intro-buscador"
            config = self._cargar_instruccion( instruccion )
            chain_type = config.get('chain_type', '')
            num_docs = config.get('num_docs', '')
            llm = config.get('llm', '')
            max_tokens = config.get('max_tokens', '')
            temperature = config.get('temperature', '')
            plantilla = config.get('plantilla', '')
            parametros = {
                "llm": llm,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "chain_type": chain_type,
                "num_docs": num_docs
            }
            self.configurar_ejecutor( parametros=parametros )

            # Carga el índice vectorial en almacen.INDICE
            api_emb = self.MODELO.api_emb()
            self.ALMACEN.cargar_indice(
                api_emb = api_emb
            )
            # Si se cargó el índice, crea un ejecutor
            if self.ALMACEN.INDICE and texto:
                self.EJECUTOR = self.MODELO.crear_cadena(
                    indice = self.ALMACEN.INDICE,
                    clase = "Busqueda",
                    chain_type = chain_type,
                    num_docs = int(num_docs),
                    plantilla = plantilla
                )
                if self.EJECUTOR:
                    respuesta = self.EJECUTOR( {"query": texto} )
                    
            else:
                self.gestor_registrar.error( f"{self.config.MENSAJES.get('ERROR_CONSULTAR_BUSQUEDA')}" )

        except Exception as e:
            self.gestor_registrar.error( f"{e}" )

        return respuesta

    # Función para subir un archivo de audio y guardarlo
    def transcribir_audio( self, archivo, idioma ):
        from archivos import Archivos
        try:
            if archivo:
                archivos = Archivos(self.config)
                resultado = "ERROR"
                ruta = archivos.cargar_audio( archivo=archivo, recurso="TEMP", nombre=self.config.USUARIO.get('id') )
                if len(ruta) > 1:
                    mensaje = self.config.MENSAJES.get('EXITO_ARCHIVO_SUBIDO')
                    resultado = "EXITO"
                elif ruta == archivos.NOMBRE_NO_VALIDO:
                    mensaje = self.config.MENSAJES.get('ERROR_NOMBRE_NOVALIDO')
                elif ruta == archivos.TIPO_NO_PERMITIDO:
                    mensaje = self.config.MENSAJES.get('ERROR_ARCHIVO_NOPERMITIDO')
                else:
                    mensaje = self.config.MENSAJES.get('ERROR_ARCHIVO_NOSUBIDO')
                if archivos.comprobar_archivo( ruta ):
                    texto = self.MODELO.transcribir_audio( ruta=ruta, idioma=idioma )
                    archivos.borrar_archivo(ruta)
                    respuesta = { "resultado": resultado, "mensaje": mensaje, "texto": texto }
                    return respuesta

        except Exception as e:
            self.gestor_registrar.error( f"{e}" )

        return None

######################################################
# FUNCIONES PUBLICAS PARA COLECCIONES Y CARPETAS
######################################################

    # Función para crear una nueva colección / aplicación
    def crear_coleccion( self, coleccion, nombre, descripcion, api_key, carpetas, chatgpt, whisper ):
        import unicodedata, re
        from archivos import Archivos
        archivos = Archivos(self.config)
        mensaje = f"{self.config.MENSAJES.get('ERROR_COLECCION_NOCREADA')}: {coleccion}"

        coleccion = re.sub( r'[\\/:"*?<>|°ºª~!#$%&=¿¡+{};@^_`…\-(),\[\]\'\s]', "", coleccion )
        coleccion = re.sub( r'\.', "", coleccion )
        coleccion = coleccion.lower().strip()
        coleccion = unicodedata.normalize( 'NFD', coleccion ).encode( 'ascii', 'ignore' ).decode( 'utf-8' )
        if self.config.comprobar_coleccion( nombre_coleccion=coleccion ):
            mensaje = f"{self.config.MENSAJES.get('ERROR_COLECCION_YAEXISTE')}: {coleccion}"
        else:
            nombre = unicodedata.normalize( 'NFD', nombre ).encode( 'ascii', 'ignore' ).decode( 'utf-8' )
            descripcion = unicodedata.normalize( 'NFD', descripcion ).encode( 'ascii', 'ignore' ).decode( 'utf-8' )
            if self.config.agregar_coleccion( nombre_coleccion=coleccion, etiqueta_coleccion=nombre ):
                self.config.COLECCION = coleccion
                archivo_coleccion = f"{archivos.obtener_ruta( tipo_recurso='DATOS' )}/coleccion.zip"
                if self.config.importar_coleccion( nombre_coleccion=coleccion, archivo_zip=archivo_coleccion ):
                    ruta_aux = f"{archivos.obtener_ruta( tipo_recurso='CONFIG' )}/config.json"
                    if archivos.comprobar_archivo( ruta=ruta_aux ):
                        with open( ruta_aux, 'r', encoding='utf-8' ) as f:
                            datos = json.load( f )
                        datos['app_nombre'] = nombre
                        datos['app_id'] = f"Admin-{coleccion}"
                        datos['token_key'] = f"key-secreta-{coleccion}"
                        datos['descripcion'] = descripcion
                        datos['carpeta'] = ''
                        datos['carpetas'] = carpetas
                        datos['chatgpt'] = chatgpt
                        datos['whisper'] = whisper
                        datos['openai_api_key'] = api_key
                        with open( ruta_aux, "w", encoding='utf-8' ) as f:
                            json.dump( datos, f, indent=4 )

                        archivos.crear_carpeta( ruta=archivos.obtener_ruta( tipo_recurso='SESIONES' ) )
                        archivos.crear_carpeta( ruta=archivos.obtener_ruta( tipo_recurso='TEMP' ) )
                        mensaje = f"{self.config.MENSAJES.get('EXITO_COLECCION_CREADA')}: {coleccion}"

        return mensaje

    # Función para crear una nueva carpeta
    def crear_carpeta( self, nombre_carpeta, etiqueta_carpeta, tipos_archivo, modulos ):
        import unicodedata, re
        from archivos import Archivos

        mensaje = f"{self.config.MENSAJES.get('ERROR_CARPETA_NOCREADA')}"

        if nombre_carpeta and etiqueta_carpeta and tipos_archivo:
            nombre_carpeta = re.sub( r'[\\/:"*?<>|°ºª~!#$%&=¿¡+{};@^_`…\-(),\[\]\'\s]', "", nombre_carpeta )
            nombre_carpeta = re.sub( r'\.', "", nombre_carpeta )
            nombre_carpeta = nombre_carpeta.lower().strip()
            nombre_carpeta = unicodedata.normalize( 'NFD', nombre_carpeta ).encode( 'ascii', 'ignore' ).decode( 'utf-8' )
            etiqueta_carpeta = unicodedata.normalize( 'NFD', etiqueta_carpeta ).encode( 'ascii', 'ignore' ).decode( 'utf-8' )
            self.config.CARPETA = nombre_carpeta
            archivos = Archivos(self.config)
            ruta_carpeta = archivos.obtener_ruta( tipo_recurso='ARCHIVOS' )
            ruta_indices = archivos.obtener_ruta( tipo_recurso='INDICES' )
            if archivos.comprobar_carpeta( ruta=ruta_carpeta ):
                mensaje = f"{self.config.MENSAJES.get('ERROR_CARPETA_YAEXISTE')}: {nombre_carpeta}"
            else:
                archivos.crear_carpeta( ruta=ruta_carpeta )
                archivos.crear_carpeta( ruta=ruta_indices )
                ruta_aux = f"{archivos.obtener_ruta( tipo_recurso='CONFIG' )}/carpetas.json"
                if archivos.comprobar_archivo( ruta=ruta_aux ):
                    with open( ruta_aux, 'r', encoding='utf-8' ) as f:
                        datos = json.load( f )
                    nueva_carpeta = {
                        "carpeta": nombre_carpeta,
                        "etiqueta": etiqueta_carpeta,
                        "tipos_archivo": tipos_archivo,
                        "modulos": modulos,
                        "instruccion": "intro-docs",
                        "clase_interaccion": "Conversacion",
                        "api_llm": "OpenAI_GPT-3.5",
                        "api_emb": "OpenAI_Embeddings",
                        "sistema_archivos": "LOCAL",
                        "almacen_indice": "LOCAL",
                        "cargar_documentos": "Diferenciado",
                        "procesar_documentos": "Basico",
                        "que_procesar": "metadatos",
                        "dividir_documentos": "Recursivo",
                        "trozo": "1000",
                        "num_docs": "5",
                        "chain_type": "stuff"
                    }
                    datos.append( nueva_carpeta )
                    with open( ruta_aux, "w", encoding='utf-8' ) as f:
                        json.dump( datos, f, indent=4 )

                    mensaje = f"{self.config.MENSAJES.get('EXITO_CARPETA_CREADA')}: {nombre_carpeta}"

        return mensaje

    # Función para borrar una carpeta
    def borrar_carpeta( self, nombre_carpeta ):
        from archivos import Archivos
        mensaje = f"{self.config.MENSAJES.get('ERROR_CARPETA_NOBORRADA')}"
        try:
            bd = BaseDatos(self.config)
            resultado = bd.borrar_documentos( carpeta=nombre_carpeta )
            if resultado:
                archivos = Archivos(self.config)
                self.config.CARPETA = nombre_carpeta
                ruta = archivos.obtener_ruta( tipo_recurso='ARCHIVOS' )
                archivos.borrar_carpeta( ruta )
                ruta = archivos.obtener_ruta( tipo_recurso='INDICES' )
                archivos.borrar_carpeta( ruta )
                ruta_archivo = f"{self.config.RUTA.get('CONFIG')}/carpetas.json"
                with open( ruta_archivo, 'r', encoding='utf-8' ) as f:
                    datos = json.load( f )
                carpetas = [ carpeta for carpeta in datos if carpeta["carpeta"] != nombre_carpeta ]
                with open( ruta_archivo, "w", encoding='utf-8' ) as f:
                    json.dump( carpetas, f, indent=4 )
                mensaje = f"{self.config.MENSAJES.get('EXITO_CARPETA_BORRADA')}"
        except Exception as e:
            mensaje = f"{self.config.MENSAJES.get('ERROR_CARPETA_NOBORRADA')}"
        return mensaje

######################################################
# FUNCIONES PUBLICAS PARA PROMPTS Y PLANTILLAS
######################################################

    # Función para consultar los prompts de la colección
    def consultar_prompts( self ):
        bd = BaseDatos(self.config)
        tareas = bd.seleccionar_tareas()
        prompts = bd.seleccionar_prompts()
        resultados = { "tareas": tareas, "prompts": prompts }
        return resultados

    # Función para burrar una plantilla de prompt
    def borrar_plantilla( self, uid ):
        if uid:
            try:
                bd = BaseDatos(self.config)
                return bd.borrar_plantilla( uid=uid )
            except Exception as e:
                self.gestor_registrar.error( f"{e}" )
        return False

    # Función para agregar una plantilla de prompt
    def ingresar_plantilla( self, parametros ):
        uid = 0
        bd = BaseDatos(self.config)
        if parametros:
            uid = bd.ingresar_plantilla( parametros=parametros )
        return uid

    # Función para obtener los datos de una plantilla de prompt
    def abrir_plantilla( self, uid ):
        resultados = None
        if uid:
            try:
                bd = BaseDatos(self.config)
                resultados = bd.abrir_plantilla( uid=uid )
            except Exception as e:
                self.gestor_registrar.error( f"{e}" )
        return resultados

    # Función para obtener una lista de las plantillas de prompt
    def consultar_plantillas( self, parametros ):
        resultados = None
        nav = 1
        max = 100
        try:
            if parametros:
                aux = parametros.get('nav', nav)
                if aux:
                    nav = int(aux)
                aux = parametros.get('max', max)
                if aux:
                    max = int(aux)
            bd = BaseDatos(self.config)
            resultados = bd.consultar_plantillas( parametros=parametros, pagina=nav, casos=max )
        except Exception as e:
            self.gestor_registrar.error( f"{e}" )
        return resultados

    # Función para obtener una lista de tareas de prompts
    def consultar_tareas( self ):
        resultados = None
        try:
            bd = BaseDatos(self.config)
            resultados = bd.consultar_tareas()
        except Exception as e:
            self.gestor_registrar.error( f"{e}" )
        return resultados

    # Función para actualizar los datos de una plantilla de prompt
    def actualizar_plantilla( self, uid, parametros ):
        resultado = False
        bd = BaseDatos(self.config)
        if parametros:
            resultado = bd.actualizar_plantilla( uid=uid, parametros=parametros )
        return resultado

######################################################
# FUNCIONES PUBLICAS PARA ARCHIVOS Y DOCUMENTOS
######################################################

    # Función para subir un archivo y guardarlo
    def subir_archivo( self, archivo ):
        from archivos import Archivos
        try:
            if archivo:
                archivos = Archivos(self.config)
                resultado = "ERROR"
                nombre = ""
                cargar = archivos.cargar_archivo( archivo=archivo )
                if len(cargar) > 1:
                    mensaje = self.config.MENSAJES.get('EXITO_ARCHIVO_SUBIDO')
                    resultado = "EXITO"
                    nombre = cargar
                elif cargar == archivos.NOMBRE_NO_VALIDO:
                    mensaje = self.config.MENSAJES.get('ERROR_NOMBRE_NOVALIDO')
                elif cargar == archivos.ARCHIVO_YA_EXISTE:
                    mensaje = self.config.MENSAJES.get('ERROR_ARCHIVO_YAEXISTE')
                elif cargar == archivos.TIPO_NO_PERMITIDO:
                    mensaje = self.config.MENSAJES.get('ERROR_ARCHIVO_NOPERMITIDO')
                else:
                    mensaje = self.config.MENSAJES.get('ERROR_ARCHIVO_NOSUBIDO')
                respuesta = { "resultado": resultado, "mensaje": mensaje, "nombre": nombre }
                return respuesta

        except Exception as e:
            self.gestor_registrar.error( f"{e}" )

        return None

    # Función para ingresar un archivo cargado como un documento en la BD
    def ingresar_documento( self, archivo ):
        from archivos import Archivos

        id_doc = 0
        try:
            # Recuperar los atributos del archivo
            archivos = Archivos(self.config)
            atributos = archivos.obtener_atributos( archivo=archivo )
            if atributos:
                archivo_nombre, archivo_extension, archivo_peso, ruta_completa, ruta_directorio = atributos
            else:
                return id_doc

            # Guardar ficha del documento en BD de recursos y recuperar su UID
            bd = BaseDatos(self.config)
            app = self.config.APP.get('app_id')
            codigo = self.config.cifrar_texto(archivo_nombre)
            parametros = {
                "archivo": archivo_nombre,
                "ruta": ruta_directorio,
                "tipo": archivo_extension,
                "peso": archivo_peso,
                "coleccion": self.config.COLECCION,
                "carpeta": self.config.CARPETA,
                "titulo": archivo_nombre,
                "app": app,
                "codigo": codigo
            }
            id_doc = bd.agregar_documento(
                estado = self.ESTADO_DOC.get('INGRESADO'),
                parametros = parametros
            )

        except Exception as e:
            self.gestor_registrar.error( f"{e}" )

        return id_doc

    # Función para crear metadatos de un documento mediante búsqueda semántica y APIs EMB+LLM
    def catalogar_documento( self, id_doc, campos ):
        import string
        catalogado = False
        try:
            resultados = {}
            if id_doc and campos:
                caracteres_dobles = [ " ", ".", "|", '"', "-", "_", "-", "/", "(", ")", "?", "!", ",", ";", ":", "[", "]" ]
                llm_inicial = self.MODELO.LLM.get('_uid')

                bd = BaseDatos(self.config)
                titulo = ''
                datos_doc = bd.seleccionar_documento( id_doc=id_doc )
                if datos_doc:
                    titulo = datos_doc.get('titulo')
                    carpeta = datos_doc.get('carpeta')
                    self.config.CARPETA = carpeta

                    instruccion = self._cargar_instruccion( nombre= "intro-metadatos" )
                    intro = instruccion.get('plantilla', '')
                    variables = {
                        'fecha': self.config.APP.get('fecha'),
                        'titulo': titulo
                    }
                    intro = self._reemplazar_etiquetas( intro, variables )
                    self.ALMACEN.cargar_indice(
                        api_emb = self.MODELO.api_emb(),
                        id_doc = id_doc
                    )

                    for campo in campos:
                        metadatos = self._cargar_instruccion( nombre= f"meta-{campo}" )
                        max_tokens = int(metadatos.get('max_tokens', 0))
                        temperature = float(metadatos.get('temperature', 0.0))
                        chain_type = metadatos.get('chain_type', '')
                        num_docs = int(metadatos.get('num_docs', 0))
                        plantilla = metadatos.get('plantilla', '')
                        plantilla = self._reemplazar_etiquetas( plantilla, variables )
                        llm = metadatos.get( 'llm', llm_inicial )

                        self.asignar_llm( llm = llm )
                        self.MODELO.configurar_api_llm([
                            ("temperature", str(temperature)),
                            ("max_tokens", str(max_tokens))
                        ])

                        if self.ALMACEN.INDICE:
                            self.EJECUTOR = None
                            self.EJECUTOR = self.MODELO.crear_cadena(
                                indice = self.ALMACEN.INDICE,
                                clase = "Consulta",
                                chain_type = chain_type,
                                num_docs = int( num_docs ),
                                plantilla = intro
                            )
                            if self.EJECUTOR:
                                respuesta = self.EJECUTOR.run( plantilla )
                                respuesta = str(respuesta).strip()
                                respuesta = self._limpiar_repetidos( respuesta, caracteres_dobles )
                                respuesta = respuesta.lstrip(string.punctuation)
                                respuesta = respuesta.rstrip()
                                # resultados = { **resultados, campo: respuesta }
                                resultados = { campo: respuesta }
                                catalogado = bd.actualizar_documento(
                                    id_doc = id_doc,
                                    estado = str(self.ESTADO_DOC.get('CATALOGADO')),
                                    parametros = resultados
                                )

        except Exception as e:
            self.gestor_registrar.error( f"{e}" )

        return catalogado

    # Función para consultar el registro de documentos en la BD
    def consultar_documentos( self, parametros ):
        resultados = None
        if parametros:
            try:
                nav = 1
                aux = parametros.get('nav', 1)
                if aux:
                    nav = int(aux)
                max = 10
                aux = parametros.get('max', 10)
                if aux:
                    max = int(aux)

                bd = BaseDatos(self.config)
                resultados = bd.buscar_documentos( parametros=parametros, pagina=nav, casos=max )

            except Exception as e:
                self.gestor_registrar.error( f"{e}" )

        return resultados

    # Función para recuperar los datos para descargar documento
    def descargar_documento( self, codigo ):
        resultados = None
        if codigo:
            try:
                bd = BaseDatos(self.config)
                resultados = bd.sumar_documento( codigo=codigo )

            except KeyError as e:
                self.gestor_registrar.error( f"{e}" )

            except Exception as e:
                self.gestor_registrar.error( f"{e}" )

        return resultados

    # Función para recuperar los datos de un documento de la BD
    def abrir_documento( self, id_doc ):
        resultados = None
        if id_doc:
            try:
                bd = BaseDatos(self.config)
                resultados = bd.abrir_documento( id_doc=id_doc )

            except KeyError as e:
                self.gestor_registrar.error( f"{e}" )

            except Exception as e:
                self.gestor_registrar.error( f"{e}" )

        return resultados

    # Función para borrar un documento del disco y la BD
    def borrar_documento( self, id_doc ):
        from archivos import Archivos
        if id_doc:
            try:
                bd = BaseDatos(self.config)
                resultados = bd.seleccionar_documento( id_doc=id_doc )
                if resultados:
                    ruta_archivo = resultados.get('ruta', '')
                    nombre_archivo = resultados.get('archivo', '')
                    tipo_archivo = resultados.get('tipo', '')
                    archivo = f"{ruta_archivo}/{nombre_archivo}.{tipo_archivo}"
                    archivos = Archivos(self.config)
                    if archivos.borrar_archivo( ruta=archivo ):
                        self.ALMACEN.borrar_indice( id_doc=id_doc )
                        if bd.borrar_documento( id_doc=id_doc ):
                            return True

            except KeyError as e:
                self.gestor_registrar.error( f"{e}" )

            except Exception as e:
                self.gestor_registrar.error( f"{e}" )

        return False

    # Función para guardar los datos editados de un documento en la BD
    def guardar_documento( self, id_doc, parametros ):
        estado = 0
        bd = BaseDatos(self.config)
        if parametros:
            estado = parametros.get('estado', self.ESTADO_DOC.get('CATALOGADO'))
        guardado = bd.actualizar_documento(
            id_doc = id_doc,
            estado = str(estado),
            parametros = parametros
        )
        return guardado

    # Función para cargar una imagen y guardarla en diferentes formatos
    def cargar_imagen( self, archivo, aplicacion ):
        from archivos import Archivos
        try:
            if archivo and aplicacion:
                archivos = Archivos(self.config)
                return archivos.cargar_imagen( archivo=archivo, aplicacion=aplicacion )
        except Exception as e:
            self.gestor_registrar.error( f"{e}" )

        return None

    # Función para obtener las carpetas con documentos desde la BD
    def obtener_carpetas( self ):
        bd = BaseDatos(self.config)
        resultados = bd.resumen_carpetas()
        return resultados

    # Función para obtener los documentos que se pueden consultar
    def obtener_documentos( self ):
        bd = BaseDatos(self.config)
        resultados = bd.documentos_consultables()
        return resultados

    # Función para buscar documentos en índice vectorial
    def buscar_textos_documentos( self, parametros ):
        import string, re
        try:
            buscar = parametros.get('buscar', None)
            max_docs = int(parametros.get('max_docs', '10'))
            api_emb = self.MODELO.api_emb()
            self.ALMACEN.cargar_indice(
                api_emb = api_emb
            )
            if not self.ALMACEN.INDICE or not max_docs or not buscar:
                return {}

            if self.ALMACEN.INDICE:
                archivos = []
                resultados = []
                listado = []
                caso = 0
                trozo = 0
                documentos = None
                datos = []

                embedding = api_emb.embed_query(buscar)
                documentos = self.ALMACEN.INDICE.similarity_search_by_vector(
                    embedding = embedding,
                    k = max_docs
                )
                if documentos:
                    for documento in documentos:
                        metadata = documento.metadata
                        page_content = str( documento.page_content )
                        page_content = re.sub( r"\n", " ", page_content )
                        page_content = re.sub( r"  ", " ", page_content )
                        page_content = page_content.strip()
                        page_content = page_content.lstrip(string.punctuation).rstrip()
                        if len(page_content) > 125:
                            archivo = metadata.get('filename', '')
                            nombre = self._obtener_nombre(archivo)
                            tipo = self._obtener_extension(archivo)
                            titulo = metadata.get('title', '')
                            paginas = metadata.get('total_pages', 0)
                            trozo = trozo + 1
                            if not nombre in listado:
                                listado.append(nombre)
                                caso = caso + 1
                                archivos.append( {"caso": caso, "nombre": nombre, "tipo": tipo, "titulo": titulo, "paginas": paginas} )
                            registro = {
                                "trozo": trozo,
                                "nombre": nombre,
                                "pagina": metadata.get('page', 0),
                                "contenido": page_content
                            }
                            resultados.append(registro)
                buscar = re.sub( r"'", "", buscar )
                buscar = re.sub( r'"', "", buscar )
                bd = BaseDatos(self.config)
                extraidos = bd.extraer_documentos( listado=listado, total=max_docs )
                lista_final = []
                for arc in archivos:
                    for doc in extraidos:
                        if doc['nombre'] == arc['nombre']:
                            archivo_completo = {**arc, **doc}
                            lista_final.append(archivo_completo)
                            break
                datos = { "buscar": buscar, "archivos": lista_final, "resultados": resultados }
                return datos
            else:
                self.gestor_registrar.error( f"{self.config.MENSAJES.get('ERROR_GESTOR_NODEFINIDO')}: {self.config.CARPETA}" )

        except Exception as e:
            self.gestor_registrar.error( f"{e}" )

        return {}

    # Función para exportar metadatos de documentos a un archivo Excel
    def exportar_metadatos( self, nombre ):
        ruta = None
        bd = BaseDatos(self.config)
        datos = bd.exportar_metadatos( self.config.CARPETA )
        if datos and nombre:
            ruta = self.ALMACEN.guardar_excel( nombre=nombre, datos=datos, directorio="TEMP" )
        return ruta

    # Función para importar metadatos de documentos desde un archivo Excel
    def importar_metadatos( self, archivo, nombre ):
        from archivos import Archivos
        resultado = False
        try:
            if archivo and nombre:
                archivos = Archivos(self.config)
                cargado = archivos.guardar_archivo( archivo=archivo, nombre=nombre, directorio="TEMP" )
                if cargado:
                    bd = BaseDatos(self.config)
                    datos = self.ALMACEN.leer_excel( nombre=nombre, directorio="TEMP" )
                    if datos:
                        for fila in datos:
                            resultado = bd.importar_metadatos( parametros=fila )

        except Exception as e:
            self.gestor_registrar.error( f"{e}" )

        return resultado

    # Función para obtener los documentos destacados
    def consultar_destacados( self, total, modulo ):
        if not total:
            total = 10
        bd = BaseDatos(self.config)
        carpetas = self._lista_carpetas( modulo=modulo )
        resultados = bd.documentos_destacados( total=int(total), carpetas=carpetas )
        return resultados


######################################################
# FUNCIONES PRIVADAS
######################################################

    def _cargar_configuracion( self ):
        try:
            ruta_archivo = f"{self.config.RUTA.get('CONFIG')}/carpetas.json"
            with open( ruta_archivo, 'r', encoding='utf-8' ) as f:
                datos = json.load( f )
            for fila in datos:
                if fila.get('carpeta') == self.config.CARPETA:
                    return fila

        except Exception as e:
            self.gestor_registrar.error( f"{e}" )

        return {}

    def _cargar_instruccion( self, nombre ):
        try:
            ruta_instrucciones = f"{self.config.RUTA['CONFIG']}/instrucciones.json"
            with open( ruta_instrucciones, 'r', encoding='utf-8' ) as f:
                instrucciones = json.load( f )
            for fila in instrucciones:
                if fila.get('_uid') == nombre:
                    return fila

        except Exception as e:
            self.gestor_registrar.error( f"{e}" )

        return None

    def _construir_plantilla( self, nombre, peticion ):
        instruccion = peticion
        try:
            if nombre:
                base = self._cargar_instruccion( nombre )
                if base:
                    peticion = str(peticion).strip()
                    plantilla = base.get('plantilla')
                    variables = {
                        'fecha': self.config.APP.get('fecha'),
                        'peticion': peticion
                    }
                    instruccion = self._reemplazar_etiquetas( plantilla, variables )

        except Exception as e:
            self.gestor_registrar.error( f"{e}" )

        return instruccion

    # Función para abrir el historial de interacciones
    def _abrir_historial( self, uuid ):
        historial = []
        try:
            if uuid and self.MODELO.MEMORIA:
                # Recuperar el historial desde la BD y escribirlo en la memoria
                try:
                    bd = BaseDatos(self.config)
                    contenido = bd.leer_historial( uuid = uuid )
                    if contenido:
                        historial = self.MODELO.escribir_memoria( contenido=contenido )
                except (json.JSONDecodeError):
                    historial = []

        except Exception as e:
            self.gestor_registrar.error( f"{e}" )
            historial = []

        return historial

    # Función para guardar el historial de interaciones
    def _guardar_historial( self, uuid ):
        try:
            # Recuperar el historial desde la memoria y guardarlo en la BD
            if uuid and self.MODELO.MEMORIA:
                contenido = self.MODELO.leer_memoria()
                if contenido:
                    bd = BaseDatos(self.config)
                    resultado = bd.guardar_historial(
                        uuid = uuid,
                        contenido = contenido
                    )
                    if resultado:
                        return True

        except Exception as e:
            self.gestor_registrar.error( f"{e}" )

        return False

    # Función para reemplazar etiquetas por valores de variables en una cadena de texto
    def _reemplazar_etiquetas( self, texto, variables ):
        for variable, valor in variables.items():
            texto = texto.replace( '{' + variable + '}', str(valor) )
        return texto

    # Función para reemplazar dobles caracteres (repetidos) en un texto, en forma recursiva
    def _limpiar_repetidos( self, texto, caracteres ):
        cadena_limpia = texto
        se_encontro_doble = False

        for caracter in caracteres:
            doble_caracter = caracter * 2

            if doble_caracter in cadena_limpia:
                se_encontro_doble = True
                cadena_limpia = cadena_limpia.replace( doble_caracter, caracter )

        if se_encontro_doble:
            return self._limpiar_repetidos( cadena_limpia, caracteres )
        else:
            return cadena_limpia

    # Función para extraer el nombre de un archivo descartando su extensión
    def _obtener_nombre( self, archivo ):

        # Dividir el nombre del archivo en partes usando el punto como separador
        partes = archivo.split('.')

        # Si solo hay una parte (no hay puntos), entonces devolvemos el nombre original
        if len( partes ) == 1:
            return archivo

        # Unimos todas las partes excepto la última para obtener el nombre del archivo sin extensión
        nombre = ".".join( partes[:-1] )

        return nombre

    def _obtener_extension( self, archivo ):

        # Dividir el nombre del archivo en partes usando el punto como separador
        partes = archivo.split('.')

        # Si solo hay una parte (no hay puntos), entonces no hay extensión y devuelve una cadena vacía
        if len( partes ) == 1:
            return ""

        # Si hay más de una parte, devuelve la última parte, que corresponde a la extensión
        return partes[-1]

    def _lista_carpetas( self, modulo ):
        ruta_archivo = f"{self.config.RUTA.get('CONFIG')}/carpetas.json"
        with open( ruta_archivo, 'r', encoding='utf-8' ) as f:
            datos = json.load( f )
        carpetas = []
        for item in datos:
            if modulo in item['modulos']:
                carpetas.append(item['carpeta'])

        return carpetas
