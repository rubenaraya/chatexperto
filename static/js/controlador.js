/* controlador.js
******************************************************
CHAT EXPERTO (Front-end) - Actualizado el: 01/07/2023
******************************************************
Clase: Controlador */

class Controlador {

// Constructor de la clase
    constructor() {
        this.app = '';
        this.idioma = 'es_CL';
        this.url = '';
        this.carpeta = '';
        this.ruta_base = ''
        this.tamano_max = 20; // Tamaño máximo archivos en MB
        this.total = 0; // Total de resultados de consulta
        this.paginas = 0; // Nº páginas de resultados
        this.nav = 1; // Página de navegación actual
        this.max = 10; // Máximo de resultados por página
        this.chunks = [];
        this.mediaRecorder = null;
        this.tiempo_mensajes = 7; //Nº segundos que permanece un mensaje de alerta
        this.tiempo_restante = '10:00'; //Tiempo máximo de grabación para mostrar en formato MM:SS
        this.max_minutos = 10; //Tiempo máximo de grabación en número de minutos
        this.max_mb_audio = 24; //Tamaño máximo archivos de audio en MB
        this.archivo_audio = 'audio-grabado';
        this.grabando = false;
        this.t = {
            error: "Lo siento, ha ocurrido un error. Intenta de nuevo en un momento",
            error_imagen: "Error al subir la imagen",
            error_audio: "Error al transcribir el audio",
            error_excel: "Error al cargar el archivo Excel",
            error_conexion: "Error de conexión, vuelve a intentar luego",
            sin_archivo: "Debes elegir un archivo para cargar",
            sin_buscar: "Debes escribir una o más palabras para buscar",
            excel_novalido: "Debes elegir un archivo Excel (.xlsx)",
            imagen_novalida: "Debes elegir una imagen de tipo PNG",
            audio_novalido: "Debes elegir un archivo de audio válido: MP3, WAV, M4A o WEBM",
            respuesta_novalida: "La respuesta recibida no es válida",
            tamano_max: "El tamaño del archivo cargado supera el límite máximo (" + String(this.tamano_max) + " MB)",
            max_mb_audio: "El tamaño del archivo de audio supera el límite máximo (" + String(this.max_mb_audio) + " MB)",
            sin_audio: "No se pudo acceder al dispositivo de audio"
        };
    }

    establecerUrl() {
        const url = window.location.href;
        this.url = url.split('#')[0].split('?')[0];
    }

    obtenerParametros() {
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('idioma')) {
            this.idioma = urlParams.get('idioma');
        }
        if (urlParams.has('nav')) {
            this.nav = urlParams.get('nav');
        }
        if (urlParams.has('max')) {
            this.max = urlParams.get('max');
        }
    }

    validarArchivo(archivo) {
        const tamanoMaximo = this.tamano_max * 1024 * 1024;
        if (archivo.name == '') {
            return { valido: false, mensaje: this.t['sin_archivo'] };
        }
        if (archivo.size > tamanoMaximo) {
            return { valido: false, mensaje: this.t['tamano_max'] };
        }
        return { valido: true };
    }

    validarAudio(archivo) {
        const tamanoMaximo = this.max_mb_audio * 1024 * 1024;
        if (archivo.name == '') {
            return { valido: false, mensaje: this.t['sin_archivo'] };
        }
        if (archivo.size > tamanoMaximo) {
            return { valido: false, mensaje: this.t['max_mb_audio'] };
        }
        return { valido: true };
    }

    mostrarError(jqXHR, estado, mensaje) {
        var errores;
        var respuesta = jqXHR.responseText;
        if ( jqXHR.readyState === 0 ) {
            control.verMensaje( this.t['error_conexion'], 'error');
        } else {
            if ( typeof respuesta == 'string' ) { 
                try {
                    respuesta = jQuery.parseJSON( respuesta ); 
                    errores = respuesta.error || false;
                    if ( errores ) { 
                        mensaje = errores;
                        estado = respuesta.codigo;
                    }
                }
                catch (e) { 
                    mensaje = respuesta; 
                }
            }
            if ( estado < 200 || estado >= 500 ) {
                control.verMensaje( mensaje, 'error' );
            } else if ( estado >= 300 && estado < 500 ) {
                control.verMensaje( mensaje, 'error' );
            } else {
                control.verMensaje( mensaje, 'aviso' );
            }
        }
        jQuery("#zona_espera").hide();
        jQuery("#mensaje_solucion_" + estado).show();
        return mensaje;
    }

    mostrarRespuesta(respuesta) {
        respuesta = control.comprobarContenido( respuesta );
        if ( respuesta ) {
            control.verMensaje( respuesta.respuesta, 'exito' );
        }
    }

    comprobarContenido(respuesta) {
        if ( jQuery.isEmptyObject( respuesta ) ) {
            control.verMensaje( this.t['respuesta_novalida'], 'error' );
            return false;
        }
        if ( typeof respuesta == 'string' ) { 
            try {
                respuesta = jQuery.parseJSON( respuesta ); 
            } catch (e) { 
                control.verMensaje( respuesta, 'aviso' );
                return false;
            }
        }
        return respuesta;
    }

    verMensaje(mensaje, tipo) {
        var alerta;
        if (tipo=='error') {
            alerta = jQuery("#mensaje_error");
        } else if (tipo=='exito') {
            alerta = jQuery("#mensaje_exito");
        } else {
            alerta = jQuery("#mensaje_aviso");
        }
        alerta.html( mensaje );
        alerta.show();
        setTimeout(function () {
            alerta.fadeOut('slow');
        }, control.tiempo_mensajes * 1000);
    }

    cambiarVisible(selector, visible) {
        const seleccion = jQuery('#' + selector);
        const seleccionClase = jQuery('.' + selector);
        if (typeof visible === "undefined" || visible === null) {
            if (seleccion.length > 0) {
                seleccion.toggle();
            } else if (seleccionClase.length > 0) {
                seleccionClase.toggle();
            }
        } else if (visible === true) {
            if (seleccion.length > 0) {
                seleccion.show();
            } else if (seleccionClase.length > 0) {
                seleccionClase.show();
            }
        } else {
            if (seleccion.length > 0) {
                seleccion.hide();
            } else if (seleccionClase.length > 0) {
                seleccionClase.hide();
            }
        }
    }

    activarBuscador(selector) {
        if ( selector === undefined || typeof selector == "selector" || selector == null ) { return; }
        const campo = document.querySelector(`input#${selector}`);
        if (campo) {
            campo.focus();
        }
    }

    activarLogin() {
        const campo = document.querySelector('input#username');
        if (campo) {
            campo.focus();
        }
    }

    activarChat() {
        const campo = document.querySelector('input#user-input');
        if (campo) {
            campo.addEventListener('keypress', (e) => {
                if (e.which === 13) {
                    this.enviarPregunta();
                    return false;
                }
            });
            campo.focus();
        }
    }

    abrirUrl(url) {
        self.location.href = url;
    }

    volverMostrar(zona) {
        jQuery("#resultados").html("");
        jQuery("#" + zona).show();
        jQuery("#zona_espera").hide();
    }

    cerrarSesion() {
        document.cookie = encodeURIComponent( 'token' ) + '=; path=/';
        self.location.href = control.ruta_base + '/';
    }

    abrirVentana(contenido) {
        var ventana = jQuery( '#INT_VENTANA' );
        ventana.html( contenido );
        ventana.modal( 'show' );
    }

    abrirModal(contenido) {
        var ventana = jQuery( '#INT_MODAL' );
        ventana.html( contenido );
        ventana.modal( 'show' );
    }

    cerrarVentana() {
        var ventana = jQuery( '#INT_VENTANA' );
        ventana.modal( 'hide' );
        ventana.html('');
    }

    cerrarModal() {
        var ventana = jQuery( '#INT_MODAL' );
        ventana.modal( 'hide' );
        ventana.html('');
    }

    confirmarAccion(tipo, id) {
        let html = jQuery('#confirmar_accion').html();
        html = html.replace('((tipo_recurso))', tipo);
        html = html.replace('((id_recurso))', id);
        control.abrirVentana(html);
    }

    activarCopiar() {
        jQuery('.boton-copiar').click(function() {
            var texto = jQuery(this).prev('.texto-copiable').html();
            texto = texto.replace(/<br>/g, "\n");
            texto = texto.replace(/^\s+/gm, '')
            .replace(/\s{2,}/g, ' ')
            .replace(/\n\s*\n/g, '\n');
            var tempElement = jQuery('<textarea>');
            tempElement.val(texto).appendTo('body').select();
            document.execCommand('copy');
            tempElement.remove();
            jQuery(this).next('.icono-copiado').show();
        });
    }

    enviarPregunta() {
        const pregunta = jQuery("#user-input").val().trim();
        if (pregunta.length > 2) {
            jQuery("#chat-input").hide();
            jQuery("#chat-espera").show();
            let fondo = jQuery('#chat-content');
            if (fondo) {
                fondo.removeClass('rojizo');
                fondo.removeClass('verdoso');
            }
            const datos = JSON.stringify( jQuery('#form_opciones').serializeJSON() );
            const peticion = jQuery.ajax({
                type: "POST",
                url: control.ruta_base + "/chat",
                dataType: "json",
                contentType: "application/json",
                beforeSend: function (xhr) {
                    var token = leerCookie('token');
                    var id_sesion = leerCookie('id_sesion');
                    xhr.setRequestHeader('id_sesion', id_sesion);
                    xhr.setRequestHeader('token', token);
                    xhr.setRequestHeader('app', control.app);
                },
                data: datos
            });
            peticion.done((response) => {
                jQuery("#chat-espera").hide();
                jQuery("#user-input").val("");
                jQuery("#chat-input").show();
                jQuery("#user-input").focus();
                if (response && response.peticion && response.respuesta && response.id) {
                    const plantilla = jQuery('#plantilla_resultado').html();
                    let html = plantilla;
                    html = html.replace('((peticion))', response.peticion);
                    html = html.replace('((respuesta))', response.respuesta);
                    jQuery("#response-content").html(html);
                    jQuery("#evaluacion").fadeIn();
                    jQuery("#like-btn").unbind().click(() => {
                        this.enviarEvaluacion(response.id, 1);
                    });
                    jQuery("#dislike-btn").unbind().click(() => {
                        this.enviarEvaluacion(response.id, 2);
                    });
                } else if (response && response.respuesta) {
                    jQuery("#response-content").html(response.respuesta);
                } else if (response && response.error) {
                    jQuery("#response-content").html(response.error);
                } else {
                    jQuery("#response-content").html(this.t['error']);
                }
            });
            peticion.fail((jqXHR, estado, mensaje) => {
                jQuery("#chat-input").show();
                jQuery("#chat-espera").hide();
                jQuery("#response-content").html(this.t['error']);
            });
        }
    }

    enviarEvaluacion(uid, evaluacion) {
        if (!evaluacion) {
            evaluacion = 0;
        }
        if (!uid) {
            uid = 0;
        }
        const datos = JSON.stringify({ "evaluacion": evaluacion });
        const peticion = jQuery.ajax({
            type: "POST",
            url: control.ruta_base + "/chat/" + uid,
            dataType: "json",
            contentType: "application/json",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            },
            data: datos
        });
        peticion.done((response) => {
            jQuery("#evaluacion").hide();
            let fondo = jQuery('#chat-content');
            if ( evaluacion === 1 && fondo ) {
                fondo.addClass('verdoso');
            } else if ( evaluacion === 2 && fondo ) {
                fondo.addClass('rojizo');
            }
            jQuery("#user-input").focus();
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            jQuery("#user-input").focus();
        });
    }

    abrirMenu(pagina) {
        jQuery('.alert').each(function() {
            jQuery(this).hide();
        });
        jQuery("#zona_espera").show();
        jQuery("#zona_contenido").hide();
        const peticion = jQuery.ajax({
            type: "GET",
            url: control.ruta_base + "/" + pagina,
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((response) => {
            jQuery("#zona_espera").hide();
            jQuery("#zona_contenido").html(response);
            jQuery("#zona_contenido").fadeIn();
            jQuery('.navbar-collapse').collapse('hide');
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
        });
    }

    revisarInteracciones(nav) {
        if (!nav) {
            nav = this.nav;
        }
        this.nav = nav;
        jQuery( '#con_nav' ).val(this.nav);
        this.total = 0;
        this.paginas = 0;
        const datos = JSON.stringify(jQuery('#form_revisar').serializeJSON());
        const peticion = jQuery.ajax({
            type: "POST",
            url: control.ruta_base + "/revisar",
            dataType: "json",
            contentType: "application/json",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            },
            data: datos
        });
        peticion.done((response) => {
            if (response && response.resultados) {
                const resultados = response.resultados;
                this.total = response.total;
                this.paginas = response.paginas;
                this.nav = response.nav;
                this.max = response.max;
                let html = "";
                const plantilla = jQuery('#plantilla_resultado').html();
                for (let i = 0; i < resultados.length; i++) {
                    let reemplazar = plantilla;
                    reemplazar = reemplazar.replace('((fecha))', resultados[i].fecha);
                    reemplazar = reemplazar.replace('((hora))', resultados[i].hora);
                    reemplazar = reemplazar.replace('((tiempo))', resultados[i].tiempo);
                    reemplazar = reemplazar.replace('((peticion))', resultados[i].peticion);
                    reemplazar = reemplazar.replace('((respuesta))', resultados[i].respuesta);
                    if ( resultados[i].evaluacion === 1 ) {
                        reemplazar = reemplazar.replace('"caso"', '"caso verdoso"');
                    } else if ( resultados[i].evaluacion === 2 ) {
                        reemplazar = reemplazar.replace('"caso"', '"caso rojizo"');
                    } else{
                        reemplazar = reemplazar.replace('"caso"', '"caso grisaceo"');
                    }
                    html += reemplazar;
                }
                jQuery("#resultados").html(html);
            } else if (response && response.respuesta) {
                jQuery("#resultados").html(response.respuesta);
            } else if (response && response.error) {
                jQuery("#resultados").html(response.error);
            } else {
                jQuery("#resultados").html(this.t['error']);
            }
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    async subirArchivo(form) {
        jQuery("#form_subir").hide();
        const formData = new FormData(form);
        const archivo = formData.get('archivo');
        const validacion = this.validarArchivo(archivo);
        if (!validacion.valido) {
            jQuery("#respuesta").html(validacion.mensaje).show();
            jQuery("#form_subir").show();
            return;
        }
        jQuery("#zona_espera").show();
        jQuery("#zona_contenido").hide();
        var carpeta = jQuery( 'select#carpeta' );
        if (carpeta.val() != '') {
            control.carpeta = carpeta.val();
        }
        try {
            const response = await fetch(control.ruta_base + '/subir', {
                method: 'POST',
                beforeSend: function (xhr) {
                    var token = leerCookie('token');
                    var id_sesion = leerCookie('id_sesion');
                    xhr.setRequestHeader('id_sesion', id_sesion);
                    xhr.setRequestHeader('token', token);
                    xhr.setRequestHeader('app', control.app);
                },
                body: formData
            });
            const jsonResponse = await response.json();
            const plantilla = jQuery('#plantilla_respuesta').html();
            let html = plantilla;
            html = html.replace('((respuesta))', jsonResponse.respuesta);
            jQuery("#respuesta").html(html).show();
            if ( jsonResponse.respuesta ) {
                jQuery("#zona_espera").hide();
                jQuery("#zona_contenido").show();
            }
            if ( jsonResponse.error ) {
                    jQuery("#zona_espera").hide();
                    jQuery("#zona_contenido").show();
                    jQuery("#respuesta").html(jsonResponse.error).show();
                    jQuery("#form_subir").show();
                }
        } catch (error) {
            jQuery("#zona_espera").hide();
            jQuery("#zona_contenido").show();
            jQuery("#respuesta").html(this.t['error']).show();
            jQuery("#form_subir").show();
        }
    }

    async cargarArchivo(form) {
        jQuery("#form_subir").hide();
        const formData = new FormData(form);
        const archivo = formData.get('archivo');
        const validacion = this.validarArchivo(archivo);
        if (!validacion.valido) {
            jQuery("#respuesta").html(validacion.mensaje).show();
            jQuery("#form_subir").show();
            return;
        }
        jQuery("#zona_espera").show();
        jQuery("#zona_contenido").hide();
        var carpeta = jQuery( 'select#carpeta' );
        if (carpeta.val() != '') {
            control.carpeta = carpeta.val();
        }
        try {
            const response = await fetch(control.ruta_base + '/cargar', {
                method: 'POST',
                beforeSend: function (xhr) {
                    var token = leerCookie('token');
                    var id_sesion = leerCookie('id_sesion');
                    xhr.setRequestHeader('id_sesion', id_sesion);
                    xhr.setRequestHeader('token', token);
                    xhr.setRequestHeader('app', control.app);
                },
                body: formData
            });
            const jsonResponse = await response.json();
            const plantilla = jQuery('#plantilla_respuesta').html();
            let html = plantilla;
            html = html.replace('((respuesta))', jsonResponse.respuesta);
            html = html.replace('((id_doc))', jsonResponse.id_doc);
            html = html.replace('((id_doc))', jsonResponse.id_doc);
            html = html.replace('((carpeta))', control.carpeta);
            jQuery("#respuesta").html(html).show();
            if ( jsonResponse.respuesta ) {
                jQuery("#zona_espera").hide();
                jQuery("#zona_contenido").show();
            }
            if ( jsonResponse.error ) {
                    jQuery("#zona_espera").hide();
                    jQuery("#zona_contenido").show();
                    jQuery("#respuesta").html(jsonResponse.error).show();
                    jQuery("#form_subir").show();
                }
        } catch (error) {
            jQuery("#zona_espera").hide();
            jQuery("#zona_contenido").show();
            jQuery("#respuesta").html(this.t['error']).show();
            jQuery("#form_subir").show();
        }
    }

    actualizarIndices() {
        const datos = JSON.stringify(jQuery('#form_actualizar').serializeJSON());
        jQuery("#form_actualizar").hide();
        jQuery("#zona_espera").show();
        jQuery("#resultados").html("");
        const peticion = jQuery.ajax({
            type: "POST",
            url: control.ruta_base + "/actualizar",
            dataType: "json",
            contentType: "application/json",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            },
            data: datos
        });
        peticion.done((response) => {
            jQuery("#zona_espera").hide();
            const plantilla = jQuery('#plantilla_respuesta').html();
            let respuesta = '';
            if (response && response.respuesta) {
                respuesta = response.respuesta;
            } else if (response && response.error) {
                respuesta = response.error;
            } else {
                respuesta = this.t['error'];
            }
            let html = plantilla;
            html = html.replace('((respuesta))', respuesta);
            jQuery("#resultados").html(html);
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            jQuery("#form_actualizar").show();
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    crearColeccion() {
        const datos = JSON.stringify(jQuery('#form_coleccion').serializeJSON());
        jQuery("#div_crear").hide();
        jQuery("#zona_espera").show();
        jQuery("#resultados").html("");
        const peticion = jQuery.ajax({
            type: "POST",
            url: control.ruta_base + "/admin",
            dataType: "json",
            contentType: "application/json",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            },
            data: datos
        });
        peticion.done((response) => {
            jQuery("#zona_espera").hide();
            const plantilla = jQuery('#plantilla_respuesta').html();
            let respuesta = '';
            if (response && response.respuesta) {
                respuesta = response.respuesta;
            } else if (response && response.error) {
                respuesta = response.error;
            } else {
                respuesta = this.t['error'];
            }
            let html = plantilla;
            html = html.replace('((respuesta))', respuesta);
            jQuery("#resultados").html(html);
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    editarArchivo(id) {
        var caso = jQuery( '#ar_'+ id );
        caso.removeClass( 'mark' );
        caso.addClass( 'mark' );
        const peticion = jQuery.ajax({
            type: "GET",
            url: control.ruta_base + "/archivo/" + id,
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((respuesta) => {
            control.abrirVentana(respuesta);
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    editarDocumento(id) {
        var caso = jQuery( '#ar_'+ id );
        caso.removeClass( 'mark' );
        caso.addClass( 'mark' );
        const peticion = jQuery.ajax({
            type: "GET",
            url: control.ruta_base + "/documento/" + id,
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((respuesta) => {
            control.abrirVentana(respuesta);
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    guardarArchivo(id) {
        var datos = jQuery( '#form_editar' ).serialize();
        jQuery("#form_editar_campos").hide();
        jQuery("#form_editar_botones").hide();
        jQuery("#form_editar_espera").show();
        const peticion = jQuery.ajax({
            type: "POST",
            url: control.ruta_base + "/archivo/" + id,
            data: datos,
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((respuesta) => {
            jQuery("#form_editar_espera").hide();
            control.cerrarVentana();
            control.mostrarRespuesta( respuesta );
            control.consultarArchivos( control.nav );
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            jQuery("#form_editar_espera").hide();
            jQuery("#form_editar_campos").show();
            jQuery("#form_editar_botones").show();
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    guardarDocumento(id) {
        var datos = jQuery( '#form_editar' ).serialize();
        jQuery("#form_editar_campos").hide();
        jQuery("#form_editar_botones").hide();
        jQuery("#form_editar_espera").show();
        const peticion = jQuery.ajax({
            type: "POST",
            url: control.ruta_base + "/archivo/" + id,
            data: datos,
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((respuesta) => {
            jQuery("#form_editar_espera").hide();
            control.cerrarVentana();
            control.mostrarRespuesta( respuesta );
            control.consultarDocumentos( control.nav );
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            jQuery("#form_editar_espera").hide();
            jQuery("#form_editar_campos").show();
            jQuery("#form_editar_botones").show();
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    descargarArchivo(codigo) {
        let url = control.ruta_base + "/descarga/" + codigo;
        window.open( url, '_blank' );
    }

    consultarArchivos(nav) {
        if (!nav) {
            nav = this.nav;
        }
        this.nav = nav;
        var con_carpeta = jQuery( '#con_carpeta' );
        if (this.carpeta && con_carpeta.val()=='') {
            con_carpeta.val(this.carpeta);
        } else {
            this.carpeta = con_carpeta.val();
        }
        jQuery( '#con_nav' ).val(this.nav);
        this.total = 0;
        this.paginas = 0;
        var datos = jQuery( '#form_archivos' ).serialize();
        jQuery("#lista_archivos").hide();
        jQuery("#zona_espera").show();
        const peticion = jQuery.ajax({
            type: "POST",
            url: control.ruta_base + "/archivos",
            data: datos,
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((respuesta) => {
            var destino = jQuery( '#lista_archivos' );
            destino.html( respuesta );
            jQuery("#zona_espera").hide();
            destino.show();
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            jQuery("#lista_archivos").show();
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    consultarDocumentos(nav) {
        if (!nav) {
            nav = this.nav;
        }
        this.nav = nav;
        var con_carpeta = jQuery( '#con_carpeta' );
        if (this.carpeta && con_carpeta.val()=='') {
            con_carpeta.val(this.carpeta);
        } else {
            this.carpeta = con_carpeta.val();
        }
        jQuery( '#con_nav' ).val(this.nav);
        this.total = 0;
        this.paginas = 0;
        var datos = jQuery( '#form_archivos' ).serialize();
        jQuery("#lista_archivos").hide();
        jQuery("#zona_espera").show();
        const peticion = jQuery.ajax({
            type: "POST",
            url: control.ruta_base + "/documentos",
            data: datos,
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((respuesta) => {
            var destino = jQuery( '#lista_archivos' );
            destino.html( respuesta );
            jQuery("#zona_espera").hide();
            destino.show();
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            jQuery("#lista_archivos").show();
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    crearCarpeta() {
        const datos = JSON.stringify(jQuery('#form_carpeta').serializeJSON());
        jQuery("#div_crear").hide();
        jQuery("#zona_espera").show();
        jQuery("#resultados").html("");
        const peticion = jQuery.ajax({
            type: "POST",
            url: control.ruta_base + "/carpetas",
            dataType: "json",
            contentType: "application/json",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            },
            data: datos
        });
        peticion.done((response) => {
            jQuery("#zona_espera").hide();
            const plantilla = jQuery('#plantilla_respuesta').html();
            let respuesta = '';
            if (response && response.respuesta) {
                respuesta = response.respuesta;
            } else if (response && response.error) {
                respuesta = response.error;
            } else {
                respuesta = this.t['error'];
            }
            let html = plantilla;
            html = html.replace('((respuesta))', respuesta);
            jQuery("#resultados").html(html);
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    crearMicarpeta() {
        const datos = JSON.stringify(jQuery('#form_carpeta').serializeJSON());
        jQuery("#div_crear").hide();
        jQuery("#zona_espera").show();
        jQuery("#resultados").html("");
        const peticion = jQuery.ajax({
            type: "POST",
            url: control.ruta_base + "/carpetas",
            dataType: "json",
            contentType: "application/json",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            },
            data: datos
        });
        peticion.done((response) => {
            jQuery("#zona_espera").hide();
            control.mostrarRespuesta( response );
            control.abrirMenu('miscarpetas');
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    elegirImagen(aplicacion) {
        const peticion = jQuery.ajax({
            type: "GET",
            data: "aplicacion=" + encodeURIComponent(aplicacion),
            url: control.ruta_base + "/imagen",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((respuesta) => {
            control.abrirVentana(respuesta);
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
        });
    }

    async subirImagen(form) {
        const formData = new FormData(form);
        try {
            const imagen = formData.get('imagen');
            const tiposPermitidos = [
                'image/png'
            ];
            if (!tiposPermitidos.includes(imagen.type)) {
                jQuery("#ventana_error").html( this.t['imagen_novalida']).show();
                return false;
            }
            jQuery("#form_imagen_subir").hide();
            jQuery("#form_imagen_botones").hide();
            jQuery("#form_imagen_espera").show();
            const response = await fetch(control.ruta_base + '/imagen', {
                method: 'POST',
                beforeSend: function (xhr) {
                    var token = leerCookie('token');
                    var id_sesion = leerCookie('id_sesion');
                    xhr.setRequestHeader('id_sesion', id_sesion);
                    xhr.setRequestHeader('token', token);
                    xhr.setRequestHeader('app', control.app);
                },
                body: formData
            });
            const jsonResponse = await response.json();
            if ( jsonResponse.respuesta ) {
                jQuery("#form_imagen_espera").hide();
                control.cerrarVentana();
                control.abrirMenu('admin');
                control.mostrarRespuesta( jsonResponse );
            }
            if ( jsonResponse.error ) {
                jQuery("#form_imagen_espera").hide();
                control.cerrarVentana();
                control.verMensaje( this.t['error_imagen'], 'error' );
            }
        } catch (error) {
            jQuery("#form_imagen_espera").hide();
            control.cerrarVentana();
            control.verMensaje( this.t['error_imagen'], 'error' );
        }
    }

    crearUsuario() {
        const datos = JSON.stringify(jQuery('#form_usuario').serializeJSON());
        jQuery("#div_crear").hide();
        jQuery("#zona_espera").show();
        jQuery("#resultados").html("");
        const peticion = jQuery.ajax({
            type: "POST",
            url: control.ruta_base + "/usuarios",
            dataType: "json",
            contentType: "application/json",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            },
            data: datos
        });
        peticion.done((response) => {
            jQuery("#zona_espera").hide();
            const plantilla = jQuery('#plantilla_respuesta').html();
            let respuesta = '';
            if (response && response.respuesta) {
                respuesta = response.respuesta;
            } else if (response && response.error) {
                respuesta = response.error;
            } else {
                respuesta = this.t['error'];
            }
            let html = plantilla;
            html = html.replace('((respuesta))', respuesta);
            jQuery("#resultados").html(html);
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    editarUsuario(id) {
        var caso = jQuery( '#us_'+ id );
        caso.removeClass( 'mark' );
        caso.addClass( 'mark' );
        const peticion = jQuery.ajax({
            type: "GET",
            url: control.ruta_base + "/usuario/" + id,
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((respuesta) => {
            control.abrirVentana(respuesta);
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    guardarUsuario(id) {
        var datos = jQuery( '#form_editar' ).serialize();
        jQuery("#form_editar_campos").hide();
        jQuery("#form_editar_botones").hide();
        jQuery("#form_editar_espera").show();
        const peticion = jQuery.ajax({
            type: "POST",
            url: control.ruta_base + "/usuario/" + id,
            data: datos,
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((respuesta) => {
            jQuery("#form_editar_espera").hide();
            control.cerrarVentana();
            control.mostrarRespuesta( respuesta );
            control.abrirMenu('usuarios');
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            jQuery("#form_editar_espera").hide();
            jQuery("#form_editar_campos").show();
            jQuery("#form_editar_botones").show();
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    borrarUsuario(id) {
        const peticion = jQuery.ajax({
            type: "DELETE",
            url: control.ruta_base + "/usuario/" + id,
            dataType: "json",
            contentType: "application/json",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((respuesta) => {
            control.mostrarRespuesta( respuesta );
            control.abrirMenu('usuarios');
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    borrarArchivo(id) {
        const peticion = jQuery.ajax({
            type: "DELETE",
            url: control.ruta_base + "/archivo/" + id,
            dataType: "json",
            contentType: "application/json",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((respuesta) => {
            control.mostrarRespuesta( respuesta );
            control.consultarArchivos( control.nav );
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    borrarDocumento(id) {
        const peticion = jQuery.ajax({
            type: "DELETE",
            url: control.ruta_base + "/archivo/" + id,
            dataType: "json",
            contentType: "application/json",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((respuesta) => {
            control.mostrarRespuesta( respuesta );
            control.consultarDocumentos( control.nav );
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    borrarCarpeta(carpeta) {
        const peticion = jQuery.ajax({
            type: "DELETE",
            url: control.ruta_base + '/carpetas/' + encodeURIComponent(carpeta),
            dataType: "json",
            contentType: "application/json",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((respuesta) => {
            control.mostrarRespuesta( respuesta );
            control.abrirMenu('carpetas');
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    borrarMicarpeta(carpeta) {
        const peticion = jQuery.ajax({
            type: "DELETE",
            url: control.ruta_base + '/carpetas/' + encodeURIComponent(carpeta),
            dataType: "json",
            contentType: "application/json",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((respuesta) => {
            control.mostrarRespuesta( respuesta );
            control.abrirMenu('miscarpetas');
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    borrarRecurso(tipo, id) {
        var ventana = jQuery( '#INT_VENTANA' );
        ventana.modal( 'hide' );
        switch (tipo) {
            case 'usuario':
                this.borrarUsuario(id);
                break;
            case 'documento':
                this.borrarDocumento(id);
                break;
            case 'archivo':
                this.borrarArchivo(id);
                break;
            case 'micarpeta':
                this.borrarMicarpeta(id);
                break;
            case 'carpeta':
                this.borrarCarpeta(id);
                break;
            case 'plantilla':
                this.borrarPlantilla(id);
                break;
        }
    }

    verMetadatos(id) {
        var caso = jQuery( '#ar_'+ id );
        caso.removeClass( 'mark' );
        caso.addClass( 'mark' );
        const peticion = jQuery.ajax({
            type: "GET",
            url: control.ruta_base + "/metadatos/" + id,
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((respuesta) => {
            control.abrirModal(respuesta);
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    generarMetadatos(id) {
        var datos = jQuery( '#form_metadatos' ).serialize();
        jQuery("#form_editar_botones").hide();
        jQuery("#form_editar_metadatos").hide();
        jQuery("#form_editar_espera").show();
        const peticion = jQuery.ajax({
            type: "POST",
            url: control.ruta_base + "/metadatos/" + id,
            data: datos,
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((respuesta) => {
            jQuery("#form_editar_espera").hide();
            control.cerrarModal();
            control.mostrarRespuesta( respuesta );
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            jQuery("#form_editar_espera").hide();
            jQuery("#form_editar_metadatos").show();
            jQuery("#form_editar_botones").show();
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    consultarChatdoc(carpeta, id) {
        if (!carpeta) {
            carpeta = '';
        }
        if (!id) {
            id = '';
        }
        if (id.length > 0) {
            let caso = jQuery( '#ar_'+ id );
            caso.removeClass( 'mark' );
            caso.addClass( 'mark' );
        } else {
            this.carpeta = carpeta;
            let caso = jQuery( '#car_'+ carpeta );
            caso.removeClass( 'mark' );
            caso.addClass( 'mark' );
        }
        jQuery("div#seccion_asistente").hide();
        jQuery("div#seccion_documentos").hide();
        jQuery("div#seccion_biblioteca").hide();
        jQuery("div#seccion_tutor").hide();
        jQuery("#zona_espera").show();
        const peticion = jQuery.ajax({
            type: "GET",
            url: control.ruta_base + "/chatdoc?carpeta=" + encodeURIComponent(carpeta) + '&doc=' + encodeURIComponent(id),
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((response) => {
            jQuery("#zona_espera").fadeOut();
            jQuery("div#consultar_chatdoc").html(response);
            jQuery("div#consultar_chatdoc").fadeIn();
            const campo = document.querySelector('input#input-mensaje-usuario');
            if (campo) {
                campo.addEventListener('keypress', (e) => {
                    if (e.which === 13) {
                        control.enviarConsulta();
                        return false;
                    }
                });
                campo.focus();
            }
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
            control.volverAsistente();
        });
    }

    volverAsistente() {
        jQuery("#zona_espera").hide();
        var asistente = jQuery("#seccion_asistente");
        var documentos = jQuery("#seccion_documentos");
        var biblioteca = jQuery("#seccion_biblioteca");
        var tutor = jQuery("#seccion_tutor");
        jQuery("#consultar_chatdoc").fadeOut('fast', function(){
            jQuery("#consultar_chatdoc").html('');
            if (asistente.length) {
                asistente.fadeIn();
            }
            if (documentos.length) {
                documentos.fadeIn();
            }
            if (biblioteca.length) {
                biblioteca.fadeIn();
            }
            if (tutor.length) {
                tutor.fadeIn();
            }
        });
    }

    enviarConsulta() {
        var input_mensaje_usuario = jQuery('input#input-mensaje-usuario');
        var imagen_espera = jQuery("div#chat-imagen-espera");
        var mensajes_conversacion = jQuery("div#chat-mensajes-conversacion");
        var caja_enviar_mensaje = jQuery("div#chat-enviar-mensaje");
        var pie_chat = jQuery('div#chat-pie' );
		let consulta = input_mensaje_usuario.val();
		if ( consulta.length < 3 ) { return; }
		caja_enviar_mensaje.hide();
		imagen_espera.show();
        jQuery(window).scrollTop( pie_chat.position().top);
		let html = jQuery("div#chat-plantilla-consulta").html();
		html = html.replace('((consulta))', consulta );
		mensajes_conversacion.append(html);
		const datos = JSON.stringify( jQuery( '#form-chat-enviar' ).serializeJSON() );
        const peticion = jQuery.ajax({
            type: "POST",
            url: control.ruta_base + "/chatdoc",
            dataType: "json",
            contentType: "application/json",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            },
            data: datos
        });
        peticion.done((response) => {
			imagen_espera.hide();
			input_mensaje_usuario.val("");
			caja_enviar_mensaje.show();
			input_mensaje_usuario.focus();
			if (response && response.peticion && response.respuesta) {
				let html = jQuery("div#chat-plantilla-respuesta").html();
                let respuesta = response.respuesta;
                respuesta = respuesta.replace(/\n/g, "<br>");
				html = html.replace('((respuesta))', respuesta);
				mensajes_conversacion.append(html);
			} else if (response && response.respuesta) {
				let html = jQuery("div#chat-plantilla-respuesta").html();
                let respuesta = response.respuesta;
                respuesta = respuesta.replace(/\n/g, "<br>");
                html = html.replace('((respuesta))', respuesta);
				mensajes_conversacion.append(html);
			} else if (response && response.error) {
				let html = jQuery("div#chat-plantilla-error").html();
				html = html.replace('((error))', response.error);
				mensajes_conversacion.append(html);
			} else {
				let html = jQuery("div#chat-plantilla-error").html();
				html = html.replace('((error))', this.t['error']);
				mensajes_conversacion.append(html);
			}
			jQuery(window).scrollTop( pie_chat.position().top);
            control.activarCopiar();
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            mensaje = control.mostrarError( jqXHR, estado, mensaje );
			imagen_espera.hide();
			caja_enviar_mensaje.show();
			let html = jQuery("div#chat-plantilla-error").html();
			html = html.replace('((error))', mensaje);
			mensajes_conversacion.append(html);
			jQuery(window).scrollTop( pie_chat.position().top);
        });
    }

    ingresarApikey() {
        const datos = JSON.stringify(jQuery('form#form_apikey').serializeJSON());
        jQuery("form#form_apikey").hide();
        const peticion = jQuery.ajax({
            type: "POST",
            url: control.ruta_base + "/apikey",
            dataType: "json",
            contentType: "application/json",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            },
            data: datos
        });
        peticion.done((response) => {
            control.mostrarRespuesta( response );
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    preguntaConsultar(texto) {
        var preguntas = new bootstrap.Collapse(document.getElementById('preguntas'));
        preguntas.hide();
        jQuery('input#input-mensaje-usuario').val(texto);
        this.enviarConsulta();
    }

    enfocarInputMensaje() {
        jQuery(window).scrollTop( jQuery('div#chat-pie' ).position().top);
        jQuery('input#input-mensaje-usuario').focus();
    }

    exportarChatdoc(carpeta, id) {
        if (!carpeta) {
            carpeta = '';
        }
        if (!id) {
            id = '';
        }
        let url = control.ruta_base + "/chatdoc/" + encodeURIComponent(carpeta) + '?doc=' + id;
        window.open( url, '_blank' );
    }

    vaciarChatdoc(carpeta, id) {
        if (!carpeta) {
            carpeta = '';
        }
        if (!id) {
            id = '';
        }
        const datos = JSON.stringify({ "doc": id });
        const peticion = jQuery.ajax({
            type: "POST",
            url: control.ruta_base + "/chatdoc/" + carpeta,
            dataType: "json",
            contentType: "application/json",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            },
            data: datos
        });
        peticion.done((response) => {
            control.cerrarVentana();
            control.mostrarRespuesta( response );
            control.consultarChatdoc(carpeta, id);
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.cerrarVentana();
            control.mostrarError( jqXHR, estado, mensaje );
        });
    }

    ajustarTextos(opcion) {
        if (opcion=='+') {
            jQuery('.texto-ajustable').each(function() {
                var fontSize = parseInt(jQuery(this).css('font-size'));
                fontSize += 1;
                jQuery(this).css('font-size', fontSize + 'px');
              });
        } else if (opcion=='-') {
            jQuery('.texto-ajustable').each(function() {
                var fontSize = parseInt(jQuery(this).css('font-size'));
                fontSize -= 1;
                jQuery(this).css('font-size', fontSize + 'px');
              });
        }
    }

    desplazarPosicion(opcion) {
        if (opcion=='+') {
            jQuery(window).scrollTop( jQuery('div#chat-encabezado' ).position().top);
        } else if (opcion=='-') {
            jQuery(window).scrollTop( jQuery('div#chat-pie' ).position().top);
        }
    }

    cambiarCarpeta(carpeta, abrir) {
        if (!carpeta) {
            carpeta = '';
        }
        this.carpeta = carpeta;
        if (abrir=='archivos') {
            this.abrirMenu('archivos');
        } else {
            this.abrirMenu('documentos');
        }
    }

    evaluarInteraccion(uid, evaluacion) {
        if (!evaluacion) {
            evaluacion = 0;
        }
        if (!uid) {
            uid = 0;
        }
        const datos = JSON.stringify({ "evaluacion": evaluacion });
        const peticion = jQuery.ajax({
            type: "POST",
            url: control.ruta_base + "/chat/" + uid,
            dataType: "json",
            contentType: "application/json",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            },
            data: datos
        });
        peticion.done((response) => {
            let fondo = jQuery('#resp_' + uid);
            if ( evaluacion === 1 && fondo ) {
                fondo.css("background-color","#bdecb6");
            } else if ( evaluacion === 2 && fondo ) {
                fondo.css("background-color","#ebc1c8");
            }
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
        });
    }

    generarIndice(carpeta) {
        if (!carpeta) {
            carpeta = this.carpeta;
        }
        this.carpeta = carpeta;
        const datos = JSON.stringify({ "carpeta": this.carpeta });
        jQuery('.alert').each(function() {
            jQuery(this).hide();
        });
        jQuery("#zona_espera").show();
        jQuery("#zona_contenido").hide();
        const peticion = jQuery.ajax({
            type: "POST",
            url: control.ruta_base + "/actualizar",
            dataType: "json",
            contentType: "application/json",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            },
            data: datos
        });
        peticion.done((response) => {
            let respuesta = '';
            if (response && response.respuesta) {
                respuesta = response.respuesta;
            } else if (response && response.error) {
                respuesta = response.error;
            } else {
                respuesta = this.t['error'];
            }
            control.verMensaje(respuesta, 'aviso' );
            jQuery("#zona_espera").hide();
            jQuery("#zona_contenido").show();
            });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
            jQuery("#zona_contenido").show();
        });
        return false;
    }

    confirmarVaciado(carpeta, id) {
        let html = jQuery('#confirmar_vaciado').html();
        html = html.replace('((carpeta))', carpeta);
        html = html.replace('((id_recurso))', id);
        control.abrirVentana(html);
    }

    buscarBiblioteca() {
        var con_carpeta = jQuery( '#con_carpeta' );
        var con_buscar = jQuery( '#con_buscar' );
        if (this.carpeta && con_carpeta.val()=='') {
            con_carpeta.val(this.carpeta);
        } else {
            this.carpeta = con_carpeta.val();
        }
        if (con_buscar.val() == '') {
            control.verMensaje( this.t['sin_buscar'], 'aviso');
            control.activarBuscador('con_buscar');
            return false;
        }
        var opciones = document.getElementById('div_opciones');
        var cerrar = new bootstrap.Collapse(opciones, {
            toggle: false
        });
        cerrar.hide();
        var datos = jQuery( '#form_buscar' ).serialize();
        jQuery("#lista_resultados").hide();
        jQuery("#lista_destacados").hide();
        jQuery("#zona_espera").show();
        con_buscar.val('');
        const peticion = jQuery.ajax({
            type: "POST",
            url: control.ruta_base + "/biblioteca",
            data: datos,
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((respuesta) => {
            var destino = jQuery( '#lista_resultados' );
            destino.html( respuesta );
            jQuery("#zona_espera").hide();
            destino.show();
            control.resaltarPalabras();
            jQuery("#volver_buscar").focus();
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            jQuery("#lista_resultados").show();
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    verTrozo(id) {
        jQuery('.trozo').each(function() {
            jQuery(this).hide();
        });
        jQuery('#tr_' + id).fadeIn();
    }

    volverBuscar() {
        var buscar = jQuery( '#con_buscar' );
        var texto = jQuery( '#texto_buscar' );
        buscar.val(texto.val());
        buscar.focus();
        jQuery(window).scrollTop( jQuery( '#form_buscar' ).position().top);
    }

    copiarTexto(zona) {
        let texto = jQuery('#' + zona).text();
        texto = texto.replace(/^\s+/gm, '').replace(/\s{2,}/g, ' ').replace(/\n\s*\n/g, '\n');
        let auxiliar = jQuery('<textarea>');
        auxiliar.val(texto).appendTo('body').select();
        document.execCommand('copy');
        auxiliar.remove();
        if (jQuery('#texto_copiado').length) {
            jQuery('#texto_copiado').show();
        } else if (jQuery('#transcripcion_copiada').length) {
            jQuery('#transcripcion_copiada').show();
        }
    }

    resaltarPalabras() {
        const texto = jQuery('#texto_buscar').val();
        if (!texto) {return false;}
        const palabras = texto.split(/\s+/).filter(palabra => palabra.length >= 4);
        const palabrasEscapadas = palabras.map(palabra => palabra.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
        const regex = new RegExp(`\\b(${palabrasEscapadas.join('|')})\\b`, 'gi');
        jQuery('.resaltar').each(function() {
            const contenido = jQuery(this);
            const texto_contenido = contenido.text();
            const texto_resaltado = texto_contenido.replace(regex, (match) => {
                if (palabras.includes(match.toLowerCase())) {
                    return '<b>' + match + '</b>';
                } else {
                    return match;
                }
            });
            contenido.html(control.reemplazarURLs(texto_resaltado));
        });
    }

    reemplazarURLs(texto) {
        const regex = /(https?:\/\/\S+)/gi;
        const contenido = texto.replace(regex, '<a href="$&" target="_blank" class="text-secondary">$&</a>');
        return contenido;
    }

    enviarBusqueda() {
        var texto = jQuery( '#texto_buscar' );
        var imagen_espera = jQuery("#mostrar_espera");
        var area_respuesta = jQuery("#mostrar_respuesta");
        var texto_respuesta = jQuery("#texto_respuesta");
        jQuery("#pedir_respuesta").fadeOut();
		imagen_espera.fadeIn();
        const datos = JSON.stringify({ "buscar": texto.val(), "carpeta": this.carpeta });
        const peticion = jQuery.ajax({
            type: "PUT",
            url: control.ruta_base + "/biblioteca",
            dataType: "json",
            contentType: "application/json",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            },
            data: datos
        });
        peticion.done((response) => {
			imagen_espera.hide();
            var respuesta_recibida = '';
			if (response && response.respuesta) {
                respuesta_recibida = response.respuesta;
			} else if (response && response.error) {
                respuesta_recibida = response.error;
			}
            area_respuesta.fadeIn();
            jQuery.each(respuesta_recibida.split(""), function(i, letter) {
                setTimeout(function() {
                    texto_respuesta.html(texto_respuesta.html() + letter);
                    if (respuesta_recibida.length == texto_respuesta.html().length) {
                        jQuery( '#copiar_texto' ).show();
                    }
                }, 35 * i);
            });
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            mensaje = control.mostrarError( jqXHR, estado, mensaje );
			imagen_espera.hide();
            texto_respuesta.html(mensaje);
            area_respuesta.show();
        });
    }

    importarMetadatos(carpeta) {
        if (!carpeta) {
            carpeta = this.carpeta;
        }
        this.carpeta = carpeta;
        const peticion = jQuery.ajax({
            type: "GET",
            data: "carpeta=" + encodeURIComponent(carpeta),
            url: control.ruta_base + "/importar",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((respuesta) => {
            control.abrirVentana(respuesta);
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
        });
    }

    exportarMetadatos(carpeta) {
        if (!carpeta) {
            carpeta = this.carpeta;
        }
        this.carpeta = carpeta;
        let url = control.ruta_base + "/exportar/" + encodeURIComponent(carpeta);
        window.open( url, '_blank' );

    }

    indexarDocumento(carpeta, id) {
        if (!carpeta) {
            carpeta = this.carpeta;
        }
        this.carpeta = carpeta;
        if (!id) {
            id = '';
        }
        const datos = JSON.stringify({ "carpeta": this.carpeta, "doc": id });
        jQuery('.alert').each(function() {
            jQuery(this).hide();
        });
        jQuery("#zona_espera").show();
        jQuery("#zona_contenido").hide();
        const peticion = jQuery.ajax({
            type: "POST",
            url: control.ruta_base + "/indexar",
            dataType: "json",
            contentType: "application/json",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            },
            data: datos
        });
        peticion.done((response) => {
            let respuesta = '';
            if (response && response.respuesta) {
                respuesta = response.respuesta;
            } else if (response && response.error) {
                respuesta = response.error;
            } else {
                respuesta = this.t['error'];
            }
            control.verMensaje(respuesta, 'aviso' );
            jQuery("#zona_espera").hide();
            jQuery("#zona_contenido").show();
            });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
            jQuery("#zona_contenido").show();
        });
        return false;
    }

    async importarExcel(form) {
        const formData = new FormData(form);
        try {
            const archivo = formData.get('archivo');
            const tiposPermitidos = [
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            ];
            if (!tiposPermitidos.includes(archivo.type)) {
                jQuery("#ventana_error").html( this.t['excel_novalido']).show();
                return false;
            }
            jQuery("#form_excel_subir").hide();
            jQuery("#form_excel_botones").hide();
            jQuery("#form_excel_espera").show();
            const response = await fetch(control.ruta_base + '/importar', {
                method: 'POST',
                beforeSend: function (xhr) {
                    var token = leerCookie('token');
                    var id_sesion = leerCookie('id_sesion');
                    xhr.setRequestHeader('id_sesion', id_sesion);
                    xhr.setRequestHeader('token', token);
                    xhr.setRequestHeader('app', control.app);
                },
                body: formData
            });
            const jsonResponse = await response.json();
            if ( jsonResponse.respuesta ) {
                jQuery("#form_excel_espera").hide();
                control.cerrarVentana();
                control.mostrarRespuesta( jsonResponse );
            }
            if ( jsonResponse.error ) {
                jQuery("#form_excel_espera").hide();
                control.cerrarVentana();
                control.verMensaje( this.t['error_excel'], 'error' );
            }
        } catch (error) {
            jQuery("#form_excel_espera").hide();
            control.cerrarVentana();
            control.verMensaje( this.t['error_excel'], 'error' );
        }
    }

    consultarDestacados() {
        const peticion = jQuery.ajax({
            type: "GET",
            url: control.ruta_base + "/destacados",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((respuesta) => {
            var destino = jQuery( '#lista_destacados' );
            destino.html( respuesta );
            destino.fadeIn();
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    consultarPlantillas(nav) {
        if (!nav) {
            nav = this.nav;
        }
        this.nav = nav;
        jQuery( '#con_nav' ).val(this.nav);
        this.total = 0;
        this.paginas = 0;
        var datos = jQuery( '#form_plantillas' ).serialize();
        jQuery("#zona_contenido").hide();
        jQuery("#zona_espera").show();
        const peticion = jQuery.ajax({
            type: "GET",
            url: control.ruta_base + "/plantillas",
            data: datos,
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((respuesta) => {
            var destino = jQuery( '#zona_contenido' );
            destino.html( respuesta );
            jQuery("#zona_espera").hide();
            destino.show();
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            jQuery("#zona_contenido").show();
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    borrarPlantilla(id) {
        const peticion = jQuery.ajax({
            type: "DELETE",
            url: control.ruta_base + "/plantilla/" + id,
            dataType: "json",
            contentType: "application/json",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((respuesta) => {
            control.mostrarRespuesta( respuesta );
            control.consultarPlantillas( control.nav );
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    editarPlantilla(id) {
        var caso = jQuery( '#pla_'+ id );
        caso.removeClass( 'mark' );
        caso.addClass( 'mark' );
        const peticion = jQuery.ajax({
            type: "GET",
            url: control.ruta_base + "/plantilla/" + id,
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((respuesta) => {
            control.abrirModal(respuesta);
            jQuery('#form_editar_plantilla .auto-resize').on('input', function() {
                this.style.height = 'auto';
                this.style.height = (this.scrollHeight) + 'px';
                var maxHeight = 400;
                if (this.scrollHeight > maxHeight) {
                    this.style.height = maxHeight + 'px';
                    this.style.overflowY = 'auto';
                }
                if (this.value.length === 0) {
                    this.style.height = 'auto';
                }
            });
            var c_peticion = jQuery('#peticion').val();
            var c_intro = jQuery('#intro').val();
            var c_texto = jQuery('#texto').val();
            var c_config = jQuery('#config').val();
            c_intro = c_intro.replace(/\|/g, "\n");
            c_peticion = c_peticion.replace(/\|/g, "\n");
            c_texto = c_texto.replace(/\|/g, "\n");
            jQuery('#intro').val(c_intro);
            jQuery('#peticion').val(c_peticion);
            jQuery('#texto').val(c_texto);
            let config = c_config.split('|');
            if (config.length==3) {
                jQuery('#lenguaje').val(config[0]);
                jQuery('#estilo').val(config[1]);
                jQuery('#tono').val(config[2]);
            }
            control.iniciarTips();
            var modal = document.getElementById('INT_MODAL');
            if (jQuery('#config').length) {
                modal.addEventListener('shown.bs.modal', function () {
                    jQuery('#intro').trigger('input');
                    jQuery('#peticion').trigger('input');
                    jQuery('#texto').trigger('input');
                });
            }
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    nuevaPlantilla(datos) {
        const peticion = jQuery.ajax({
            type: "POST",
            url: control.ruta_base + "/plantillas",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            },
            data: datos
        });
        peticion.done((respuesta) => {
            control.abrirModal(respuesta);
            jQuery('#form_editar_plantilla .auto-resize').on('input', function() {
                this.style.height = 'auto';
                this.style.height = (this.scrollHeight) + 'px';
                var maxHeight = 400;
                if (this.scrollHeight > maxHeight) {
                    this.style.height = maxHeight + 'px';
                    this.style.overflowY = 'auto';
                }
                if (this.value.length === 0) {
                    this.style.height = 'auto';
                }
            });
            control.iniciarTips();
            var modal = document.getElementById('INT_MODAL');
            modal.addEventListener('shown.bs.modal', function () {
                if (jQuery('#config').length) {
                    let c_config = jQuery('#config').val();
                    let config = c_config.split('|');
                    if (config.length==3) {
                        jQuery("#form_editar_campos select[name='lenguaje']").val(config[0]);
                        jQuery("#form_editar_campos select[name='estilo']").val(config[1]);
                        jQuery("#form_editar_campos select[name='tono']").val(config[2]);
                    }
                    jQuery('#intro').trigger('input');
                    jQuery('#peticion').trigger('input');
                    jQuery('#texto').trigger('input');
                }
            });
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    iniciarTips() {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
          return new bootstrap.Tooltip(tooltipTriggerEl)
        });
    }

    guardarPlantilla(modo, id) {
        let lenguaje = jQuery("#form_editar_campos select[name='lenguaje']").val();
        let estilo = jQuery("#form_editar_campos select[name='estilo']").val();
        let tono = jQuery("#form_editar_campos select[name='tono']").val();
        jQuery("#form_editar_plantilla input[name='config']").val( lenguaje + '|' + estilo + '|' + tono);
        var datos = jQuery( '#form_editar_plantilla' ).serialize();
        jQuery("#form_editar_campos").hide();
        jQuery("#form_editar_botones").hide();
        jQuery("#form_editar_espera").show();
        var peticion = null;
        if (modo=='nueva') {
            peticion = jQuery.ajax({
                type: "POST",
                url: control.ruta_base + "/plantilla",
                data: datos,
                beforeSend: function (xhr) {
                    var token = leerCookie('token');
                    var id_sesion = leerCookie('id_sesion');
                    xhr.setRequestHeader('id_sesion', id_sesion);
                    xhr.setRequestHeader('token', token);
                    xhr.setRequestHeader('app', control.app);
                }
            });
        } else {
            peticion = jQuery.ajax({
                type: "PUT",
                url: control.ruta_base + "/plantilla/" + id,
                data: datos,
                beforeSend: function (xhr) {
                    var token = leerCookie('token');
                    var id_sesion = leerCookie('id_sesion');
                    xhr.setRequestHeader('id_sesion', id_sesion);
                    xhr.setRequestHeader('token', token);
                    xhr.setRequestHeader('app', control.app);
                }
            });
        }
        peticion.done((respuesta) => {
            jQuery("#form_editar_espera").hide();
            control.cerrarModal();
            control.mostrarRespuesta( respuesta );
            var plantillas = jQuery("#seccion_plantillas");
            if (plantillas.length) {
                control.abrirMenu('plantillas');
            }
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            jQuery("#form_editar_espera").hide();
            jQuery("#form_editar_campos").show();
            jQuery("#form_editar_botones").show();
            control.mostrarError( jqXHR, estado, mensaje );
        });
        return false;
    }

    cerrarTranscripcion() {
        jQuery('#mostrar_transcripcion').fadeOut();
        jQuery('#transcripcion_copiada').hide();
        jQuery('#transcripcion').html('');
    }

    calcularTiempoRestante(hora_inicio) {
        if (control.grabando == false) { return "0:0"; }
        var total_minutos = control.max_minutos;
        if (total_minutos > 0) { total_minutos = total_minutos - 1; }
        var hora_actual = new Date().getTime();
        var diferencia = hora_actual - hora_inicio;
        var minutos = total_minutos - Math.floor((diferencia % (1000 * 60 * 60)) / (1000 * 60));
        var segundos = 59 - Math.floor((diferencia % (1000 * 60)) / 1000);
        return minutos + ":" + segundos;
    }
    
    actualizarTiempoRestante(hora_inicio) {
        if (control.grabando == true) {
            var tiempoRestante = control.calcularTiempoRestante(hora_inicio);
            jQuery("#tiempo_restante").html(tiempoRestante);
        }
    }
    
    iniciarTemporizador(hora_inicio) {
        control.actualizarTiempoRestante(hora_inicio);
        var intervalo = setInterval(function() {
            control.actualizarTiempoRestante(hora_inicio);
            if (control.calcularTiempoRestante(hora_inicio) === "0:0") {
                clearInterval(intervalo);
            }
        }, 500);
    }
    
    ingresarAudio() {
        const peticion = jQuery.ajax({
            type: "GET",
            url: control.ruta_base + "/audio",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((respuesta) => {
            respuesta = respuesta.replace('((max_minutos))', String(control.max_minutos));
            respuesta = respuesta.replace('((max_mb_audio))', String(control.max_mb_audio));
            control.abrirModal(respuesta);
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.mostrarError( jqXHR, estado, mensaje );
        });
    }

    grabarAudio() {
        jQuery('#boton_grabar').hide();
        jQuery('#form_audio').hide();
        jQuery('#form_grabacion_botones').hide();
        jQuery('#boton_detener').show();
        control.chunks = [];
        navigator.mediaDevices.getUserMedia({ audio: true, video: false })
        .then((stream) => {
            const options = {mimeType: 'audio/webm'};
            control.mediaRecorder = new MediaRecorder(stream, options);
            control.mediaRecorder.start();
            control.mediaRecorder.addEventListener('dataavailable', (e) => {
                if (e.data.size > 0) {
                    control.chunks.push(e.data);
                }
                if (control.mediaRecorder.state == "inactive") {
                    let blob = new Blob(control.chunks, { type: "audio/webm" });
                    let reproductor = document.getElementById("reproductor_audio");
                    reproductor.src = URL.createObjectURL(blob);
                    reproductor.controls = true;
                    reproductor.autoplay = false;
                }
            });
        })
        .catch((err) => {
            control.verMensaje(control.t['sin_audio'] + '\n' + err, 'error');
            return;
        });
        control.grabando = true;
        let hora_inicio = new Date().getTime();
        control.iniciarTemporizador(hora_inicio);
        setTimeout(() => {
            control.detenerGrabacion();
        }, ((control.max_minutos * 60) + 1) * 1000);
        jQuery('#tiempo_restante').html(control.tiempo_restante);
        jQuery('#temporizador').show();
    }

    detenerGrabacion() {
        if (control.grabando == true) {
            control.mediaRecorder.stop();
            jQuery('#boton_detener').hide();
            jQuery('#temporizador').hide();
            jQuery('#boton_grabar').hide();
            jQuery('#form_grabacion_botones').show();
            control.grabando = false;
        }
    }

    enviarAudio() {
        jQuery("#form_audio").hide();
        jQuery("#form_grabacion").hide();
        jQuery("#form_audio_espera").show();
        let blob = new Blob(control.chunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('audio', blob, control.archivo_audio + '.webm');
        const peticion = jQuery.ajax({
            type: 'POST',
            url: control.ruta_base + "/audio",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                var id_sesion = leerCookie('id_sesion');
                xhr.setRequestHeader('id_sesion', id_sesion);
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            },
            data: formData,
            processData: false,
            contentType: false
        });
        peticion.done((respuesta) => {
            jQuery("#form_audio_espera").hide();
            control.cerrarModal();
            jQuery('#transcripcion').text(respuesta.texto);
            jQuery('#mostrar_transcripcion').fadeIn();
            jQuery('#mostrar_transcripcion').fadeIn();
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            jQuery("#form_audio_espera").hide();
            control.cerrarModal();
            control.mostrarError( jqXHR, estado, mensaje );
        });
    }

    async subirAudio(form) {
        const formData = new FormData(form);
        try {
            const audio = formData.get('audio');
            const tiposPermitidos = [
                'audio/webm',
                'audio/wav',
                'audio/mpeg',
                'audio/m4a'
            ];
            if (!tiposPermitidos.includes(audio.type)) {
                jQuery("#audio_error").html( this.t['audio_novalido']).show();
                return false;
            }
            const validacion = this.validarAudio(audio);
            if (!validacion.valido) {
                jQuery("#audio_error").html(validacion.mensaje).show();
                return false;
            }
            jQuery("#form_audio").hide();
            jQuery("#form_grabacion").hide();
            jQuery("#form_audio_espera").show();
            const response = await fetch(control.ruta_base + '/audio', {
                method: 'POST',
                beforeSend: function (xhr) {
                    var token = leerCookie('token');
                    var id_sesion = leerCookie('id_sesion');
                    xhr.setRequestHeader('id_sesion', id_sesion);
                    xhr.setRequestHeader('token', token);
                    xhr.setRequestHeader('app', control.app);
                },
                body: formData
            });
            const jsonResponse = await response.json();
            if ( jsonResponse.texto ) {
                jQuery("#form_audio_espera").hide();
                control.cerrarModal();
                jQuery('#transcripcion').text(jsonResponse.texto);
                jQuery('#mostrar_transcripcion').fadeIn();
            }
            if ( jsonResponse.error ) {
                jQuery("#form_audio_espera").hide();
                control.cerrarModal();
                control.verMensaje( this.t['error_audio'], 'error' );
            }
        } catch (error) {
            jQuery("#form_audio_espera").hide();
            control.cerrarModal();
            control.verMensaje( this.t['error_audio'], 'error' );
        }
    }

}

function leerCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
}

// Script de ejecución: Crea una instancia del Controlador para todo el front-end
var control = new Controlador();
