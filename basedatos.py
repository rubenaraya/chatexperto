# basedatos.py
import re, sqlite3
from registros import configurar_logger

class BaseDatos:
    def __init__( self, config=None ):

        # Manejador de registros
        self.basedatos_registrar = configurar_logger( "basedatos", "basedatos.log" )
        self.config = config
        
        # Bases de datos (SQLite)
        self._BD = {
            'USUARIOS': f"{self.config.RUTA.get('BASEDATOS')}/usuarios.db",
            'LOGS': f"{self.config.RUTA.get('BASEDATOS')}/logs.db",
            'RECURSOS': f"{self.config.RUTA.get('BASEDATOS')}/recursos.db"
        }

        # Plantillas de instrucciones SQL
        self._SQL = self._cargar_configuracion()
        
        # Tipos de limpiezas de datos
        self._limpiar_entrada = {
            'texto': self._limpiar_texto,
            'fecha': self._limpiar_fecha,
            'numero': self._limpiar_numero
        }

######################################################
# FUNCIONES PUBLICAS
######################################################

    # Función para agregar una interaccion realizada mediante un ejecutor
    def agregar_interaccion( self, peticion='', respuesta='', tiempo=0, coleccion='', app='' ):
        try:
            conexion = sqlite3.connect( self._BD.get('LOGS') )
            consulta_sql = self._SQL.get( 'INSERT_INTERACCION' )
            parametros = [
                self.config.APP.get('fecha'), 
                self.config.APP.get('hora'), 
                peticion, respuesta, coleccion, tiempo, app
            ]
            bd = conexion.cursor()
            bd.execute( consulta_sql, parametros )
            conexion.commit()
            uid = bd.lastrowid
            conexion.close()
            return uid
        except Exception as e:
            self.basedatos_registrar.error( f"{e}" )
            return 0
        finally:
            if conexion:
                conexion.close()

    # Función para registrar la evaluación del usuario sobre una interaccion
    def evaluar_interaccion( self, uid=0, evaluacion=0 ):
        try:
            conexion = sqlite3.connect( self._BD.get('LOGS') )
            consulta_sql = self._SQL.get( 'UPDATE_INTERACCION' )
            parametros = [ evaluacion, uid ]
            bd = conexion.cursor()
            bd.execute( consulta_sql, parametros )
            conexion.commit()
            conexion.close()
            return True
        except Exception as e:
            self.basedatos_registrar.error( f"{e}" )
            return False
        finally:
            if conexion:
                conexion.close()

    # Función para buscar interacciones (con filtros) y obtener sus resultados
    def buscar_interacciones( self, parametros={}, pagina=1, casos=10 ):
        try:
            conexion = sqlite3.connect( self._BD.get('LOGS') )
            consulta_sql = self._SQL.get( 'SELECT_INTERACCIONES' )
            param = []
            
            # Compone la sentencia SQL dependiento de los parámetros recibidos
            palabras = parametros.get('palabras', None)
            if palabras:
                palabras = self._limpiar_entrada.get( 'texto' )( palabras )
                if self._validar_entrada( palabras ):
                    consulta_sql += " AND ("
                    for texto in palabras:
                        consulta_sql += " AND (UPPER(respuesta) LIKE UPPER(?) OR respuesta LIKE (?))"
                        param.append( f"%{texto}%" )
                        param.append( f"%{texto}%" )
                    consulta_sql += ")"
                    consulta_sql = str( consulta_sql ).replace(" AND ( AND ", " AND (" )

            fecha = parametros.get('fecha', None)
            if fecha:
                fecha = self._limpiar_entrada.get( 'fecha' )( fecha )
                if self._validar_entrada( fecha ):
                    consulta_sql += " AND fecha = ?"
                    param.append( fecha )

            evaluacion = parametros.get('evaluacion', None)
            if evaluacion:
                evaluacion = self._limpiar_entrada.get( 'numero' )( evaluacion )
                if self._validar_entrada( evaluacion ):
                    consulta_sql += " AND evaluacion = ?"
                    param.append( evaluacion )

            coleccion = parametros.get('coleccion', None)
            if coleccion:
                coleccion = self._limpiar_entrada.get( 'texto' )( coleccion )
                if self._validar_entrada( coleccion ):
                    for texto in coleccion:
                        consulta_sql += " AND coleccion = ?"
                        param.append( texto )
            
            # Ejecuta las consultas SQL y obtiene resultados
            consulta_total = f"SELECT COUNT(*) FROM ({consulta_sql})"
            bd = conexion.cursor()
            bd.execute( consulta_total, param )
            total_registros = bd.fetchone()[0]
            total_paginas = ( total_registros + casos - 1 ) // casos
            consulta_sql += " ORDER BY id DESC LIMIT ? OFFSET ?"
            param.extend( [casos, (pagina - 1) * casos] )
            bd.execute( consulta_sql, param )
            lista = bd.fetchall()
            conexion.close()

            # Compone y entrega la salida en formato JSON
            resultado = {
				"busqueda": {
					"palabras": palabras,
					"fecha": fecha,
					"evaluacion": evaluacion,
					"coleccion": coleccion,
					"pagina": pagina
				},
				"total": total_registros,
				"paginas": total_paginas,
				"nav": pagina,
                "max": casos,
				"resultados": [
					{
						"id": row[0],
						"fecha": row[1],
						"hora": row[2],
						"peticion": row[3],
						"respuesta": row[4],
						"tiempo": row[5],
						"evaluacion": row[6],
						"coleccion": row[7]
					}
					for row in lista
				]
			}
            return resultado
        except Exception as e:
            self.basedatos_registrar.error( f"{e}" )
            return None
        finally:
            if conexion:
                conexion.close()

    # Función para comprobar la existencia de un usuario vigente
    def comprobar_usuario( self, usuario='', password='' ):
        try:
            conexion = sqlite3.connect( self._BD.get('USUARIOS') )
            consulta_sql = self._SQL.get( 'LOGIN' )
            parametros = [ usuario, password ]
            bd = conexion.cursor()
            bd.execute( consulta_sql, parametros )
            datos_usuario = bd.fetchone()
            conexion.close()
            return datos_usuario
        except sqlite3.Error as e:
            self.basedatos_registrar.error( f"{e}" )
            return None
        finally:
            if conexion:
                conexion.close()

    # Función para agregar un documento a una colección
    def agregar_documento( self, estado=0, parametros={} ):
        try:
            param = [ int(estado) ]
            campos = ''
            valores = ''

            archivo = parametros.get('archivo', None)
            if archivo:
                param.append( archivo )
                campos = f"{campos}, archivo"
                valores = f"{valores},?"

            ruta = parametros.get('ruta', None)
            if ruta:
                ruta = str(ruta).replace('\\', '/' )
                param.append( ruta )
                campos = f"{campos}, ruta"
                valores = f"{valores},?"

            codigo = parametros.get('codigo', None)
            if codigo:
                param.append( codigo )
                campos = f"{campos}, codigo"
                valores = f"{valores},?"

            tipo = parametros.get('tipo', None)
            if tipo:
                param.append( tipo )
                campos = f"{campos}, tipo"
                valores = f"{valores},?"

            peso = parametros.get('peso', None)
            if peso:
                param.append( round(peso, None) )
                campos = f"{campos}, peso"
                valores = f"{valores},?"

            coleccion = parametros.get('coleccion', None)
            if coleccion:
                param.append( coleccion )
                campos = f"{campos}, coleccion"
                valores = f"{valores},?"

            carpeta = parametros.get('carpeta', None)
            if carpeta:
                param.append( carpeta )
                campos = f"{campos}, carpeta"
                valores = f"{valores},?"

            titulo = parametros.get('titulo', None)
            if titulo:
                param.append( str(titulo).replace('-', ' ').strip() )
                campos = f"{campos}, titulo"
                valores = f"{valores},?"

            app = parametros.get('app', None)
            if app:
                param.append( app )
                campos = f"{campos}, app"
                valores = f"{valores},?"

            propietario = parametros.get('propietario', 0)
            if propietario:
                param.append( propietario )
                campos = f"{campos}, propietario"
                valores = f"{valores},?"

            param.append( 0 )
            campos = f"{campos}, descargas"
            valores = f"{valores},?"

            param.append( 0 )
            campos = f"{campos}, respuestas"
            valores = f"{valores},?"

            param.append( self.config.APP.get('fecha') )
            campos = f"{campos}, fechaing"
            valores = f"{valores},?"

            consulta_sql = self._SQL.get( 'INSERT_DOCUMENTO' )
            consulta_sql = str(consulta_sql).replace('{campos}', campos).replace('{valores}', valores)

            conexion = sqlite3.connect( self._BD.get('RECURSOS') )
            bd = conexion.cursor()
            bd.execute( consulta_sql, param )
            conexion.commit()
            uid = bd.lastrowid
            conexion.close()
            return uid
        except Exception as e:
            self.basedatos_registrar.error( f"{e}" )
            return 0
        finally:
            if conexion:
                conexion.close()
    
    # Función para modificar datos de un documento de una colección
    def actualizar_documento( self, id_doc=0, estado=0, parametros={} ):
        try:
            param = [ estado ]
            campos = ''

            if parametros:
                titulo = parametros.get('titulo', None)
                if titulo:
                    param.append( titulo )
                    campos = f"{campos}, titulo=?"

                autores = parametros.get('autores', None)
                if autores:
                    param.append( autores )
                    campos = f"{campos}, autores=?"

                editores = parametros.get('editores', None)
                if editores:
                    param.append( editores )
                    campos = f"{campos}, editores=?"

                fechapub = parametros.get('fechapub', None)
                if fechapub:
                    param.append( fechapub )
                    campos = f"{campos}, fechapub=?"

                descripcion = parametros.get('descripcion', None)
                if descripcion:
                    param.append( descripcion )
                    campos = f"{campos}, descripcion=?"

                palabras = parametros.get('palabras', None)
                if palabras:
                    param.append( palabras )
                    campos = f"{campos}, palabras=?"

                resumen = parametros.get('resumen', None)
                if resumen:
                    param.append( resumen )
                    campos = f"{campos}, resumen=?"

                sugerencias = parametros.get('sugerencias', None)
                if sugerencias:
                    param.append( sugerencias )
                    campos = f"{campos}, sugerencias=?"

                seccion = parametros.get('seccion', None)
                if seccion:
                    param.append( seccion )
                    campos = f"{campos}, seccion=?"

                categoria = parametros.get('categoria', None)
                if categoria:
                    param.append( categoria )
                    campos = f"{campos}, categoria=?"

                zona = parametros.get('zona', None)
                if zona:
                    param.append( zona )
                    campos = f"{campos}, zona=?"

                periodo = parametros.get('periodo', 0)
                if periodo:
                    param.append( int(periodo) )
                    campos = f"{campos}, periodo=?"

            param.append( id_doc )
            consulta_sql = self._SQL.get( 'UPDATE_DOCUMENTO' )
            consulta_sql = str(consulta_sql).replace( "{campos}", campos )

            conexion = sqlite3.connect( self._BD.get('RECURSOS') )
            bd = conexion.cursor()
            bd.execute( consulta_sql, param )
            conexion.commit()
            conexion.close()
            return True
        except Exception as e:
            self.basedatos_registrar.error( f"{e}" )
            return False
        finally:
            if conexion:
                conexion.close()

    # Función para obtener datos de un documento
    def seleccionar_documento( self, id_doc=0 ):
        try:
            conexion = sqlite3.connect( self._BD.get('RECURSOS') )
            consulta_sql = self._SQL.get( 'SELECT_DOCUMENTO' )
            parametros = [ id_doc ]
            bd = conexion.cursor()
            bd.execute( consulta_sql, parametros )
            datos = bd.fetchone()
            conexion.close()
            if datos:
                columnas = [desc[0] for desc in bd.description]
                caso = {columnas[i]: datos[i] for i in range(len(columnas))}
                return caso
            else:
                return None
        except sqlite3.Error as e:
            self.basedatos_registrar.error( f"{e}" )
            return None
        finally:
            if conexion:
                conexion.close()

    # Función para obtener datos de edición de un documento
    def abrir_documento( self, id_doc=0 ):
        try:
            conexion = sqlite3.connect( self._BD.get('RECURSOS') )
            consulta_sql = self._SQL.get( 'SELECT_ABRIR_DOCUMENTO' )
            parametros = [ id_doc ]
            bd = conexion.cursor()
            bd.execute( consulta_sql, parametros )
            datos = bd.fetchone()
            conexion.close()
            if datos:
                columnas = [desc[0] for desc in bd.description]
                caso = {columnas[i]: datos[i] for i in range(len(columnas))}
                return caso
            else:
                return None
        except sqlite3.Error as e:
            self.basedatos_registrar.error( f"{e}" )
            return None
        finally:
            if conexion:
                conexion.close()

    # Función para leer el historial de conversaciones del usuario
    def leer_historial( self, uuid ):
        resultado = "[]"
        try:
            conexion = sqlite3.connect( self._BD.get('LOGS') )
            consulta_sql = self._SQL.get( 'SELECT_HISTORIAL' )
            parametros = [ uuid ]
            bd = conexion.cursor()
            bd.execute( consulta_sql, parametros )
            datos = bd.fetchone()
            if datos:
                resultado = datos[0]
            else:
                # Insertar nuevo registro
                resultado = "[]"
                consulta_sql = self._SQL.get( 'INSERT_HISTORIAL' )
                parametros = [ uuid, resultado ]
                bd = conexion.cursor()
                bd.execute( consulta_sql, parametros )
                conexion.commit()
            conexion.close()
        except sqlite3.Error as e:
            self.basedatos_registrar.error( f"{e}" )
        finally:
            if conexion:
                conexion.close()
        return resultado

    # Función para guardar el historial de conversaciones del usuario
    def guardar_historial( self, uuid, contenido ):
        try:
            conexion = sqlite3.connect( self._BD.get('LOGS') )
            consulta_sql = self._SQL.get( 'UPDATE_HISTORIAL' )
            parametros = [ 
                contenido, 
                uuid 
            ]
            bd = conexion.cursor()
            bd.execute( consulta_sql, parametros )
            conexion.commit()
            conexion.close()
            return True
        except Exception as e:
            self.basedatos_registrar.error( f"{e}" )
            return False
        finally:
            if conexion:
                conexion.close()

    # Función para buscar usuarios y obtener sus resultados
    def buscar_usuarios( self, parametros={}, pagina=1, casos=100 ):
        try:
            conexion = sqlite3.connect( self._BD.get('USUARIOS') )
            consulta_sql = self._SQL.get( 'SELECT_USUARIOS' )
            param = []

            # Ejecuta las consultas SQL y obtiene resultados
            consulta_total = f"SELECT COUNT(*) FROM ({consulta_sql})"
            bd = conexion.cursor()
            bd.execute( consulta_total, param )
            total_registros = bd.fetchone()[0]
            total_paginas = ( total_registros + casos - 1 ) // casos
            consulta_sql += " ORDER BY id DESC LIMIT ? OFFSET ?"
            param.extend( [casos, (pagina - 1) * casos] )
            bd.execute( consulta_sql, param )
            lista = bd.fetchall()
            conexion.close()

            # Compone y entrega la salida en formato JSON
            resultado = {
				"total": total_registros,
				"paginas": total_paginas,
				"nav": pagina,
                "max": casos,
				"resultados": [
					{
						"id": row[0],
						"alias": row[1],
						"email": row[2],
						"roles": row[3],
						"imagen": row[4],
						"estado": row[5]
					}
					for row in lista
				]
			}
            return resultado

        except Exception as e:
            self.basedatos_registrar.error( f"{e}" )
            return None
        finally:
            if conexion:
                conexion.close()

    # Función para buscar documentos (con filtros) y obtener sus resultados
    def buscar_documentos( self, parametros={}, pagina=1, casos=10 ):
        try:
            conexion = sqlite3.connect( self._BD.get('RECURSOS') )
            consulta_sql = self._SQL.get( 'SELECT_DOCUMENTOS' )
            param = []

            # Compone la sentencia SQL dependiento de los parámetros recibidos
            texto_buscar = parametros.get('texto', None)
            if texto_buscar:
                texto_buscar = self._limpiar_entrada.get( 'texto' )( texto_buscar )
                if self._validar_entrada( texto_buscar ):
                    consulta_sql += " AND ("
                    for texto in texto_buscar:
                        consulta_sql += " AND (UPPER(titulo) LIKE UPPER(?) OR titulo LIKE (?))"
                        param.append( f"%{texto}%" )
                        param.append( f"%{texto}%" )
                    consulta_sql += ")"
                    consulta_sql = str( consulta_sql ).replace(" AND ( AND ", " AND (" )

            estado = parametros.get('estado', None)
            if estado:
                estado = self._limpiar_entrada.get( 'numero' )( estado )
                if self._validar_entrada( estado ):
                    consulta_sql += " AND estado=?"
                    param.append( estado )

            carpeta = parametros.get('carpeta', None)
            if carpeta:
                carpeta = self._limpiar_entrada.get( 'texto' )( carpeta )
                if self._validar_entrada( carpeta ):
                    for texto in carpeta:
                        consulta_sql += " AND carpeta=?"
                        param.append( texto )

            tipo = parametros.get('tipo', None)
            if tipo:
                tipo = self._limpiar_entrada.get( 'texto' )( tipo )
                if self._validar_entrada( tipo ):
                    for texto in tipo:
                        consulta_sql += " AND tipo=?"
                        param.append( texto )

            zona = parametros.get('zona', None)
            if zona:
                zona = self._limpiar_entrada.get( 'texto' )( zona )
                if self._validar_entrada( zona ):
                    for texto in zona:
                        consulta_sql += " AND zona=?"
                        param.append( texto )

            # Ejecuta las consultas SQL y obtiene resultados
            consulta_total = f"SELECT COUNT(*) FROM ({consulta_sql})"
            bd = conexion.cursor()
            bd.execute( consulta_total, param )
            total_registros = bd.fetchone()[0]
            total_paginas = ( total_registros + casos - 1 ) // casos
            consulta_sql += " ORDER BY id DESC LIMIT ? OFFSET ?"
            param.extend( [casos, (pagina - 1) * casos] )
            bd.execute( consulta_sql, param )
            lista = bd.fetchall()
            conexion.close()

            # Compone y entrega la salida en formato JSON
            resultado = {
				"total": total_registros,
				"paginas": total_paginas,
				"nav": pagina,
                "max": casos,
				"resultados": [
					{
						"id": row[0],
						"estado": row[1],
						"archivo": row[2],
						"tipo": row[3],
						"peso": row[4],
						"carpeta": row[5],
						"imagen": row[6],
						"titulo": row[7],
						"resumen": row[8],
						"fechaing": row[9],
						"codigo": row[10],
						"zona": row[11],
						"descargas": row[12]
					}
					for row in lista
				]
			}
            return resultado

        except Exception as e:
            self.basedatos_registrar.error( f"{e}" )
            return None
        finally:
            if conexion:
                conexion.close()

    # Función para recuperar datos y sumar descarga a un documento
    def sumar_documento( self, codigo=None ):
        try:
            if not codigo:
                return None

            conexion = sqlite3.connect( self._BD.get('RECURSOS') )
            consulta_sql = self._SQL.get( 'SELECT_CODIGO_DOCUMENTO' )
            parametros = [ codigo ]
            bd = conexion.cursor()
            bd.execute( consulta_sql, parametros )
            datos = bd.fetchone()
            if not datos:
                return None

            columnas = [desc[0] for desc in bd.description]
            caso = {columnas[i]: datos[i] for i in range(len(columnas))}
            id_doc = datos[0]
            consulta_sql = self._SQL.get( 'UPDATE_DESCARGA_DOCUMENTO' )
            parametros = [ 
                int(id_doc)
            ]
            bd = conexion.cursor()
            bd.execute( consulta_sql, parametros )
            conexion.commit()
            conexion.close()
            return caso
        except Exception as e:
            self.basedatos_registrar.error( f"{e}" )
            return None
        finally:
            if conexion:
                conexion.close()

    # Función para crear un nuevo usuario
    def agregar_usuario( self, parametros={} ):
        uid = 0
        estado = 1
        try:
            param = [ int(estado) ]
            campos = ''
            valores = ''

            alias = parametros.get('alias', None)
            if alias:
                param.append( alias )
                campos = f"{campos}, alias"
                valores = f"{valores},?"

            email = parametros.get('email', None)
            if email:
                param.append( email )
                campos = f"{campos}, email"
                valores = f"{valores},?"

            roles = parametros.get('roles', None)
            if roles:
                param.append( roles )
                campos = f"{campos}, roles"
                valores = f"{valores},?"

            clave = parametros.get('clave', None)
            if clave:
                param.append( clave )
                campos = f"{campos}, clave"
                valores = f"{valores},?"

            consulta_sql = self._SQL.get( 'INSERT_USUARIO' )
            consulta_sql = str(consulta_sql).replace('{campos}', campos).replace('{valores}', valores)

            conexion = sqlite3.connect( self._BD.get('USUARIOS') )
            bd = conexion.cursor()
            bd.execute( consulta_sql, param )
            conexion.commit()
            uid = bd.lastrowid
            conexion.close()
            return uid
        except Exception as e:
            self.basedatos_registrar.error( f"{e}" )
            return uid
        finally:
            if conexion:
                conexion.close()

    # Función para obtener los datos de un usuario
    def abrir_usuario( self, uid=0 ):
        try:
            conexion = sqlite3.connect( self._BD.get('USUARIOS') )
            consulta_sql = self._SQL.get( 'SELECT_USUARIO' )
            parametros = [ uid ]
            bd = conexion.cursor()
            bd.execute( consulta_sql, parametros )
            datos = bd.fetchone()
            conexion.close()
            if datos:
                columnas = [desc[0] for desc in bd.description]
                caso = {columnas[i]: datos[i] for i in range(len(columnas))}
                return caso
            else:
                return None
        except sqlite3.Error as e:
            self.basedatos_registrar.error( f"{e}" )
            return None
        finally:
            if conexion:
                conexion.close()

    # Función para actualizar los datos de un usuario
    def actualizar_usuario( self, uid=0, parametros={} ):
        try:
            param = []
            campos = ''

            alias = parametros.get('alias', None)
            if alias:
                param.append( alias )
                campos = f"{campos}, alias=?"

            roles = parametros.get('roles', None)
            if roles:
                param.append( roles )
                campos = f"{campos}, roles=?"

            estado = parametros.get('estado', None)
            if estado:
                param.append( int(estado) )
                campos = f"{campos}, estado=?"

            clave = parametros.get('clave', None)
            if clave:
                param.append( clave )
                campos = f"{campos}, clave=?"

            param.append( uid )
            consulta_sql = self._SQL.get( 'UPDATE_USUARIO' )
            consulta_sql = str(consulta_sql).replace( "{campos}", campos )

            conexion = sqlite3.connect( self._BD.get('USUARIOS') )
            bd = conexion.cursor()
            bd.execute( consulta_sql, param )
            conexion.commit()
            conexion.close()
            return True
        except Exception as e:
            self.basedatos_registrar.error( f"{e}" )
            return False
        finally:
            if conexion:
                conexion.close()

    # Función para borrar un usuario
    def borrar_usuario( self, uid=0 ):
        try:
            param = [ uid ]
            consulta_sql = self._SQL.get( 'DELETE_USUARIO' )
            conexion = sqlite3.connect( self._BD.get('USUARIOS') )
            bd = conexion.cursor()
            bd.execute( consulta_sql, param )
            conexion.commit()
            conexion.close()
            return True
        except Exception as e:
            self.basedatos_registrar.error( f"{e}" )
            return False
        finally:
            if conexion:
                conexion.close()

    # Función para borrar un documento
    def borrar_documento( self, id_doc=0 ):
        try:
            param = [ id_doc ]
            consulta_sql = self._SQL.get( 'DELETE_DOCUMENTO' )
            conexion = sqlite3.connect( self._BD.get('RECURSOS') )
            bd = conexion.cursor()
            bd.execute( consulta_sql, param )
            conexion.commit()
            conexion.close()
            return True
        except Exception as e:
            self.basedatos_registrar.error( f"{e}" )
            return False
        finally:
            if conexion:
                conexion.close()

    # Función para borrar los documentos de una carpeta
    def borrar_documentos( self, carpeta ):
        try:
            param = [ carpeta ]
            consulta_sql = self._SQL.get( 'DELETE_DOCUMENTOS' )
            conexion = sqlite3.connect( self._BD.get('RECURSOS') )
            bd = conexion.cursor()
            bd.execute( consulta_sql, param )
            conexion.commit()
            conexion.close()
            return True
        except Exception as e:
            self.basedatos_registrar.error( f"{e}" )
            return False
        finally:
            if conexion:
                conexion.close()

    # Función para verificar si un e-mail ya está registrado
    def verificar_email( self, email ):
        try:
            conexion = sqlite3.connect( self._BD.get('USUARIOS') )
            consulta_sql = self._SQL.get( 'SELECT_CONTAR_USUARIO' )
            parametros = [ email ]
            bd = conexion.cursor()
            bd.execute( consulta_sql, parametros )
            datos = bd.fetchone()
            conexion.close()
            if datos[0] > 0:
                return True
        except sqlite3.Error as e:
            self.basedatos_registrar.error( f"{e}" )
            return None
        finally:
            if conexion:
                conexion.close()
        return False

    # Función para obtener resumen de las carpetas con documentos
    def resumen_carpetas( self ):
        try:
            conexion = sqlite3.connect( self._BD.get('RECURSOS') )
            consulta_sql = self._SQL.get( 'RESUMEN_CARPETAS' )
            bd = conexion.cursor()
            bd.execute( consulta_sql )
            datos = bd.fetchall()
            conexion.close()
            columnas = [desc[0] for desc in bd.description]
            lista = []
            if datos:
                for registro in datos:
                    caso = {columnas[i]: registro[i] for i in range(len(columnas))}
                    lista.append(caso)
            return lista
        except sqlite3.Error as e:
            self.basedatos_registrar.error( f"{e}" )
            return []
        finally:
            if conexion:
                conexion.close()

    # Función para obtener lista de documentos que se pueden consultar
    def documentos_consultables( self ):
        try:
            conexion = sqlite3.connect( self._BD.get('RECURSOS') )
            consulta_sql = self._SQL.get( 'SELECT_DOC_CONSULTABLES' )
            bd = conexion.cursor()
            bd.execute( consulta_sql )
            datos = bd.fetchall()
            conexion.close()
            columnas = [desc[0] for desc in bd.description]
            lista = []
            if datos:
                for registro in datos:
                    caso = {columnas[i]: registro[i] for i in range(len(columnas))}
                    lista.append(caso)
            return lista
        except sqlite3.Error as e:
            self.basedatos_registrar.error( f"{e}" )
            return []
        finally:
            if conexion:
                conexion.close()

    # Función para obtener historial de interacciones de un usuario
    def interacciones_usuario( self, filtro=None ):
        if not filtro:
            return []
        try:
            conexion = sqlite3.connect( self._BD.get('LOGS') )
            consulta_sql = self._SQL.get( 'SELECT_INTERACCIONES_USUARIO' )
            param = [ filtro ]
            bd = conexion.cursor()
            bd.execute( consulta_sql, param )
            datos = bd.fetchall()
            conexion.close()
            columnas = [desc[0] for desc in bd.description]
            lista = []
            if datos:
                for registro in datos:
                    caso = {columnas[i]: registro[i] for i in range(len(columnas))}
                    lista.append(caso)
            return lista
        except sqlite3.Error as e:
            self.basedatos_registrar.error( f"{e}" )
            return []
        finally:
            if conexion:
                conexion.close()

    # Función para borrar interacciones e historial de un usuario
    def borrar_historiales( self, uuid ):
        try:
            param = [ uuid ]
            conexion = sqlite3.connect( self._BD.get('LOGS') )
            consulta_sql = self._SQL.get( 'DELETE_HISTORIAL' )
            bd = conexion.cursor()
            bd.execute( consulta_sql, param )
            conexion.commit()
            consulta_sql = self._SQL.get( 'DELETE_INTERACCIONES' )
            bd = conexion.cursor()
            bd.execute( consulta_sql, param )
            conexion.commit()
            conexion.close()
            return True
        except Exception as e:
            self.basedatos_registrar.error( f"{e}" )
            return False
        finally:
            if conexion:
                conexion.close()

    # Función para extraer documentos dada una lista de archivos
    def extraer_documentos( self, listado=[], total=10 ):
        try:
            conexion = sqlite3.connect( self._BD.get('RECURSOS') )
            reemplazar = ','.join(['?'] * len(listado))
            consulta_sql = self._SQL.get( 'SELECT_NOMBRE_DOCUMENTOS' )
            consulta_sql = str(f"{consulta_sql} LIMIT {total}").format(reemplazar)

            # Ejecuta la consulta SQL y obtiene resultados
            bd = conexion.cursor()
            bd.execute( consulta_sql, listado )
            datos = bd.fetchall()
            conexion.close()
            columnas = [desc[0] for desc in bd.description]
            lista = []
            if datos:
                for registro in datos:
                    caso = {columnas[i]: registro[i] for i in range(len(columnas))}
                    lista.append(caso)
            return lista

        except Exception as e:
            self.basedatos_registrar.error( f"{e}" )
            return []
        finally:
            if conexion:
                conexion.close()

    # Función para exportar metadatos de documentos
    def exportar_metadatos( self, carpeta ):
        try:
            param = [ carpeta ]
            conexion = sqlite3.connect( self._BD.get('RECURSOS') )
            consulta_sql = self._SQL.get( 'SELECT_EXPORTAR_METADATOS' )
            bd = conexion.cursor()
            bd.execute( consulta_sql, param )
            datos = bd.fetchall()
            conexion.close()
            columnas = [desc[0] for desc in bd.description]
            lista = []
            if datos:
                for registro in datos:
                    caso = {columnas[i]: registro[i] for i in range(len(columnas))}
                    lista.append(caso)
            return lista
        except sqlite3.Error as e:
            self.basedatos_registrar.error( f"{e}" )
            return []
        finally:
            if conexion:
                conexion.close()

    # Función para importar metadatos de documentos
    def importar_metadatos( self, parametros={} ):
        try:
            campos = ''
            param = []
            titulo = parametros.get('titulo', None)
            if titulo:
                param.append( titulo )
                campos = f"{campos}, titulo=?"
            carpeta = parametros.get('carpeta', None)
            if carpeta:
                param.append( carpeta )
                campos = f"{campos}, carpeta=?"
            autores = parametros.get('autores', None)
            if autores:
                param.append( autores )
                campos = f"{campos}, autores=?"
            fechapub = parametros.get('fechapub', None)
            if fechapub:
                param.append( fechapub )
                campos = f"{campos}, fechapub=?"
            resumen = parametros.get('resumen', None)
            if resumen:
                param.append( resumen )
                campos = f"{campos}, resumen=?"
            sugerencias = parametros.get('sugerencias', None)
            if sugerencias:
                param.append( sugerencias )
                campos = f"{campos}, sugerencias=?"
            zona = parametros.get('zona', None)
            if zona:
                param.append( zona )
                campos = f"{campos}, zona=?"
            id = parametros.get('id', None)
            if id:
                param.append( id )

            conexion = sqlite3.connect( self._BD.get('RECURSOS') )
            consulta_sql = self._SQL.get( 'UPDATE_METADATOS_DOCUMENTO' )
            consulta_sql = str(consulta_sql).replace( "{campos}", campos )
            bd = conexion.cursor()
            bd.execute( consulta_sql, param )
            conexion.commit()
            conexion.close()
            return True
        except sqlite3.Error as e:
            self.basedatos_registrar.error( f"{e}" )
            return False
        finally:
            if conexion:
                conexion.close()

    # Función para obtener listas de documentos destacados
    def documentos_destacados( self, total, carpetas=[] ):
        try:
            reemplazar = ','.join(['?'] * len(carpetas))
            conexion = sqlite3.connect( self._BD.get('RECURSOS') )
            bd = conexion.cursor()

            # Ejecuta las consultas SQL y obtiene sus resultados
            consulta_sql = self._SQL.get( 'SELECT_DOC_RECIENTES' )
            consulta_sql = str(f"{consulta_sql} LIMIT {total}").format(reemplazar)
            bd.execute( consulta_sql, carpetas )
            datos1 = bd.fetchall()
            columnas1 = [desc[0] for desc in bd.description]
            consulta_sql = self._SQL.get( 'SELECT_DOC_POPULARES' )
            consulta_sql = str(f"{consulta_sql} LIMIT {total}").format(reemplazar)
            bd.execute( consulta_sql, carpetas )
            datos2 = bd.fetchall()
            columnas2 = [desc[0] for desc in bd.description]
            conexion.close()
            recientes = []
            if datos1:
                for registro in datos1:
                    caso = {columnas1[i]: registro[i] for i in range(len(columnas1))}
                    recientes.append(caso)
            populares = []
            if datos2:
                for registro in datos2:
                    caso = {columnas2[i]: registro[i] for i in range(len(columnas2))}
                    populares.append(caso)
            lista = { "recientes": recientes, "populares": populares }
            return lista

        except Exception as e:
            self.basedatos_registrar.error( f"{e}" )
            return {}
        finally:
            if conexion:
                conexion.close()


######################################################
# FUNCIONES PRIVADAS
######################################################

    def _limpiar_texto( self, texto ):
        minimo = 3
        maximo = 25
        excluir = '\\|"\'#$%&/{};:_<>*¿?°ºª~¡!=+[],.'
        texto = str( texto )
        if len( texto ) < minimo:
            return None

        # Elimina caracteres especiales no deseados
        for char in excluir:
            texto = texto.replace( char, '' )

        # Quita saltos de línea y reemplaza dobles espacios por espacios simples
        texto = texto.replace( '\n', ' ' ).replace( '\r', '' )
        texto = re.sub( r'\s{2,}', ' ', texto )

        # Sanitiza el texto para consultas SQL
        texto = re.sub( r"[\x00\x0A\x0D\x1A\x22\x27\x5C]", lambda m: '\\' + m.group(0), texto )

        # Limita el texto al máximo de caracteres, cortando antes de la última palabra
        if len( texto ) > maximo:
            texto = texto[:maximo].rsplit(' ', 1)[0]

        # Verifica que el texto tenga el mínimo de caracteres
        if len( texto ) < minimo:
            return None

        # Separa el texto en palabras y devuelve una lista
        lista = texto.split()
        return lista

    def _limpiar_fecha( self, fecha ):
        import datetime
        formatos = [ '%d-%m-%Y','%Y-%m-%d' ]
        fecha_valida = None
        for formato in formatos:
            try:
                fecha = datetime.datetime.strptime( fecha, formato )
                fecha_valida = fecha
                break
            except ValueError:
                pass
        if fecha_valida:
            resultado = str( fecha_valida.strftime('%d/%m/%Y') )
            return resultado
        else:
            return ''

    def _limpiar_numero( self, numero ):
        from decimal import Decimal, InvalidOperation

        decimales = 2
        minimo = 0
        maximo = float('inf')
        numero = str( numero ).replace(',', '.').strip()

        # Verifica que solo haya un punto numero.
        if len(re.findall( r'\.', numero )) > 1:
            return ''
        try:
            num = Decimal( numero )
        except InvalidOperation:
            return ''

        # Verifica que el número esté en el rango permitido.
        if not ( minimo <= num <= maximo ):
            return ''

        # Redondea el número, si es entero, lo convierte a un entero sin decimales.
        num = num.quantize( Decimal(10) ** -decimales )
        if num == num.to_integral():
            num = num.to_integral()

        # Convierte el número a un string con punto decimal y lo entrega.
        numero = str( num )
        return numero
 
    def _validar_entrada( self, entrada ):
        resultado = False
        if ( entrada and entrada is not None and entrada != 'None' and entrada != '' ):
            resultado = True
        return resultado

    def _cargar_configuracion( self ):
        import json, os
        try:
            ruta_archivo = f"{self.config.RUTA.get('CONFIG')}/basedatos.json"
            if not os.path.isfile( ruta_archivo ):
                ruta_archivo = f"{self.config.RUTA.get('SISTEMA')}/basedatos.json"
                if not os.path.isfile( ruta_archivo ):
                    return {}
            with open( ruta_archivo, 'r', encoding='utf-8' ) as f:
                datos = json.load( f )
                return datos
        except Exception as e:
            self.basedatos_registrar.error( f"{e}" )

        return {}
