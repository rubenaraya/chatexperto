# modelos.py
import json
from registros import configurar_logger

class Modelos:

    def __init__( self, config=None, emb=None, llm=None ):
        
        # Manejador de registros
        self.modelos_registrar = configurar_logger( "modelos", "modelos.log" )
        self.config = config
        
        # Configuración de los modelos basada en parámetros de inicialización
        if not emb:
            emb = "OpenAI_Embeddings"
        if not llm:
            llm = "OpenAI_GPT-3.5"
        self.EMB = self.cargar_configuracion( id_modelo = emb )
        self.LLM = self.cargar_configuracion( id_modelo = llm )

        # Propiedades
        self.MEMORIA = None

######################################################
# FUNCIONES PUBLICAS
######################################################

    # Función para cargar la configuración desde diccionario JSON
    def cargar_configuracion( self, id_modelo ):
        import os
        try:
            ruta_archivo = f"{self.config.RUTA.get('CONFIG')}/modelos.json"
            if not os.path.isfile( ruta_archivo ):
                ruta_archivo = f"{self.config.RUTA.get('SISTEMA')}/modelos.json"
                if not os.path.isfile( ruta_archivo ):
                    return {}
            with open( ruta_archivo, 'r', encoding='utf-8' ) as f:
                datos = json.load( f )
            for fila in datos:
                if fila.get('_uid') == id_modelo:
                    return fila
        except Exception as e:
            self.modelos_registrar.error( f"{e}" )

        return {}

    # Función para configurar parámetros de la interfaz del servicio de finalizaciones LLM
    def configurar_api_llm( self, parametros ):
        try:
            for variable, valor in parametros:
                if variable in self.LLM:
                    self.LLM[variable] = valor
        except Exception as e:
            self.modelos_registrar.error( f"{e}" )
            raise e

    # Función para configurar parámetros del servicio de Embeddings
    def configurar_api_emb( self, parametros ):
        try:
            for variable, valor in parametros:
                if variable in self.EMB:
                    self.EMB[variable] = valor
        except Exception as e:
            self.modelos_registrar.error( f"{e}" )
            raise e

    # Función para aplicar configuración y devolver la interfaz del servicio de Embeddings
    def api_emb( self ):
        interfaz = None
        try:
            # Si el servicio es la API de OpenAI_Embeddings
            if self.EMB.get('_uid') == 'OpenAI_Embeddings':
                from langchain.embeddings.openai import OpenAIEmbeddings
                interfaz = OpenAIEmbeddings(
                    model = self.EMB.get('model'), 
                    chunk_size = int(self.EMB.get('chunk_size')),
                    openai_api_key = self.config.APP.get('openai_api_key')
                )

            # ...otros servicios

        except Exception as e:
            self.modelos_registrar.error( f"{e}" )

        return interfaz

    # Función para aplicar configuración y devolver la interfaz del servicio LLM de completions
    def api_llm( self ):
        interfaz = None
        try:
            # Si el servicio es la API de OpenAI con GPT-3
            if self.LLM.get('_uid') == 'OpenAI_GPT-3':
                from langchain.llms import OpenAI
                interfaz = OpenAI(
                    model_name = self.LLM.get('model'), 
                    temperature = float(self.LLM.get('temperature', 0)),
                    max_tokens = int(self.LLM.get('max_tokens', 0)),
                    openai_api_key = self.config.APP.get('openai_api_key')
                )

            # Si el servicio es la API de OpenAI con GPT-3.5 o GPT-4
            elif self.LLM.get('_uid') in [ "OpenAI_GPT-3.5", "OpenAI_GPT-3.5-16k", "OpenAI_GPT-4" ]:
                from langchain.chat_models import ChatOpenAI
                interfaz = ChatOpenAI(
                    model_name = self.LLM.get('model'), 
                    temperature = float(self.LLM.get('temperature', 0)),
                    max_tokens = int(self.LLM.get('max_tokens', 0)),
                    openai_api_key = self.config.APP.get('openai_api_key')
                )

            # ...otros servicios

        except Exception as e:
            self.modelos_registrar.error( f"{e}" )

        return interfaz

    # Función para crear una interfaz para cadena y configurar sus componentes y atributos
    def crear_cadena( self, indice, clase, plantilla=None, num_docs=4, chain_type="stuff" ):
        interfaz = None
        recuperador = None

        try:
            if indice:
                recuperador = indice.as_retriever( 
                    search_type = "similarity",
                    search_kwargs = {"k": num_docs}
                )

            # Si es una cadena de Consulta
            if clase == 'Consulta':
                interfaz = self._crear_cadena_consulta( recuperador=recuperador, plantilla=plantilla, chain_type=chain_type )

            # Si es una cadena de conversación
            elif clase == 'Conversacion':
                interfaz = self._crear_cadena_conversacion( recuperador=recuperador, plantilla=plantilla )

            # Si es una cadena de peticion
            elif clase == 'Peticion':
                interfaz = self._crear_cadena_peticion()

            # Si es una cadena de búsqueda
            elif clase == 'Busqueda':
                interfaz = self._crear_cadena_busqueda( recuperador=recuperador, plantilla=plantilla, chain_type=chain_type )

        except Exception as e:
            self.modelos_registrar.error( f"{e}" )

        return interfaz

    # Función para escribir contenido en la memoria
    def escribir_memoria( self, contenido ):
        from langchain.schema import messages_from_dict
        historial = []
        try:
            if self.MEMORIA:
                try:
                    if contenido:
                        historial_cargado = json.loads( contenido )
                    else:
                        historial_cargado = []

                except (json.JSONDecodeError):
                    historial_cargado = []

                self.MEMORIA.chat_memory.messages = messages_from_dict( historial_cargado )
                historial = self.MEMORIA.load_memory_variables({})

        except Exception as e:
            self.modelos_registrar.error( f"{e}" )
            historial = []

        return historial

    # Función para leer contenido de la memoria
    def leer_memoria( self ):
        from langchain.schema import messages_to_dict
        try:
            if self.MEMORIA:
                contenido = json.dumps( messages_to_dict( self.MEMORIA.chat_memory.messages ) )
                return contenido
        except Exception as e:
            self.modelos_registrar.error( f"{e}" )

        return None

    # Función para enviar audio a servicio de transcripción
    def transcribir_audio( self, ruta, idioma ):
        import openai
        texto = ""
        with open(ruta, "rb") as f:
            texto = openai.Audio.transcribe(
                file = f,
                model = "whisper-1",
                response_format = "text",
                language = idioma,
                api_key = self.config.APP.get('openai_api_key')
            )
        return texto


######################################################
# FUNCIONES PRIVADAS
######################################################

    def _crear_cadena_consulta( self, recuperador, plantilla, chain_type ):
        from langchain.chains import RetrievalQA
        from langchain.prompts import PromptTemplate
        from langchain.chains.question_answering import load_qa_chain

        interfaz = None
        try:
            chain = None
            llm = self.api_llm()

            if chain_type == "stuff":
                plantilla = plantilla + "\n=========\n{context}\n=========\n{question}"
                PROMPT = PromptTemplate( 
                    template = plantilla,
                    input_variables = [ "question", "context" ]
                )
                chain = load_qa_chain(
                    llm = llm,
                    chain_type = "stuff",
                    verbose = False,
                    prompt = PROMPT
                )

            elif chain_type == "refine":
                chain = load_qa_chain(
                    llm = llm,
                    chain_type = "refine",
                    verbose = False
                )

            elif chain_type == "map_reduce":
                chain = load_qa_chain(
                    llm = llm,
                    chain_type = "map_reduce",
                    verbose = False
                )

            if chain and recuperador:
                interfaz = RetrievalQA(
                    combine_documents_chain = chain,
                    retriever = recuperador,
                    return_source_documents = False,
                    verbose = False
                )
        except Exception as e:
            self.modelos_registrar.error( f"{e}" )

        return interfaz

    def _crear_cadena_conversacion( self, recuperador, plantilla ):
        from langchain.chains import ConversationalRetrievalChain
        from langchain.prompts import ( ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate )
        from langchain.memory import ConversationBufferMemory
        from langchain.chains.question_answering import load_qa_chain

        interfaz = None
        try:
            # Definición plantilla de prompt
            plantilla_system = plantilla + "\n=========\nContext:\n{context}\n=========\nHistory:\n{chat_history}"
            plantilla_human = "{question}"

            prompt_system = SystemMessagePromptTemplate.from_template( template = plantilla_system )
            prompt_human = HumanMessagePromptTemplate.from_template( template = plantilla_human )
            PROMPT = ChatPromptTemplate.from_messages( [ prompt_system, prompt_human ] )

            qa_chain = load_qa_chain(
                llm = self.api_llm(),
                chain_type = "stuff",
                verbose = False,
                prompt = PROMPT
            )

            # Configuración del buffer de memoria
            self.MEMORIA = ConversationBufferMemory(
                return_messages = True,
                memory_key = "chat_history",
                human_prefix = "user",
                ai_prefix = "assistant",
                input_key = "question"
            )

            # Configuración de la cadena de conversacion
            interfaz = ConversationalRetrievalChain.from_llm(
                llm = self.api_llm(),
                retriever = recuperador,
                memory = self.MEMORIA,
                verbose = False,
                return_source_documents = False
            )
            interfaz.combine_docs_chain = qa_chain

        except Exception as e:
            self.modelos_registrar.error( f"{e}" )

        return interfaz

    def _crear_cadena_peticion( self ):
        from langchain.chains import ConversationChain
        from langchain.prompts import ( ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate )
        from langchain.memory import ConversationBufferMemory

        interfaz = None
        try:
            # Definición plantilla de prompt
            plantilla_system = "History:\n{chat_history}"
            plantilla_human = "{input}"

            prompt_system = SystemMessagePromptTemplate.from_template( template = plantilla_system )
            prompt_human = HumanMessagePromptTemplate.from_template( template = plantilla_human )
            PROMPT = ChatPromptTemplate.from_messages( [ prompt_system, prompt_human ] )

            # Configuración del buffer de memoria
            self.MEMORIA = ConversationBufferMemory(
                return_messages = True,
                memory_key = "chat_history",
                human_prefix = "user",
                ai_prefix = "assistant",
                input_key = "input"
            )

            # Configuración de la cadena de tarea
            interfaz = ConversationChain(
                llm = self.api_llm(),
                memory = self.MEMORIA,
                verbose = False,
                prompt = PROMPT
            )

        except Exception as e:
            self.modelos_registrar.error( f"{e}" )

        return interfaz

    def _crear_cadena_busqueda( self, recuperador, plantilla, chain_type ):
        from langchain.chains import RetrievalQA
        from langchain.prompts import PromptTemplate

        if not plantilla or not chain_type:
            return None

        interfaz = None
        try:
            llm = self.api_llm()
            plantilla = plantilla + '\n' + """
            PREGUNTA: {question}
            =========
            {context}
            =========
            RESPUESTA FINAL:"""
            chain_type_kwargs = {"prompt": PromptTemplate(template=plantilla, input_variables=["context", "question"])}
            interfaz = RetrievalQA.from_chain_type(
                llm = llm,
                chain_type = chain_type,
                retriever = recuperador,
                return_source_documents = True,
                chain_type_kwargs = chain_type_kwargs
            )

        except Exception as e:
            self.modelos_registrar.error( f"{e}" )

        return interfaz
