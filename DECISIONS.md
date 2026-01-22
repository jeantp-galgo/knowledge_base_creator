# Architecture Decision Records (ADR)

Registro de decisiones técnicas importantes del proyecto Deep Research Models.

---

## ADR-001: Usar Gemini en lugar de OpenAI

**Fecha:** 2026-01-15
**Estado:** ✅ Activo

### Contexto
Necesitamos un LLM con capacidades de "deep research" (búsqueda web + razonamiento) para generar bases de conocimiento de motos basadas en opiniones reales de usuarios.

### Decisión
Usar **Google Gemini** (API interactions) en lugar de OpenAI GPT-4 + browsing.

### Alternativas consideradas
1. **OpenAI GPT-4 con browsing:** Más conocido, pero más caro y con limitaciones en acceso a web
2. **Claude con MCP tools:** Excelente para razonamiento, pero sin búsqueda web nativa integrada
3. **Perplexity API:** Especializado en research, pero menos control sobre el formato de salida

### Consecuencias

#### ✅ Ventajas
- Gemini tiene deep research nativo (busca automáticamente en web)
- Maneja bien contextos largos (perfecto para procesar múltiples prompts)
- Respeta estructura de output (secciones `[VENTAJAS]`, `[PROBLEMAS]`, etc.)
---

## ADR-002: Usar datos del comparador de Galgo para identificar competidores

**Fecha:** 2026-01-18
**Estado:** Por implementar

### Contexto
Para generar comparaciones útiles, necesitamos saber qué modelos comparan realmente los usuarios entre sí.

### Decisión
Usar la **base de datos del comparador de Galgo** (URLs + views de Amplitude) en lugar de pedirle a la IA que "adivine" los competidores.

### Alternativas consideradas
1. **Preguntarle a Gemini:** "¿Cuáles son los competidores de la Hero Hunk 125 R?"
   - Problema: Puede inventar o basarse en info genérica no relevante para Colombia
2. **Usar segmento/cilindrada:** Filtrar motos del mismo tipo
   - Problema: No refleja comportamiento real de usuarios

### Consecuencias

#### ✅ Ventajas
- **Datos reales de comportamiento:** Los top 3 son los que los usuarios REALMENTE comparan
- Evita comparaciones irrelevantes o inventadas por la IA
- Aprovecha data propia de Galgo (ventaja competitiva)

#### ⚠️ Desventajas
- Dependencia de la base del comparador (debe actualizarse periódicamente)
- Si un modelo es muy nuevo, puede no tener suficientes comparaciones

---

## ADR-003: Output en archivos .md en lugar de otra extensión

**Fecha:** 2026-01-20
**Estado:** ✅ Activo

### Contexto
Las knowledge bases generadas necesitan ser almacenadas para consulta posterior (actualmente por el chatbot o sistema RAG).

### Decisión
Guardar cada knowledge base como **archivo Markdown** con naming `{fecha}-{code}-{pais}.md`.

### Alternativas consideradas
1. **PDF:** A simple vista es mas sencillo de leer para un humano
* Desventaja:
    * Más dificil de leer por LLM ya que tiene que parsear.
    * Las URLs se cortan si son largas.

### Consecuencias

#### ✅ Ventajas
- **Simplicidad:** No requiere infraestructura adicional
- **Versionable:** Fácil trackear cambios en Git
- **Human-readable:** Cualquiera puede abrir y revisar el output

---

## ADR-004: Descargar eventos raw de Amplitude en lugar de usar charts
### REVISAR
**Fecha:** 2026-01-22
**Estado:** ✅ No activo

### Contexto
Necesitamos todas las URLs del comparador, pero los charts de Amplitude tienen un límite de ~100 URLs por visualización.

### Decisión
Usar la API de **export raw events** (`/api/2/export`) descargando por semanas, en lugar de la API de charts (`/api/3/chart/{id}`).

### Alternativas consideradas
1. **Seguir usando charts con paginación:** Más simple, pero sigue limitado
2. **Crear múltiples charts filtrados:** Engorroso y manual

### Consecuencias

#### ✅ Ventajas
- **Sin límites:** Obtenemos TODAS las URLs, no solo las top 100
- Más control sobre el rango de fechas
- Datos más granulares (eventos individuales vs agregados)

#### ⚠️ Desventajas
- Mayor complejidad (manejo de gzip, iteración semanal)
- Más lento (descarga semana por semana)
- Mayor consumo de cuota de API

#### Implementación
- Método `start_session_weekly(weeks=4)`
- Descompresión gzip automática
- Fallback si los datos no vienen comprimidos

---

## ADR-005: Notebooks solo para orquestación, lógica en módulos

**Fecha:** 2026-01-20
**Estado:** ✅ Activo (en refactorización)

### Contexto
El notebook original (`trash/notebooks/app.ipynb`) tenía toda la lógica mezclada (extracción, procesamiento, prompts).

### Decisión
- **Notebooks:** Solo para ejecutar el pipeline y explorar resultados
- **Lógica de negocio:** En módulos bajo `src/`

### Consecuencias

#### ✅ Ventajas
- Código reutilizable (puedes crear un `main.py` después)
- Testeable (puedes hacer unit tests de las funciones)
- Más limpio y mantenible

#### ⚠️ Desventajas
- Más archivos (pero mejor organizado)

---

## ADR-006: Usar prompts en archivos .md externos

**Fecha:** 2026-01-18
**Estado:** ✅ Activo

### Contexto
Los prompts para Gemini son largos (200+ líneas) y cambian frecuentemente durante pruebas.

### Decisión
Guardar prompts como templates en `src/data/prompts/*.md` con variables tipo `{marca}`, `{modelo}`.

### Alternativas consideradas
1. **Prompts hardcodeados en código Python:** Difícil de editar
2. **Prompts en base de datos:** Overkill para este caso

### Consecuencias

#### ✅ Ventajas
- Fácil de editar sin tocar código
- Versionable en Git (puedes ver historial de cambios en prompts)
- Reutilizable para diferentes research types

#### ⚠️ Desventajas
- Un archivo más que mantener sincronizado

---

## Template para nuevas decisiones

## ADR-XXX: [Título de la decisión]

**Fecha:** YYYY-MM-DD
**Estado:** ✅ Activo / ⚠️ Superseded / ❌ Rechazado

### Contexto
[Describe el problema que necesitas resolver]

### Decisión
[Qué decidiste hacer]

### Alternativas consideradas
1. Opción A: [pros/cons]
2. Opción B: [pros/cons]

### Consecuencias
#### ✅ Ventajas
- ...

#### ⚠️ Desventajas
- ...
