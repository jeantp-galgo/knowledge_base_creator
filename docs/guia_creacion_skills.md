# Guía para Crear Nuevas Skills

## Antes de escribir cualquier cosa, responde estas preguntas

1. ¿Esta skill necesita datos externos (internet, APIs, archivos)?
   - Sí → necesita script
   - No → Claude la ejecuta directamente en la conversación

2. ¿Qué hace Claude y qué hace el script?
   - Escríbelo explícitamente antes de tocar código

3. ¿Dónde vive la inteligencia (reglas, prioridades, schema)?
   - Siempre en el SKILL.md, nunca en el script

Si no puedes responder estas tres preguntas con claridad, no empieces a escribir todavía.

---

## La lección aprendida (caso real)

Durante la primera ejecución del Orchestrator para generar el Knowledge Base de la Hero Hunk 125R, ocurrió este error:

**Qué pasó:** Se crearon scripts Python en `outputs/` para el Validator, Writer y QA, y se usó Gemini para ejecutar tareas que debía hacer Claude directamente.

**Por qué ocurrió:** El Scraper necesitaba un script para llamar a Gemini. Una vez que se entró en "modo script", esa lógica se extendió automáticamente a los pasos siguientes sin detenerse a preguntar si era necesario.

```
Scraper necesita Gemini  →  script (correcto)
        ↓
Ya estoy en modo script
        ↓
Validator  →  script con Gemini  (error)
Writer     →  script con Gemini  (error)
QA         →  script con Gemini  (error)
```

**Por qué fue un error:** Validator, Writer y QA trabajan con datos que ya están en el contexto de la conversación. No necesitan acceso externo. Claude hace esas tareas mejor que Gemini y sin costo adicional.

**Qué lo hubiera prevenido:** Tener respondida la pregunta 1 antes de empezar. Si la respuesta es "no necesita datos externos", no hay script. Sin excepción.

---

## Cómo definir el SKILL.md correctamente

### Lo que debe decir siempre

- **Qué hace Claude** en esta skill (construir prompt, razonar, generar, evaluar)
- **Qué hace el script** si existe (ejecutar, validar output, reintentar)
- **Dónde termina el script** y dónde retoma Claude
- **El schema exacto** del output si aplica

### Lo que no debe pasar

- Que el prompt de búsqueda viva dentro del script → si cambia el prompt, no debería requerir tocar código
- Que el script tome decisiones de negocio → eso es rol de Claude
- Que quede ambiguo hasta dónde procesa Claude y hasta dónde el script

### Señal de alerta

Si al leer el SKILL.md no queda claro dónde termina el script y empieza Claude, el documento está incompleto. Esa ambigüedad es exactamente lo que causó el error del caso anterior.

---

## Estructura recomendada para un SKILL.md con script

```
## Objetivo
(qué hace la skill en una línea)

## Contexto de Uso
(parámetros que recibe del Orchestrator)

## Proceso
  Paso 1: Claude hace X
  Paso 2: Claude construye Y y lo pasa al script
  Paso 3: Script ejecuta, retorna Z
  Paso 4: Claude recibe Z, verifica, pasa al siguiente skill

## Qué incluir / Qué priorizar
(las reglas de negocio que Claude usa para construir el prompt)

## Formato de Salida
(schema exacto, incluirlo en el prompt que se le pasa al script)

## Restricciones
(reglas que van al prompt)
```

## Estructura recomendada para un SKILL.md sin script

```
## Objetivo
## Contexto de Uso
## Proceso
  (pasos de razonamiento que Claude ejecuta directamente)
## Criterios / Reglas
## Formato de Salida
```

---

## Checklist antes de considerar una skill lista

- [ ] Está respondida la pregunta "¿necesita datos externos?"
- [ ] Si tiene script: el SKILL.md dice exactamente qué hace el script y qué hace Claude
- [ ] El prompt no está hardcodeado en el script
- [ ] El schema del output está definido en el SKILL.md
- [ ] Si no tiene script: el SKILL.md describe el razonamiento que Claude debe hacer
- [ ] Está claro qué parámetros recibe del Orchestrator y qué retorna
