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
        this.propuesta = [];
        this.informe['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono)).|Usa como base el siguiente texto:|"""|((texto))|"""';
        this.articulo['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono)).|Usa como base el siguiente texto:|"""|((texto))|"""';
        this.noticia['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono)).|Usa como base el siguiente texto:|"""|((texto))|"""';
        this.presentacion['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono)).|Usa como base el siguiente texto:|"""|((texto))|"""';
        this.guion['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono)).|Usa como base el siguiente texto:|"""|((texto))|"""';
        this.aviso['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono)).|Usa como base el siguiente texto:|"""|((texto))|"""';
        this.correo['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono)).|Usa como base el siguiente texto:|"""|((texto))|"""';
        this.preguntas['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono)).|Usa como base el siguiente texto:|"""|((texto))|"""';
        this.texto['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono)).|Usa como base el siguiente texto:|"""|((texto))|"""';
        this.instrucciones['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono)).|Usa como base el siguiente texto:|"""|((texto))|"""';
        this.ideas['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono)).|Usa como base el siguiente texto:|"""|((texto))|"""';
        this.propuesta['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono)).|Usa como base el siguiente texto:|"""|((texto))|"""';
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

    copiarCampo(campo) {
        var texto = jQuery('#' + campo).val();
        var tempElement = jQuery('<textarea>');
        tempElement.val(texto).appendTo('body').select();
        document.execCommand('copy');
        tempElement.remove();
    }

    limpiarPrompt() {
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
        jQuery('#' + tarea + '-marcas').val('');
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
        var marcas = '';
        var claves = '';
        var config = '';
        switch (tarea) {
            case "informe":
                if (this.informe[tipo]) {
                    intro = this.informe[tipo]['intro'];
                    peticion = this.informe[tipo]['peticion'];
                    texto = this.informe[tipo]['texto'];
                    marcas = this.informe[tipo]['marcas'];
                    claves = this.informe[tipo]['claves'];
                    config = this.informe[tipo]['config'];
                }
                break;
            case "articulo": 
                if (this.articulo[tipo]) {
                    intro = this.articulo[tipo]['intro'];
                    peticion = this.articulo[tipo]['peticion'];
                    texto = this.articulo[tipo]['texto'];
                    marcas = this.articulo[tipo]['marcas'];
                    claves = this.articulo[tipo]['claves'];
                    config = this.articulo[tipo]['config'];
                }
                break;
            case "noticia": 
                if (this.noticia[tipo]) {
                    intro = this.noticia[tipo]['intro'];
                    peticion = this.noticia[tipo]['peticion'];
                    texto = this.noticia[tipo]['texto'];
                    marcas = this.noticia[tipo]['marcas'];
                    claves = this.noticia[tipo]['claves'];
                    config = this.noticia[tipo]['config'];
                }
                break;
            case "presentacion": 
                if (this.presentacion[tipo]) {
                    intro = this.presentacion[tipo]['intro'];
                    peticion = this.presentacion[tipo]['peticion'];
                    texto = this.presentacion[tipo]['texto'];
                    marcas = this.presentacion[tipo]['marcas'];
                    claves = this.presentacion[tipo]['claves'];
                    config = this.presentacion[tipo]['config'];
                }
                break;
            case "guion": 
                if (this.guion[tipo]) {
                    intro = this.guion[tipo]['intro'];
                    peticion = this.guion[tipo]['peticion'];
                    texto = this.guion[tipo]['texto'];
                    marcas = this.guion[tipo]['marcas'];
                    claves = this.guion[tipo]['claves'];
                    config = this.guion[tipo]['config'];
                }
                break;
            case "aviso": 
                if (this.aviso[tipo]) {
                    intro = this.aviso[tipo]['intro'];
                    peticion = this.aviso[tipo]['peticion'];
                    texto = this.aviso[tipo]['texto'];
                    marcas = this.aviso[tipo]['marcas'];
                    claves = this.aviso[tipo]['claves'];
                    config = this.aviso[tipo]['config'];
                }
                break;
            case "correo": 
                if (this.correo[tipo]) {
                    intro = this.correo[tipo]['intro'];
                    peticion = this.correo[tipo]['peticion'];
                    texto = this.correo[tipo]['texto'];
                    marcas = this.correo[tipo]['marcas'];
                    claves = this.correo[tipo]['claves'];
                    config = this.correo[tipo]['config'];
                }
                break;
            case "preguntas": 
                if (this.preguntas[tipo]) {
                    intro = this.preguntas[tipo]['intro'];
                    peticion = this.preguntas[tipo]['peticion'];
                    texto = this.preguntas[tipo]['texto'];
                    marcas = this.preguntas[tipo]['marcas'];
                    claves = this.preguntas[tipo]['claves'];
                    config = this.preguntas[tipo]['config'];
                }
                break;
            case "texto": 
                if (this.texto[tipo]) {
                    intro = this.texto[tipo]['intro'];
                    peticion = this.texto[tipo]['peticion'];
                    texto = this.texto[tipo]['texto'];
                    marcas = this.texto[tipo]['marcas'];
                    claves = this.texto[tipo]['claves'];
                    config = this.texto[tipo]['config'];
                }
                break;
            case "instrucciones": 
                if (this.instrucciones[tipo]) {
                    intro = this.instrucciones[tipo]['intro'];
                    peticion = this.instrucciones[tipo]['peticion'];
                    texto = this.instrucciones[tipo]['texto'];
                    marcas = this.instrucciones[tipo]['marcas'];
                    claves = this.instrucciones[tipo]['claves'];
                    config = this.instrucciones[tipo]['config'];
                }
                break;
            case "ideas": 
                if (this.ideas[tipo]) {
                    intro = this.ideas[tipo]['intro'];
                    peticion = this.ideas[tipo]['peticion'];
                    texto = this.ideas[tipo]['texto'];
                    marcas = this.ideas[tipo]['marcas'];
                    claves = this.ideas[tipo]['claves'];
                    config = this.ideas[tipo]['config'];
                }
                break;
            case "propuesta": 
                if (this.propuesta[tipo]) {
                    intro = this.propuesta[tipo]['intro'];
                    peticion = this.propuesta[tipo]['peticion'];
                    texto = this.propuesta[tipo]['texto'];
                    marcas = this.propuesta[tipo]['marcas'];
                    claves = this.propuesta[tipo]['claves'];
                    config = this.propuesta[tipo]['config'];
                }
                break;
            default:
                control.verMensaje('No se encontró la plantilla: ' + tipo, 'error');
                break;
        }
        intro = intro.replace(/\|/g, "\n");
        peticion = peticion.replace(/\|/g, "\n");
        texto = texto.replace(/\|/g, "\n");
        jQuery('#' + tarea + '-intro').val(intro);
        jQuery('#' + tarea + '-peticion').val(peticion);
        jQuery('#' + tarea + '-texto').val(texto);
        jQuery('#' + tarea + '-marcas').val(marcas);
        jQuery('#' + tarea + '-claves').val(claves);
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
        var prompt = '';
        switch (tarea) {
            case "informe": prompt = this.informe['prompt']; break;
            case "articulo": prompt = this.articulo['prompt']; break;
            case "noticia": prompt = this.noticia['prompt']; break;
            case "presentacion": prompt = this.presentacion['prompt']; break;
            case "guion": prompt = this.guion['prompt']; break;
            case "aviso": prompt = this.aviso['prompt']; break;
            case "correo": prompt = this.correo['prompt']; break;
            case "preguntas": prompt = this.preguntas['prompt']; break;
            case "texto": prompt = this.texto['prompt']; break;
            case "instrucciones": prompt = this.instrucciones['prompt']; break;
            case "ideas": prompt = this.ideas['prompt']; break;
            case "propuesta": prompt = this.propuesta['prompt']; break;
        }
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
        jQuery('#input-mensaje-usuario').val(prompt);
        jQuery('#input-mensaje-usuario').trigger('input');
        jQuery(window).scrollTop( jQuery('div#pie-prompts' ).position().top);
    }

    iniciarTips() {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
          return new bootstrap.Tooltip(tooltipTriggerEl)
        });
    }

    formularioMarcas() {
        var tarea = jQuery('#tarea').val();
        var lista = jQuery('#' + tarea + '-marcas').val();
        var texto = jQuery('#' + tarea + '-texto').val();
        var plantilla = jQuery('#formulario_marcas');
        var formulario = jQuery('#form-marcas');
        var campos = lista.split('|');
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
        var lista = jQuery('#' + tarea + '-claves').val();
        var texto = jQuery('#' + tarea + '-peticion').val();
        var plantilla = jQuery('#formulario_claves');
        var formulario = jQuery('#form-claves');
        var campos = lista.split('|');
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

}

var prompts = new Prompts();
