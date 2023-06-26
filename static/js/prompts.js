/* prompts.js
******************************************************
CHAT EXPERTO (Front-end) - Actualizado el: 26/06/2023
******************************************************
Clase: Prompts */

class Prompts {

    constructor() {
        this.chunks = [];
        this.mediaRecorder = null;
        this.tiempo_grabacion = 180;
        this.archivo_audio = 'audio-guardado';
        this.misprompts = [];
        this.misprompts['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono))((palabras)).|Usa como base el siguiente texto:|"""|((texto))|"""';
    }

    iniciarFormularios() {
        jQuery('.auto-resize').on('input', function() {
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
        jQuery('#input-mensaje-usuario').on('input', function() {
            var numero = jQuery(this).val().length;
            jQuery('#num_caracteres').html(numero);
        });
    }

    elegirTarea() {
        var tarea = jQuery('#tarea').val();
        jQuery('.form-prompt').each(function() {
            jQuery(this).hide();
        });
        if (tarea.length > 0) {
            jQuery('#form-' + tarea).fadeIn();
            jQuery('#generar_prompt').fadeIn();
            jQuery('#guardar_como').fadeIn();
        }
    }

    enviarConsulta() {
        var input_mensaje_usuario = jQuery('#input-mensaje-usuario');
        var imagen_espera = jQuery("div#chat-imagen-espera");
        var mensajes_conversacion = jQuery("div#chat-mensajes-conversacion");
        var caja_enviar_mensaje = jQuery("div#chat-enviar-mensaje");
        var pie_chat = jQuery('div#pie-prompts' );
        var advertencia = jQuery('div#prompt-advertencia' );
		let consulta = input_mensaje_usuario.val();
		if ( consulta.length < 10 ) { return; }
		advertencia.hide();
		caja_enviar_mensaje.hide();
		imagen_espera.show();
        jQuery(window).scrollTop( pie_chat.position().top);
		const datos = JSON.stringify( jQuery( '#form-chat-enviar' ).serializeJSON() );
        const peticion = jQuery.ajax({
            type: "POST",
            url: control.ruta_base + "/prompts",
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
            input_mensaje_usuario.trigger('input');
			caja_enviar_mensaje.show();
			input_mensaje_usuario.focus();
			if (response && response.peticion && response.respuesta) {
                let html = jQuery("div#chat-plantilla-consulta").html();
                if (consulta.includes('"""')) {
                    consulta = consulta.substring(0, consulta.indexOf('"""'));
                }
                consulta = consulta.replace(/\n/g, ' ');
                html = html.replace('((consulta))', consulta );
                mensajes_conversacion.append(html);
                html = jQuery("div#chat-plantilla-respuesta").html();
                let respuesta = response.respuesta;
                respuesta = respuesta.replace(/\n/g, "<br>");
				html = html.replace('((respuesta))', respuesta);
				mensajes_conversacion.append(html);
			} else if (response && response.respuesta) {
                let html = jQuery("div#chat-plantilla-consulta").html();
                if (consulta.includes('"""')) {
                    consulta = consulta.substring(0, consulta.indexOf('"""'));
                }
                consulta = consulta.replace(/\n/g, ' ');
                html = html.replace('((consulta))', consulta );
                mensajes_conversacion.append(html);
				html = jQuery("div#chat-plantilla-respuesta").html();
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

    copiarCampo(campo) {
        var texto = jQuery('#' + campo).val();
        var tempElement = jQuery('<textarea>');
        tempElement.val(texto).appendTo('body').select();
        document.execCommand('copy');
        tempElement.remove();
    }

    limpiarPrompt() {
        jQuery('#prompt-advertencia').hide();
        jQuery('#input-mensaje-usuario').val('');
        jQuery('#input-mensaje-usuario').trigger('input');
        jQuery('#input-mensaje-usuario').focus();
    }

    confirmarVaciado() {
        let html = jQuery('#confirmar_vaciado').html();
        control.abrirVentana(html);
    }

    vaciarConversacion() {
        const peticion = jQuery.ajax({
            type: "DELETE",
            url: control.ruta_base + "/prompts",
            dataType: "json",
            contentType: "application/json",
            beforeSend: function (xhr) {
                var token = leerCookie('token');
                xhr.setRequestHeader('token', token);
                xhr.setRequestHeader('app', control.app);
            }
        });
        peticion.done((response) => {
            control.cerrarVentana();
            control.mostrarRespuesta( response );
            jQuery("div#historial").hide();
            jQuery("div#titulo_historial").hide();
        });
        peticion.fail((jqXHR, estado, mensaje) => {
            control.cerrarVentana();
            control.mostrarError( jqXHR, estado, mensaje );
        });

    }

    limpiarCampos(tarea) {
        jQuery('#' + tarea + '-intro').val('');
        jQuery('#' + tarea + '-peticion').val('');
        jQuery('#' + tarea + '-texto').val('');
        jQuery('#' + tarea + '-intro').trigger('input');
        jQuery('#' + tarea + '-peticion').trigger('input');
        jQuery('#' + tarea + '-texto').trigger('input');
    }

    usarPlantilla(campo) {
        var tipo = jQuery('#' + campo).val();
        var tarea = jQuery('#tarea').val();
        var peticion = '';
        var intro = '';
        var texto = '';
        var config = '';
        if (this.misprompts[tipo]) {
            intro = this.misprompts[tipo]['intro'];
            peticion = this.misprompts[tipo]['peticion'];
            texto = this.misprompts[tipo]['texto'];
            config = this.misprompts[tipo]['config'];
        } else {
            control.verMensaje('No se encontró la plantilla: ' + tipo, 'error');
        }
        intro = intro.replace(/\|/g, "\n");
        peticion = peticion.replace(/\|/g, "\n");
        texto = texto.replace(/\|/g, "\n");
        jQuery('#' + tarea + '-intro').val(intro);
        jQuery('#' + tarea + '-peticion').val(peticion);
        jQuery('#' + tarea + '-texto').val(texto);
        jQuery('#' + tarea + '-intro').trigger('input');
        jQuery('#' + tarea + '-peticion').trigger('input');
        jQuery('#' + tarea + '-texto').trigger('input');
        let datos = config.split('|');
        if (datos.length==3) {
            jQuery('#lenguaje').val(datos[0]);
            jQuery('#estilo').val(datos[1]);
            jQuery('#tono').val(datos[2]);
        }
    }

    generarPrompt() {
        var tarea = jQuery('#tarea').val();
        var estilo = jQuery('#estilo').val();
        var tono = jQuery('#tono').val();
        var lenguaje = jQuery('#lenguaje').val();
        var idioma = jQuery('#idioma').val();
        var palabras = jQuery('#palabras').val();
        if (palabras.length >0) {
            palabras = ', en un máximo de ' + palabras + ' palabras o menos';
        }
        var prompt = this.misprompts['prompt'];
        let intro = jQuery('#' + tarea + '-intro').val();
        let peticion = jQuery('#' + tarea + '-peticion').val();
        let texto = jQuery('#' + tarea + '-texto').val();
        prompt = prompt.replace(/\|/g, "\n");
        prompt = prompt.replace('((intro))', intro);
        prompt = prompt.replace('((peticion))', peticion);
        prompt = prompt.replace('((texto))', texto);
        prompt = prompt.replace('((estilo))', estilo);
        prompt = prompt.replace('((tono))', tono);
        prompt = prompt.replace('((lenguaje))', lenguaje);
        prompt = prompt.replace('((idioma))', idioma);
        prompt = prompt.replace('((palabras))', palabras);
        jQuery('div#prompt-advertencia' ).show();
        jQuery('#input-mensaje-usuario').val(prompt);
        jQuery('#input-mensaje-usuario').trigger('input');
        jQuery(window).scrollTop( jQuery('div#pie-prompts' ).position().top);
    }

    formularioMarcas() {
        var tarea = jQuery('#tarea').val();
        var texto = jQuery('#' + tarea + '-texto').val();
        var plantilla = jQuery('#formulario_marcas');
        var formulario = jQuery('#form-marcas');
        var regex = /\(\((.*?)\)\)/g;
        var campos = [];
        var match;
        while ((match = regex.exec(texto)) !== null) {
          campos.push(match[1]);
        }
        formulario.html('');
        campos.forEach( function(campo) {
            let id = campo.toLowerCase().replace(/\s/g, '-');
            let etiqueta = campo.replace(/-/g, ' ');
            etiqueta = etiqueta.charAt(0).toUpperCase() + etiqueta.slice(1);
            let input = jQuery("div#campo_marca").html();
            input = input.replace(/idcampo/g, id);
            input = input.replace(/etiqueta/g, etiqueta);
            if (texto.includes('(('+ id + '))')) {
                formulario.append(input);
            }
        });
        let html = plantilla.html();
        control.abrirModal(html);
        jQuery('#form-marcas .auto-resize').on('input', function() {
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
    }

    reemplazarMarcas() {
        var tarea = jQuery('#tarea').val();
        var texto = jQuery('#' + tarea + '-texto').val();
        jQuery('textarea.form-marca').each( function() {
            let area = jQuery(this);
            let nombre = area.attr('name');
            let valor = area.val();
            if (valor.length >0) {
                texto = prompts.reemplazarTextoMarca(texto, nombre, valor);
            }
        });
        jQuery('#' + tarea + '-texto').val(texto);
        control.cerrarModal();
    }

    reemplazarTextoMarca(completa, buscada, reemplazo) {
        var regex = new RegExp('\\(\\(' + buscada + '\\)\\)', 'g');
        return completa.replace(regex, reemplazo);
    }

    formularioClaves() {
        var tarea = jQuery('#tarea').val();
        var texto = jQuery('#' + tarea + '-peticion').val();
        var plantilla = jQuery('#formulario_claves');
        var formulario = jQuery('#form-claves');
        var regex = /\(\((.*?)\)\)/g;
        var campos = [];
        var match;
        while ((match = regex.exec(texto)) !== null) {
          campos.push(match[1]);
        }
        formulario.html('');
        campos.forEach( function(campo) {
            let id = campo.toLowerCase().replace(/\s/g, '-');
            let etiqueta = campo.replace(/-/g, ' ');
            etiqueta = etiqueta.charAt(0).toUpperCase() + etiqueta.slice(1);
            let input = jQuery("div#campo_clave").html();
            input = input.replace(/idcampo2/g, id);
            input = input.replace(/etiqueta2/g, etiqueta);
            if (texto.includes('(('+ id + '))')) {
                formulario.append(input);
            }
        });
        let html = plantilla.html();
        control.abrirModal(html);
        jQuery('#form-claves .auto-resize').on('input', function() {
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
    }

    reemplazarClaves() {
        var tarea = jQuery('#tarea').val();
        var texto = jQuery('#' + tarea + '-peticion').val();
        jQuery('textarea.form-clave').each( function() {
            let area = jQuery(this);
            let nombre = area.attr('name');
            let valor = area.val();
            if (valor.length >0) {
                texto = prompts.reemplazarTextoMarca(texto, nombre, valor);
            }
        });
        jQuery('#' + tarea + '-peticion').val(texto);
        control.cerrarModal();
    }

    guardarChat() {
        let url = control.ruta_base + "/guardarchat";
        window.open( url, '_blank' );
    }

    guardarComo() {
        let tarea = jQuery('#tarea').val();
        let estilo = jQuery('#estilo').val();
        let tono = jQuery('#tono').val();
        let lenguaje = jQuery('#lenguaje').val();
        let intro = jQuery('#' + tarea + '-intro').val();
        let peticion = jQuery('#' + tarea + '-peticion').val();
        let texto = jQuery('#' + tarea + '-texto').val();
        const datos = { 
            "tarea": tarea, 
            "config": lenguaje + '|' + estilo + '|' + tono, 
            "intro": intro, 
            "peticion": peticion, 
            "texto": texto
        };
        control.nuevaPlantilla(datos);
    }

    grabarAudio() {
        if (jQuery('#grabar_audio').hasClass('recording')) {
            jQuery('#grabar_audio').removeClass('recording');
            jQuery('#grabar_audio').text('Iniciar grabación');
            this.detenerGrabacion();
        } else {
            jQuery('#grabar_audio').addClass('recording');
            jQuery('#grabar_audio').text('Detener grabación');
            this.chunks = [];
            this.comenzarGrabacion();
            setTimeout(() => {
                this.detenerGrabacionAuto();
            }, this.tiempo_grabacion * 1000);
        }
    }

    comenzarGrabacion() {
        navigator.mediaDevices.getUserMedia({ audio: true })
        .then((stream) => {
            this.mediaRecorder = new MediaRecorder(stream);
            this.mediaRecorder.start();
            this.mediaRecorder.addEventListener('dataavailable', (e) => {
                this.chunks.push(e.data);
            });
        })
        .catch((err) => {
            console.error('Error al acceder al dispositivo de audio: ', err);
        });
    }

    detenerGrabacion() {
        this.mediaRecorder.stop();
    }

    reproducirGrabacion() {
        const blob = new Blob(this.chunks, { type: 'audio/mp3' });
        const audioURL = URL.createObjectURL(blob);
        jQuery('#reproducir_audio').attr('src', audioURL);
    }

    detenerGrabacionAuto() {
        if (jQuery('#grabar_audio').hasClass('recording')) {
            jQuery('#grabar_audio').removeClass('recording');
            jQuery('#grabar_audio').text('Iniciar grabación');
            this.detenerGrabacion();
        }
    }

    enviarAudio() {
        this.reproducirGrabacion();
        const blob = new Blob(this.chunks, { type: 'audio/mp3' });
        const formData = new FormData();
        formData.append('audio', blob, this.archivo_audio + '.mp3');
        jQuery.ajax({
            url: '/audio',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: (response) => {
                console.log('Archivo de audio enviado con éxito.');
            },
            error: (error) => {
                console.error('Error al enviar el archivo de audio: ', error);
            }
        });
    }

}

var prompts = new Prompts();
