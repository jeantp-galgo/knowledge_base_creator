## Contexto del Proyecto
### Qué se quiere hacer
Automatizar la generación de bases de conocimiento sobre motocicletas usando IA. Estas bases de conocimiento se utilizarán para alimentar un chatbot en un marketplace de motos.

### Objetivo principal

El objetivo de la base de conocimiento es capturar la experiencia real y emocional de poseer y usar la moto, no las especificaciones que ya están en manuales.
Es responder preguntas como:

"¿Realmente vale la pena?"
"¿Qué me va a molestar después de 6 meses de uso?"
"¿Me va a dejar tirado?"
"¿Es mejor que la competencia en la práctica diaria?"

Es el tipo de información que un amigo que YA tiene la moto te contaría tomando cerveza, no lo que dice el vendedor o el folleto.

### Funcionamiento general
Se toman datos de una moto desde un archivo CSV que contiene los datos (marca, modelo, año, país, tipo de moto)
Se genera un prompt personalizado con esos datos
Se envía el prompt a Replicate API para ejecutar (modelo por definir)
Se recibe un informe detallado con experiencias reales de usuarios
Se guarda el informe como base de conocimiento
El chatbot del marketplace consulta estos informes para responder preguntas de usuarios

### Qué tipo de información genera
Los informes se enfocan en experiencias reales de usuarios, NO en especificaciones técnicas:

Problemas comunes que reportan los dueños
Sensaciones de manejo
Comparaciones con otras motos
Consumo real de combustible
Valor de reventa
Modificaciones populares

### Consideraciones importantes

Se genera un informe por cada moto POR PAÍS (la misma moto en Colombia puede tener experiencias diferentes que en México)
Los informes complementan la información técnica de la base de datos, no la reemplazan
El sistema usa el tipo de moto (urbana, deportiva, adventure, etc.) para adaptar qué información buscar