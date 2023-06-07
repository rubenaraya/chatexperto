# almacenes.py
from langchain.docstore.document import Document
from registros import configurar_logger
from archivos import Archivos
from typing import List

class Almacenes:

    def __init__( self, config=None, almacen_indice=None ):
        
        # Manejador de registros
        self.almacenes_registrar = configurar_logger( "almacenes", "almacenes.log" )
        self.config = config

        # Configuración del almacén basada en parámetro de inicialización
        if not almacen_indice:
            almacen_indice = "LOCAL"
        self.CFG = self._cargar_configuracion( almacen_indice = almacen_indice )

        # Propiedades
        self.INDICE = None

########################################################
# FUNCIONES PUBLICAS
########################################################

    # Función para cargar documentos de una carpeta local y extraer sus textos
    def cargar_documentos( self, metodo="Generico", archivo=None ):
        try:
            # Configuración de rutas
            archivos = Archivos(self.config)
            ruta_archivos = archivos.obtener_ruta( tipo_recurso="ARCHIVOS" )

            # si metodo es Generico
            if metodo == "Generico":
                loader = self._cargar_documentos_generico( ruta_archivos=ruta_archivos, archivo=archivo )

            elif metodo == "Diferenciado":
                loader = self._cargar_documentos_diferenciado( ruta_archivos=ruta_archivos, archivo=archivo )

            else:
                loader = None

            # Realiza la extracción del texto de los documentos y los devuelve en un List[Document]
            if loader:
                if isinstance( loader, list ):
                    documentos = []
                    for doc in loader:
                        documento = doc.load()
                        documentos.extend( documento )
                else:
                    documentos = loader.load()
                return documentos

        except Exception as e:
            self.almacenes_registrar.error( f"{e}" )

        return None

    # Función para pre-procesar los textos y metadatos de los documentos cargados
    def procesar_documentos( self, documentos=None, metodo="Basico", que_procesar="metadatos" ):
        if documentos and metodo == 'Basico':
            documentos = self._procesar_documentos_basico( documentos=documentos, que_procesar=que_procesar )
        
        return documentos

    # Función para dividir en trozos los textos procesados de los documentos
    def dividir_documentos( self, documentos=None, metodo="Recursivo", trozo="500" ):
        texto_trozado = None
        if documentos:
            
            if metodo == 'Simple':
                texto_trozado = self._dividir_documentos_simple( documentos=documentos, trozo=trozo )

            elif metodo == 'Recursivo':
                texto_trozado = self._dividir_documentos_recursivo( documentos=documentos, trozo=trozo )

        return texto_trozado

    # Función para asignar valores a la configuración de un indice vectorial
    def configurar_indice( self, parametros ):
        try:
            for variable, valor in parametros:
                if variable in self.CFG:
                    self.CFG[variable] = valor
        except Exception as e:
            self.almacenes_registrar.error( f"{e}" )
            raise e

    # Función para crear y almacenar un nuevo índice vectorial con los documentos divididos
    def crear_indice( self, documentos=None, api_emb=None, id_doc=0 ):

        if self.CFG.get('_uid') == 'LOCAL' or self.CFG.get('_uid') == 'FAISS':
            return self._crear_indice_faiss( documentos=documentos, api_emb=api_emb, id_doc=id_doc )

        elif self.CFG.get('_uid') == 'MILVUS':
            return self._crear_indice_milvus( documentos=documentos, api_emb=api_emb, id_doc=id_doc )

        elif self.CFG.get('_uid') == 'PINECONE':
            return self._crear_indice_pinecone( documentos=documentos, api_emb=api_emb, id_doc=id_doc )

        elif self.CFG.get('_uid') == 'QDRANT':
            return self._crear_indice_qdrant( documentos=documentos, api_emb=api_emb, id_doc=id_doc )

        elif self.CFG.get('_uid') == 'REDIS':
            return self._crear_indice_redis( documentos=documentos, api_emb=api_emb, id_doc=id_doc )

        elif self.CFG.get('_uid') == 'WEAVIATE':
            return self._crear_indice_weaviate( documentos=documentos, api_emb=api_emb, id_doc=id_doc )

        elif self.CFG.get('_uid') == 'CHROMA':
            return self._crear_indice_chroma( documentos=documentos, api_emb=api_emb, id_doc=id_doc )

        return False

    # Función para combinar índices de múltiples archivos en un índice de carpeta
    def combinar_indices( self, nombre_indice, api_emb=None ):

        if self.CFG.get('_uid') == 'LOCAL' or self.CFG.get('_uid') == 'FAISS':
            return self._combinar_indices_faiss( nombre_indice=nombre_indice, api_emb=api_emb )

        elif self.CFG.get('_uid') == 'MILVUS':
            return False

        elif self.CFG.get('_uid') == 'PINECONE':
            return False

        elif self.CFG.get('_uid') == 'QDRANT':
            return False

        elif self.CFG.get('_uid') == 'REDIS':
            return False

        elif self.CFG.get('_uid') == 'WEAVIATE':
            return False

        elif self.CFG.get('_uid') == 'CHROMA':
            return False

        return False

    # Función para abrir un índice vectorial existente
    def cargar_indice( self, api_emb=None, id_doc=0 ):
        self.INDICE = None

        if self.CFG.get('_uid') == 'LOCAL':
            self._cargar_indice_faiss( api_emb=api_emb, id_doc=id_doc )

        elif self.CFG.get('_uid') == 'MILVUS':
            self._cargar_indice_milvus( api_emb=api_emb, id_doc=id_doc )

        elif self.CFG.get('_uid') == 'PINECONE':
            self._cargar_indice_pinecone( api_emb=api_emb, id_doc=id_doc )

        elif self.CFG.get('_uid') == 'QDRANT':
            self._cargar_indice_qdrant( api_emb=api_emb, id_doc=id_doc )

        elif self.CFG.get('_uid') == 'REDIS':
            self._cargar_indice_redis( api_emb=api_emb, id_doc=id_doc )

        elif self.CFG.get('_uid') == 'WEAVIATE':
            self._cargar_indice_weaviate( api_emb=api_emb, id_doc=id_doc )

        elif self.CFG.get('_uid') == 'CHROMA':
            self._cargar_indice_chroma( api_emb=api_emb, id_doc=id_doc )

        return self.INDICE

    # Función para borrar un índice vectorial existente
    def borrar_indice( self, id_doc=0 ):

        if self.CFG.get('_uid') == 'LOCAL':
            return self._borrar_indice_faiss( id_doc=id_doc )

        return False

    # Función para guardar datos en un archivo Excel
    def guardar_excel( self, nombre, datos, directorio ):
        import pandas as pd
        try:
            if nombre and datos and directorio:
                archivos = Archivos(self.config)
                ruta_archivos = archivos.obtener_ruta( tipo_recurso=directorio )
                archivo_excel = f"{ruta_archivos}/{nombre}"
                df = pd.DataFrame( datos )
                df.to_excel( archivo_excel, index=False )
                return ruta_archivos
        except Exception as e:
            self.almacenes_registrar.error( f"{e}" )
        return None

    # Función para leer datos desde un archivo Excel
    def leer_excel( self, nombre, directorio ):
        import pandas as pd
        try:
            if nombre and directorio:
                archivos = Archivos(self.config)
                ruta_archivos = archivos.obtener_ruta( tipo_recurso=directorio )
                archivo_excel = f"{ruta_archivos}/{nombre}"
                df = pd.read_excel( archivo_excel )
                df = df.fillna('')
                return df.to_dict( orient='records' )
        except Exception as e:
            self.almacenes_registrar.error( f"{e}" )
        return None


########################################################
# FUNCION PARA COMPATIBILIDAD CON RETRIEVERS
########################################################

    def get_relevant_documents( self, query: str ) -> List[Document]:
        if not self.INDICE:
            return None

        textos_encontrados = self.INDICE.similarity_search( query=query, k=4 )
        if textos_encontrados:
            return textos_encontrados
        return None


########################################################
# FUNCIONES PRIVADAS
########################################################

    def _obtener_extension( self, nombre_archivo ):

        # Dividir el nombre del archivo en partes usando el punto como separador
        partes = nombre_archivo.split('.')

        # Si solo hay una parte (no hay puntos), entonces no hay extensión y devuelve una cadena vacía
        if len( partes ) == 1:
            return ""

        # Si hay más de una parte, devuelve la última parte, que corresponde a la extensión
        return partes[-1]

    def _cargar_configuracion( self, almacen_indice: str="" ):
        import json, os
        try:
            ruta_archivo = f"{self.config.RUTA.get('CONFIG')}/almacenes.json"
            if not os.path.isfile( ruta_archivo ):
                ruta_archivo = f"{self.config.RUTA.get('SISTEMA')}/almacenes.json"
                if not os.path.isfile( ruta_archivo ):
                    return {}
            with open( ruta_archivo, 'r', encoding='utf-8' ) as f:
                datos = json.load( f )
            for fila in datos:
                if fila.get('_uid') == almacen_indice:
                    return fila

        except Exception as e:
            self.almacenes_registrar.error( f"{e}" )

        return {}

    def _cargar_documentos_generico( self, ruta_archivos=None, archivo=None ):
        from langchain.document_loaders import DirectoryLoader, UnstructuredFileLoader

        loader = None
        try:
            # Si se recibió un nombre de archivo, lo carga si existe
            if archivo:
                ruta = f"{ruta_archivos}/{archivo}"
                loader = UnstructuredFileLoader( file_path = ruta, mode = "elements")

            # Si no se solicitó archivo, carga el directorio completo
            else:
                loader = DirectoryLoader( path = ruta_archivos, silent_errors = True, recursive = False )

        except Exception as e:
            self.almacenes_registrar.error( f"{e}" )
            loader = None

        return loader

    def _cargar_documentos_diferenciado( self, ruta_archivos=None, archivo=None ):
        from langchain.document_loaders import Docx2txtLoader
        from langchain.document_loaders.csv_loader import CSVLoader
        from langchain.document_loaders import UnstructuredPowerPointLoader
        from langchain.document_loaders import PyMuPDFLoader
        from langchain.document_loaders import TextLoader
        from langchain.document_loaders import SRTLoader
        from langchain.document_loaders import UnstructuredHTMLLoader

        loader = None
        try:
            # Si se especificó un archivo, lo carga como documento
            if archivo:
                ruta = f"{ruta_archivos}/{archivo}"
                extension = self._obtener_extension( nombre_archivo=archivo )
                if extension == "pdf":
                    loader = PyMuPDFLoader( file_path=ruta )
                elif extension == "docx":
                    loader = Docx2txtLoader( file_path=ruta )
                elif extension == "pptx":
                    loader = UnstructuredPowerPointLoader( file_path=ruta )
                elif extension == "csv":
                    loader = CSVLoader( file_path=ruta, encoding="utf8" )
                elif extension == "txt":
                    loader = TextLoader( file_path=ruta, encoding="utf8" )
                elif extension == "html":
                    loader = UnstructuredHTMLLoader( file_path=ruta )
                elif extension == "srt":
                    loader = SRTLoader( file_path=ruta)
                elif extension == "xlsx":
                    loader = self._convertir_cargar_excel( ruta_archivos=ruta_archivos, archivo=archivo )

            # Si no se solicitó archivo, carga el directorio completo como documentos diferenciados
            else:
                cargadores = []
                for extension in self.config.TIPOS_ARCHIVO:
                    archivos = Archivos(self.config)
                    lista_archivos = archivos.obtener_lista_archivos( extension=extension, ruta=ruta_archivos )
                    for archivo in lista_archivos:
                        ruta = f"{ruta_archivos}/{archivo}.{extension}"
                        loader = None
                        if extension == "pdf":
                            loader = PyMuPDFLoader( file_path=ruta )
                        elif extension == "docx":
                            loader = Docx2txtLoader( file_path=ruta )
                        elif extension == "pptx":
                            loader = UnstructuredPowerPointLoader( file_path=ruta )
                        elif extension == "csv":
                            loader = CSVLoader( file_path=ruta, encoding="utf8" )
                        elif extension == "txt":
                            loader = TextLoader( file_path=ruta, encoding="utf8" )
                        elif extension == "html":
                            loader = UnstructuredHTMLLoader( file_path=ruta )
                        elif extension == "srt":
                            loader = SRTLoader( file_path=ruta)
                        elif extension == "xlsx":
                            loader = self._convertir_cargar_excel( ruta_archivos=ruta_archivos, archivo=f"{archivo}.{extension}" )
                        
                        if loader:
                            cargadores.append( loader )

                if len(cargadores) > 0:
                    loader = cargadores

        except Exception as e:
            self.almacenes_registrar.error( f"{e}" )
            loader = None

        return loader

    def _convertir_cargar_excel( self, ruta_archivos=None, archivo=None ):
        from langchain.document_loaders import CSVLoader
        import pandas

        loader = None
        try:
            archivos = Archivos(self.config)
            ruta_temp = archivos.obtener_ruta( tipo_recurso='TEMP' )
            ruta_extraido = f"{ruta_temp}/extraido"
            archivos.crear_carpeta( ruta=ruta_extraido )

            # Si se recibió un nombre de archivo, lo agrega a la lista
            lista_archivos = []
            if archivo:
                nombre_archivo = str(archivo).removesuffix('.xlsx')
                lista_archivos = [ nombre_archivo ]

            # Si no se solicitó archivo, se cargan todos los .XLSX que hay en el directorio
            else:
                # Obtiene la lista de archivos .XLSX que hay en ruta_archivos
                lista_archivos = archivos.obtener_lista_archivos( 'xlsx', ruta_archivos )

            # Convierte cada archvo XLSX de la lista a CSV y lo almacena en "ruta_extraido"
            for ar in lista_archivos:
                origen_xlsx = f"{ruta_archivos}/{ar}.xlsx"
                destino_csv = f"{ruta_extraido}/{ar}.csv"
                xslx = pandas.read_excel( origen_xlsx )
                xslx.to_csv(
                    path_or_buf = destino_csv, 
                    index = False, 
                    header = True, 
                    quoting = 1
                )

            datos = pandas.DataFrame()
            if archivo:
                # Convierte el archivo CSV extraido de utf-8 a cp1252 y lo abre en un cargador
                nombre_archivo = str(archivo).removesuffix('.xlsx')
                origen_csv = f"{ruta_extraido}/{nombre_archivo}.csv"
                temporal = pandas.read_csv( origen_csv, encoding='utf-8' )
                datos = pandas.concat( [datos, temporal], axis=0 )
                archivo_convertido = f"{ruta_extraido}/{nombre_archivo}.csv"
                datos.to_csv( archivo_convertido, index=False, header=True, quoting=1, encoding='cp1252' )
                loader = CSVLoader( file_path=archivo_convertido, encoding='cp1252' )

            else:
                # Obtiene la lista de archivos CSV que hay almacenados en "ruta_extraido"
                lista_archivos = archivos.obtener_lista_archivos( 'csv', ruta_extraido )

                # Crea un consolidado de textos extraidos con todos los archivos CSV
                for ar in lista_archivos:
                    origen_csv = f"{ruta_extraido}/{ar}.csv"
                    temporal = pandas.read_csv( origen_csv, encoding='utf-8' )
                    datos = pandas.concat( [datos, temporal], axis=0 )

                # Guarda el consolidado en un archivo CSV y lo vuelve a abrir en un cargador (en codificación cp1252)
                archivo_consolidado = f"{ruta_temp}/xlsx_consolidado_textos_extraidos-{self.config.CARPETA}.csv"
                datos.to_csv( archivo_consolidado, index=False, header=True, quoting=1, encoding='cp1252' )
                loader = CSVLoader( file_path=archivo_consolidado, encoding='cp1252' )

        except Exception as e:
            self.almacenes_registrar.error( f"{e}" )
            loader = None

        return loader

    def _procesar_documentos_basico( self, documentos=None, que_procesar=None ):
        import re

        try:
            for doc in documentos:

                if que_procesar in [ "todo", "contenido" ]:
                    # Efectúa limpieza en Document[page_content]
                    page_content = str(doc.page_content)
                    page_content = re.sub( r"(\w+)-\n(\w+)", "\1\2", page_content )
                    page_content = re.sub( r"(?<!\n\s)\n(?!\s\n)", " ", page_content.strip() )
                    page_content = re.sub( r"\n\s*\n", "\n\n", page_content )
                    page_content = page_content.replace( "\t", " " )
                    page_content = page_content.replace( "\\\\", "/" )
                    page_content = page_content.replace( "  ", " " ).replace( "  ", " " ).replace( "  ", " " ).replace( "  ", " " ).replace( "  ", " " )
                    page_content = page_content.replace( "…", "." ).replace( "…", "." ).replace( "…", "." ).replace( "…", "." ).replace( "…", "." )
                    page_content = page_content.replace( "...", "." ).replace( "...", "." ).replace( "...", "." ).replace( "...", "." ).replace( "...", "." )
                    page_content = page_content.replace( "___", "_" ).replace( "___", "_" ).replace( "___", "_" ).replace( "___", "_" ).replace( "___", "_" )
                    doc.page_content = page_content

                if que_procesar in [ "todo", "metadatos" ]:
                    # Efectúa limpieza y asignaciones en Document[metadata]
                    metadata = doc.metadata
                    source = metadata.get('source')
                    source = str( source ).replace( "\\", "/" )
                    partes = source.split('/')
                    if len(partes) == 1:
                        filename = ''
                    else:
                        filename = partes[-1]
                    doc.metadata['source'] = source
                    doc.metadata['filename'] = filename
                    doc.metadata['category'] = self.config.CARPETA

        except Exception as e:
            self.almacenes_registrar.error( f"{e}" )

        return documentos

    def _dividir_documentos_simple( self, documentos=None, trozo="0" ):
        from langchain.text_splitter import CharacterTextSplitter
        
        texto_trozado = None
        try:
            divisor_texto = CharacterTextSplitter(
                chunk_size = int(trozo),
                chunk_overlap = (int(trozo) / 10)
            )
            texto_trozado = divisor_texto.split_documents( documentos )

        except Exception as e:
            self.almacenes_registrar.error( f"{e}" )

        return texto_trozado

    def _dividir_documentos_recursivo( self, documentos=None, trozo="0" ):
        from langchain.text_splitter import RecursiveCharacterTextSplitter

        texto_trozado = None
        try:
            divisor_texto = RecursiveCharacterTextSplitter(
                chunk_size = int(trozo),
                chunk_overlap = (int(trozo) / 10),
                length_function = len
                #separators = [ "\n\n", "\n", ".", "!", "?", ",", " ", "" ]
            )
            texto_trozado = divisor_texto.split_documents( documentos )

        except Exception as e:
            self.almacenes_registrar.error( f"{e}" )

        return texto_trozado

########################################################
# FUNCIONES PARA DIFERENTES ALMACENES DE VECTORES
########################################################

    # FAISS
    def _crear_indice_faiss( self, documentos=None, api_emb=None, id_doc=0 ):
        from langchain.vectorstores.faiss import FAISS
        try:
            # Configuración de rutas y nombres
            if len( self.CFG.get('ruta_indice') ) == 0:
                archivos = Archivos(self.config)
                self.CFG['ruta_indice'] = archivos.obtener_ruta( tipo_recurso="INDICES" )

            if not id_doc:
                id_doc = 0
            if int(id_doc) > 0:
                self.CFG['id_indice'] = str( id_doc ).zfill( 4 )

            # Crea un indice FAISS con los textos trozados y la API de embeddings y lo almacena en el disco local
            self.INDICE = FAISS.from_documents( documentos, api_emb )
            self.INDICE.save_local( self.CFG.get('ruta_indice'), self.CFG.get('id_indice') )
            """
            TODO: Este fragmento de código no funciona (igual caso que en "_combinar_indices_faiss"), ya que los índies deben ser IndexFlatL2
            # Si se creó un índice de documento, lo agrega al índice de la carpeta
            if int(id_doc) > 0:
                ruta_indice_carpeta = f"{self.CFG.get('ruta_indice')}/index.faiss"
                if archivos.comprobar_archivo( ruta=ruta_indice_carpeta ):
                    local_db = FAISS.load_local(
                        folder_path = self.CFG.get('ruta_indice'),
                        embeddings = api_emb,
                        index_name = 'index'
                    )
                    local_db.merge_from(self.INDICE)
                    local_db.save_local( self.CFG.get('ruta_indice'), 'index' )
                else:
                    self.INDICE.save_local( self.CFG.get('ruta_indice'), 'index' )
            """
            return True

        except Exception as e:
            self.almacenes_registrar.error( f"{e}" )

        return False

    def _cargar_indice_faiss( self, api_emb=None, id_doc=0 ):
        from langchain.vectorstores.faiss import FAISS
        try:
            # Configuración de rutas y nombres
            if int(id_doc) > 0:
                self.CFG['id_indice'] = str( id_doc ).zfill( 4 )

            if len( self.CFG.get('ruta_indice') ) == 0:
                archivos = Archivos(self.config)
                self.CFG['ruta_indice'] = archivos.obtener_ruta( tipo_recurso="INDICES" )
            
            # Comrueba si existe el índice
            comprobar = f"{self.CFG.get('ruta_indice')}/{self.CFG.get('id_indice')}.faiss"
            if not archivos.comprobar_archivo( ruta=comprobar ):
                return False

            # Comprueba si se asignó API de embeddings, si es así carga el índice
            if api_emb:
                self.INDICE = FAISS.load_local( 
                    folder_path = self.CFG.get('ruta_indice'), 
                    embeddings = api_emb, 
                    index_name = self.CFG['id_indice'] 
                )
                return True

        except Exception as e:
            self.almacenes_registrar.error( f"{e}" )

        return False

    def _borrar_indice_faiss( self, id_doc=0 ):
        try:
            # Configuración de rutas y nombres
            if int(id_doc) > 0:
                self.CFG['id_indice'] = str( id_doc ).zfill( 4 )
                archivos = Archivos(self.config)

                if len( self.CFG.get('ruta_indice') ) == 0:
                    self.CFG['ruta_indice'] = archivos.obtener_ruta( tipo_recurso="INDICES" )
                
                # Elimina el índice del disco
                ruta_borrar = f"{self.CFG.get('ruta_indice')}/{self.CFG.get('id_indice')}.pkl"
                archivos.borrar_archivo( ruta=ruta_borrar )
                ruta_borrar = f"{self.CFG.get('ruta_indice')}/{self.CFG.get('id_indice')}.faiss"
                archivos.borrar_archivo( ruta=ruta_borrar )
                return True

        except Exception as e:
            self.almacenes_registrar.error( f"{e}" )

        return False

    # TODO: Se debe corregir para habilitar
    def _combinar_indices_faiss( self, nombre_indice, api_emb=None ):
        from langchain.vectorstores.faiss import FAISS

        if not nombre_indice or not api_emb:
            return False

        try:
            # Configuración de rutas y nombres
            archivos = Archivos(self.config)
            if len( self.CFG.get('ruta_indice') ) == 0:
                self.CFG['ruta_indice'] = archivos.obtener_ruta( tipo_recurso="INDICES" )

            # Borra el nuevo índice si ya existe
            nuevo_indice = f"{self.CFG['ruta_indice']}/{nombre_indice}.faiss"
            archivos.borrar_archivo( ruta=nuevo_indice )

            # Obtiene la lista de archivos .faiss en la carpeta de índices
            lista_archivos = archivos.obtener_lista_archivos( extension='faiss', ruta=self.CFG['ruta_indice'] )
            if not lista_archivos:
                return False

            indice_base = lista_archivos[0]
            self.INDICE = FAISS.load_local( 
                folder_path = self.CFG.get('ruta_indice'), 
                embeddings = api_emb, 
                index_name = indice_base 
            )
            
            for archivo in lista_archivos:
                if archivo not in [ self.CFG['id_indice'], 'index', indice_base ]:
                    indice_archivo = FAISS.load_local( 
                        folder_path = self.CFG.get('ruta_indice'), 
                        embeddings = api_emb, 
                        index_name = archivo 
                    )
                    # self.INDICE.merge_from( indice_archivo )

            # self.INDICE.save_local( self.CFG.get('ruta_indice'), nombre_indice )
            return False

        except Exception as e:
            self.almacenes_registrar.error( f"{e}" )

        return False


    # PINECONE: No implementado
    def _crear_indice_pinecone( self, documentos=None, api_emb=None, id_doc=0 ):
        return False

    def _cargar_indice_pinecone( self, api_emb=None, id_doc=0 ):
        return False


    # MILVUS: No implementado
    def _crear_indice_milvus( self, documentos=None, api_emb=None, id_doc=0 ):
        return False

    def _cargar_indice_milvus( self, api_emb=None, id_doc=0 ):
        return False


    # QDRANT: No implementado
    def _crear_indice_qdrant( self, documentos=None, api_emb=None, id_doc=0 ):
        return False

    def _cargar_indice_qdrant( self, api_emb=None, id_doc=0 ):
        return False


    # REDIS: No implementado
    def _crear_indice_redis( self, documentos=None, api_emb=None, id_doc=0 ):
        return False

    def _cargar_indice_redis( self, api_emb=None, id_doc=0 ):
        return False


    # WEAVIATE: No implementado
    def _crear_indice_weaviate( self, documentos=None, api_emb=None, id_doc=0 ):
        return False

    def _cargar_indice_weaviate( self, api_emb=None, id_doc=0 ):
        return False


    # CHROMA: No implementado
    def _crear_indice_chroma( self, documentos=None, api_emb=None, id_doc=0 ):
        return False

    def _cargar_indice_chroma( self, api_emb=None, id_doc=0 ):
        return False
