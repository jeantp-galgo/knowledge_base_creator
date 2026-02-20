# Arquitectura de Skills: Por qué la inteligencia vive en el SKILL.md

## El principio central

Cada skill tiene dos partes con responsabilidades distintas:

- **SKILL.md**: contiene la inteligencia. Define qué buscar, cómo priorizarlo, qué schema retornar y qué restricciones aplicar.
- **Script Python**: es un ejecutor. Recibe instrucciones ya construidas, llama a la API externa y garantiza que el resultado sea válido.

Esta separación no es arbitraria. Tiene una razón práctica concreta.

---

## Por qué el prompt no vive en el script

Si el prompt está dentro del script, cada vez que quieras ajustar qué recolectar, cambiar una prioridad o modificar el schema, tienes que tocar código Python. Eso implica conocer el código, correr el riesgo de romper algo y hacer un cambio que debería ser editorial en un lugar técnico.

Si el prompt vive en el SKILL.md, cualquier ajuste es editar un archivo markdown. Sin código, sin riesgo de rotura, sin necesidad de entender el script.

El SKILL.md también es lo que Claude lee para saber qué hacer. Si la inteligencia estuviera en el script, Claude no tendría visibilidad de las reglas del negocio. Estaría ejecutando una caja negra.

---

## Cómo fluye la información

```
SKILL.md
  → Claude lo lee y entiende las reglas
  → Claude construye el prompt con los parámetros del Orchestrator
  → Claude pasa el prompt al script

scraper_fetch.py
  → Recibe el prompt ya construido
  → Llama a Gemini con google_search
  → Valida que el output sea JSON válido
  → Reintenta si el JSON es inválido
  → Retorna el JSON al skill

Claude (de vuelta en el skill)
  → Verifica que el JSON no esté vacío
  → Pasa el resultado al Orchestrator
```

Claude es el puente inteligente entre la definición (SKILL.md) y la ejecución (script).

---

## Por qué el Scraper tiene script y los demás no

El Scraper necesita acceso a internet para buscar experiencias reales de usuarios. Claude no tiene esa capacidad de forma nativa. Gemini con `google_search` es el puente a datos externos. Eso justifica el script.

El Validator, el Writer y el QA trabajan con datos que ya están en el contexto de la conversación. Son tareas de razonamiento, generación y evaluación. Claude hace estas tareas directamente, sin necesidad de llamar a una API externa.

| Skill | Script | Razón |
|-------|--------|-------|
| Scraper | Sí | Necesita web search (acceso externo) |
| Validator | No | Razonamiento con datos en contexto |
| Writer | No | Generación de texto en contexto |
| QA | No | Evaluación con datos en contexto |

Agregar scripts para Validator, Writer y QA no añadiría capacidad nueva. Solo añadiría complejidad, llamadas API innecesarias y menor calidad en las tareas de razonamiento.

---

## El contrato del script

Todo script de proveedor que se agregue al sistema debe cumplir el mismo contrato:

- **Entrada**: `prompt` (string, construido por Claude)
- **Salida**: `dict` con clave `"experiencias_usuarios"` (lista)
- **En fallo**: `{"experiencias_usuarios": [], "error": "descripción del error"}`

Esto permite intercambiar proveedores (Gemini, Tavily, Firecrawl) sin cambiar nada en el SKILL.md ni en el Orchestrator. Solo cambia el script que se llama.

---

## Qué pasa cuando el sistema escala

Este sistema está diseñado para correr con muchas motocicletas distintas. Con esa escala, la consistencia del output es crítica.

Si Claude tuviera que estructurar texto crudo en cada corrida (la alternativa descartada), el resultado dependería de cuánto contexto libre hay, del orden de las instrucciones y de variaciones naturales en la generación. Con el tiempo, la estructura del JSON podría variar sutilmente entre corridas.

Al delegar la estructuración a Gemini mediante un prompt con schema explícito, y al validar el JSON en el script antes de retornarlo, el output que llega al Validator siempre tiene la misma forma. El pipeline se vuelve predecible a escala.
