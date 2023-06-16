/* prompts.js
******************************************************
CHAT EXPERTO (Front-end) - Actualizado el: 16/06/2023
******************************************************
Clase: Prompts */

class Prompts {

    constructor() {
        this.informe = [];
        this.articulo = [];
        this.noticia = [];
        this.presentacion = [];
        this.guion = [];
        this.aviso = [];
        this.correo = [];
        this.preguntas = [];
        this.texto = [];
        this.instrucciones = [];
        this.ideas = [];
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
        }
    }

    enviarConsulta() {
        var input_mensaje_usuario = jQuery('#input-mensaje-usuario');
        var imagen_espera = jQuery("div#chat-imagen-espera");
        var mensajes_conversacion = jQuery("div#chat-mensajes-conversacion");
        var caja_enviar_mensaje = jQuery("div#chat-enviar-mensaje");
        var pie_chat = jQuery('div#pie-prompts' );
		let consulta = input_mensaje_usuario.val();
		if ( consulta.length < 10 ) { return; }
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

    copiarPrompt() {
        var texto = jQuery('#input-mensaje-usuario').val();
        var tempElement = jQuery('<textarea>');
        tempElement.val(texto).appendTo('body').select();
        document.execCommand('copy');
        tempElement.remove();
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

    //TODO: Completar
    limpiarCampos(tarea) {
        if (tarea == 'informe') {
            jQuery('#informe-intro').val('');
            jQuery('#informe-peticion').val('');
            jQuery('#informe-texto').val('');
            jQuery('#informe-intro').trigger('input');
            jQuery('#informe-peticion').trigger('input');
            jQuery('#informe-texto').trigger('input');
        }
    }

    //TODO: Completar
    usarPlantilla(campo) {
        var tipo = jQuery('#' + campo).val();
        var tarea = jQuery('#tarea').val();
        if (tarea == 'informe') {
            if (this.informe[tipo]) {
                jQuery('#informe-intro').val( this.informe[tipo]['intro'] );
                let peticion = this.informe[tipo]['peticion'];
                peticion = peticion.replace(/\|/g, "\n");
                jQuery('#informe-peticion').val(peticion);
                let texto = this.informe[tipo]['texto'];
                texto = texto.replace(/\|/g, "\n");
                jQuery('#informe-texto').val(texto);
                jQuery('#informe-intro').trigger('input');
                jQuery('#informe-peticion').trigger('input');
                jQuery('#informe-texto').trigger('input');
            }
            else {
                control.verMensaje('No se encontró la plantilla: ' + tipo, 'error');
            }
        }
    }

    //TODO: Completar
    generarPrompt() {
        var tarea = jQuery('#tarea').val();
        var estilo = jQuery('#estilo').val();
        var tono = jQuery('#tono').val();
        var lenguaje = jQuery('#lenguaje').val();
        var prompt = '';
        if (tarea == 'informe') {
            let intro = jQuery('#informe-intro').val();
            let peticion = jQuery('#informe-peticion').val();
            let texto = jQuery('#informe-texto').val();
            prompt = this.informe['prompt'];
            prompt = prompt.replace(/\|/g, "\n");
            prompt = prompt.replace('((intro))', intro);
            prompt = prompt.replace('((peticion))', peticion);
            prompt = prompt.replace('((texto))', texto);
        }
        prompt = prompt.replace('((estilo))', estilo);
        prompt = prompt.replace('((tono))', tono);
        prompt = prompt.replace('((lenguaje))', lenguaje);
        jQuery('#input-mensaje-usuario').val(prompt);
        jQuery('#input-mensaje-usuario').trigger('input');
        jQuery(window).scrollTop( jQuery('div#pie-prompts' ).position().top);
    }

}

var prompts = new Prompts();
