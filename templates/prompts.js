var misprompts = [];
//{% for prompt in datos.prompts %}
misprompts['{{prompt.id}}'] = {"nombre": "{{prompt.etiqueta}}", "intro": "{{prompt.intro}}", "peticion": "{{prompt.peticion}}", "texto": "{{prompt.texto}}", "config": "{{prompt.config}}"};
//{% endfor %}
