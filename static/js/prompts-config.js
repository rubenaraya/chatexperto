prompts.informe['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono)).|Usa como base el siguiente texto:|"""|((texto))|"""';
prompts.articulo['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono)).|Usa como base el siguiente texto:|"""|((texto))|"""';
prompts.noticia['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono)).|Usa como base el siguiente texto:|"""|((texto))|"""';
prompts.presentacion['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono)).|Usa como base el siguiente texto:|"""|((texto))|"""';
prompts.guion['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono)).|Usa como base el siguiente texto:|"""|((texto))|"""';
prompts.aviso['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono)).|Usa como base el siguiente texto:|"""|((texto))|"""';
prompts.correo['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono)).|Usa como base el siguiente texto:|"""|((texto))|"""';
prompts.preguntas['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono)).|Usa como base el siguiente texto:|"""|((texto))|"""';
prompts.texto['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono)).|Usa como base el siguiente texto:|"""|((texto))|"""';
prompts.instrucciones['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono)).|Usa como base el siguiente texto:|"""|((texto))|"""';
prompts.ideas['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono)).|Usa como base el siguiente texto:|"""|((texto))|"""';
prompts.propuesta['prompt'] = '((intro))|((peticion))|Responde en ((idioma)) usando un LENGUAJE ((lenguaje)), con un ESTILO ((estilo)) y en un TONO ((tono)).|Usa como base el siguiente texto:|"""|((texto))|"""';

prompts.informe['psico-colegios'] = {
    "intro": "Eres Psicóloga. Tienes habilidad para redactar informes de casos, tus respuestas deben ser completas y bien desarrolladas.",
    "peticion": "Redacta un Informe psicológico|acerca de: la situación del paciente [paciente],|que se usará para: informar del diagnóstico al establecimiento educacional donde estudia,|con el propósito de: entregar orientaciones para abordar la situación que está viviendo el niño/a,|dirigido a: ((dirigido-a)).",
    "texto": "Quien suscribe, certifica que con fecha ((fecha-inicio)), inicia proceso de evaluación psicoterapéutica al paciente [paciente] de ((edad-paciente)) años de edad, que cursa ((curso-actual)) en [establecimiento], solicitada por sus padres [madre] y [padre].|El motivo de consulta, según relato de los padres y la entrevista con [paciente], hace referencia a ((motivo-de-consulta)).|Se aplicaron algunos instrumentos, cuyos resultados indican que el paciente presenta ((diagnostico-clinico)).|Se ha identificado que [paciente] se encuentra ((otras-observaciones)).|Lo anterior está generando consecuencias emocionales y conductuales negativas, como ((consecuencias-negativas)).|Para atender adecuadamente la situación de [paciente], es importante trabajar de manera conjunta y coordinada con el establecimiento educacional para ((objetivo-de-colaboracion)).|Agradeciendo de antemano su atención a esta información, quedo a su disposición para cualquier consulta o inquietud.",
    "marcas": "fecha-inicio|edad-paciente|curso-actual|motivo-de-consulta|diagnostico-clinico|otras-observaciones|consecuencias-negativas|objetivo-de-colaboracion",
    "claves": "dirigido-a",
    "config": "Profesional|Asertivo|Educativo"
};
prompts.informe['psico-laboral'] = {
    "intro": "",
    "peticion": "",
    "texto": "",
    "marcas": "",
    "claves": "",
    "config": ""
};
