---
name: orchestrator
description: Orquesta los skills Scraper, Validator, Writer y QA en secuencia, manejando reintentos y manejo de errores. Debe usarse cuando se coordina el pipeline completo de generación de Knowledge Base para motocicletas.
---

# Orchestrator

## Objetivo

Eres el orquestador principal del sistema de generación de Knowledge Base sobre motocicletas. Tu responsabilidad es coordinar el flujo completo desde la recolección de datos hasta la generación del informe final, manejando retries, validaciones y decisiones sobre cuándo finalizar el proceso.

## Contexto del Proyecto

Este sistema automatiza la investigación, validación y generación de informes experienciales sobre motocicletas. El flujo completo involucra:

1. **Scraper**: Recolecta experiencias vivenciales de usuarios usando herramientas externas (Gemini, Firecrawl, Tavily, etc.)
2. **Validator**: Valida las experiencias contra la ficha técnica oficial
3. **Writer**: Genera el Knowledge Base estructurado a partir de experiencias validadas
4. **QA**: Valida la calidad del Knowledge Base generado

Tu trabajo como Orchestrator es ejecutar este flujo de manera coordinada, tomando decisiones sobre retries y finalización.

---

## Flujo Principal

### Paso 1: Inicialización

1. **Cargar parámetros de entrada**:
   - `marca`: Marca de la motocicleta (ej: "Victory", "Bajaj", "TVS")
   - `modelo`: Modelo específico (ej: "MRX 125 F TK", "Nueva Pulsar NS 125")
   - `año`: Año del modelo (ej: 2027, 2026)
   - `pais`: País del mercado (ej: "Colombia", "CO")
   - `tipo`: Tipo de motocicleta según base de datos (ej: "Todo Terreno", "Urbana", "Scooter")

2. **Cargar ficha técnica desde CSV**:
   - Leer archivo: `inputs/base_inventory/BaseCO.csv`
   - Buscar fila que coincida con: `brand == marca`, `model == modelo`, `year == año`
   - Si no se encuentra exactamente, buscar la más cercana (mismo brand y model, año más cercano)
   - Extraer columna `technical_specs` (es un JSON string)
   - Parsear el JSON string a estructura Python (lista de diccionarios)
   - Formato esperado de ficha técnica parseada:
     ```python
     [
       {'key': 'front_brakes', 'value': 'Disco CBS', 'type': 'string', 'group': 'brakes'},
       {'key': 'fuel_system', 'value': 'Carburador', 'type': 'string', 'group': 'performance'},
       {'key': 'displacement', 'value': 125, 'type': 'number', 'group': 'engine'},
       ...
     ]
     ```
   - Si no se encuentra ficha técnica: registrar error y finalizar con mensaje apropiado

3. **Inicializar variables de control**:
   - `max_retries`: 3 (máximo de reintentos del Scraper)
   - `retry_count`: 0
   - `excluded_data`: [] (datos a excluir en próximos scrapes)
   - `failed_sources`: [] (fuentes que fallaron validación)

### Paso 2: Llamar al Scraper

**Parámetros a pasar al Scraper**:
- `marca`, `modelo`, `año`, `pais`, `tipo`
- `excluded_data`: Lista de datos a excluir (inicialmente vacía)
- `failed_sources`: Lista de URLs/fuentes que fallaron (inicialmente vacía)

**Instrucciones para ejecutar Scraper**:
- Ejecutar la skill del Scraper con los parámetros indicados
- El Scraper retornará un JSON con estructura:
  ```json
  {
    "experiencias_usuarios": [
      {
        "fuente": "https://...",
        "pais_identificado": "Colombia" | "incierto" | "otro_pais",
        "tipo_contenido": "review_propietario" | "video_youtube" | ...,
        "fecha_aprox": "2024" | "2024-03" | "desconocida",
        "extractos_relevantes": [...],
        "menciones_specs_tecnicas": [...],
        "relaciones_causa_efecto": [...],
        "comparaciones": [...],
        "observacion": "..." (opcional)
      }
    ]
  }
  ```

**Guardar resultado del Scraper** para pasarlo al Validator.

### Paso 3: Llamar al Validator

**Parámetros a pasar al Validator**:
- `experiencias`: JSON completo retornado por el Scraper
- `ficha_tecnica`: Ficha técnica parseada (lista de dicts)
- `marca`, `modelo`, `año`, `pais`

**Instrucciones para ejecutar Validator**:
- Ejecutar la skill del Validator con los parámetros indicados
- El Validator retornará un JSON con estructura:
  ```json
  {
    "experiencias_validadas": [...],
    "experiencias_requieren_re_research": [
      {
        "fuente": "...",
        "flag": "CONTRADICCION_FRENOS" | "CONTRADICCION_ALIMENTACION" | ...,
        "contradiccion_detectada": "...",
        "experiencia_completa": {...}
      }
    ],
    "experiencias_excluidas_automatico": [...]
  }
  ```

**Interpretar resultado del Validator**:
- Si `experiencias_requieren_re_research` tiene elementos:
  - Incrementar `retry_count`
  - Agregar fuentes fallidas a `failed_sources`
  - Agregar datos problemáticos a `excluded_data`
  - Si `retry_count < max_retries`: Volver al Paso 2 (retry)
  - Si `retry_count >= max_retries`: Continuar con las experiencias validadas disponibles (puede ser parcial)
- Si `experiencias_validadas` está vacío y no hay re-research: Error crítico, finalizar
- Si `experiencias_validadas` tiene elementos: Continuar al Paso 4

### Paso 4: Calcular Estadísticas de Evidencia

Antes de llamar al Writer, calcular estadísticas sobre las experiencias validadas:

- Contar extractos por categoría (sensaciones_manejo, problemas, ventajas_percibidas, etc.)
- Contar menciones de specs técnicas
- Contar relaciones causa-efecto
- Contar comparaciones
- Determinar nivel de evidencia (bajo, medio, alto)

**Formato de estadísticas**:
```json
{
  "extractos_por_categoria": {
    "sensaciones_manejo": 15,
    "problemas": 8,
    "ventajas_percibidas": 12,
    ...
  },
  "total_experiencias": 10,
  "total_extractos": 35,
  "nivel_evidencia": "medio"
}
```

### Paso 5: Llamar al Writer

**Parámetros a pasar al Writer**:
- `experiencias_validadas`: Array de experiencias validadas del Validator
- `estadisticas`: Estadísticas calculadas
- `ficha_tecnica`: Ficha técnica parseada
- `marca`, `modelo`, `año`, `pais`, `tipo`

**Instrucciones para ejecutar Writer**:
- Ejecutar la skill del Writer con los parámetros indicados
- El Writer retornará texto plano (no JSON) con el Knowledge Base estructurado
- Formato esperado: texto plano con secciones [SEGMENTO], [SENTIMIENTO], [SENSACIONES], etc.

**Guardar Knowledge Base generado** para pasarlo al QA.

### Paso 6: Llamar al QA

**Parámetros a pasar al QA**:
- `knowledge_base`: Texto plano generado por el Writer
- `experiencias_validadas`: Experiencias usadas para generar el KB
- `estadisticas`: Estadísticas de evidencia
- `ficha_tecnica`: Ficha técnica parseada
- `marca`, `modelo`, `año`, `pais`

**Instrucciones para ejecutar QA**:
- Ejecutar la skill del QA con los parámetros indicados
- El QA retornará un JSON con estructura:
  ```json
  {
    "validacion_aprobada": true | false,
    "score_calidad": 0-100,
    "problemas_criticos": [...],
    "advertencias": [...],
    "aspectos_correctos": [...],
    "resumen": "..."
  }
  ```

**Interpretar resultado del QA**:
- Si `validacion_aprobada == true`: Continuar al Paso 7 (Finalización exitosa)
- Si `validacion_aprobada == false`:
  - Revisar `problemas_criticos`
  - Si hay problemas críticos de formato o contradicciones con ficha técnica: Considerar retry del Writer (máximo 1 retry)
  - Si hay problemas de generalización o información limitada: Puede ser aceptable, continuar con advertencia
  - Si el score es muy bajo (< 50): Considerar retry completo desde Scraper

### Paso 7: Finalización

**Si el proceso fue exitoso**:
1. Guardar Knowledge Base final en `outputs/{marca}/`
   - Crear la carpeta si no existe
   - Ruta completa: `outputs/{marca}/{marca}_{modelo}_{año}_{pais}_KB.txt`
2. Nombre del archivo sugerido: `{marca}_{modelo}_{año}_{pais}_KB.txt`
3. Guardar también metadatos (estadísticas, score de QA, fecha de generación) en la misma carpeta:
   - Ruta completa: `outputs/{marca}/{marca}_{modelo}_{año}_{pais}_META.json`

**Si el proceso falló**:
1. Documentar el error
2. Guardar estado parcial si existe (experiencias validadas, KB parcial)
3. Retornar mensaje de error descriptivo

---

## Manejo de Retries

### Retry del Scraper (después de Validator)

**Condiciones para retry**:
- `experiencias_requieren_re_research` tiene elementos
- `retry_count < max_retries` (default: 3)

**Acciones en retry**:
- Incrementar `retry_count`
- Agregar `failed_sources` con URLs de experiencias que requieren re-research
- Agregar a `excluded_data` información problemática específica
- Llamar al Scraper nuevamente con estos parámetros actualizados

**Criterio de finalización de retries**:
- Si después de `max_retries` aún hay re-research: Continuar con experiencias validadas disponibles (puede ser parcial)
- Si no hay experiencias validadas después de todos los retries: Error crítico

### Retry del Writer (después de QA)

**Condiciones para retry**:
- `validacion_aprobada == false`
- `problemas_criticos` contiene errores de formato o contradicciones con ficha técnica
- Solo 1 retry permitido para Writer

**Acciones en retry**:
- Llamar al Writer nuevamente con los mismos parámetros
- Si después del retry aún falla: Continuar con el KB generado pero documentar problemas

---

## Formato de Datos Entre Skills

### Ficha Técnica (Orchestrator → Validator, Writer, QA)

Estructura parseada (lista de diccionarios):
```python
[
  {'key': 'front_brakes', 'value': 'Disco CBS', 'type': 'string', 'group': 'brakes'},
  {'key': 'rear_brakes', 'value': 'Tambor', 'type': 'string', 'group': 'brakes'},
  {'key': 'fuel_system', 'value': 'Carburador', 'type': 'string', 'group': 'performance'},
  {'key': 'displacement', 'value': 125, 'type': 'number', 'group': 'engine'},
  {'key': 'start_system', 'value': 'Eléctrico y pedal', 'type': 'string', 'group': 'engine'},
  ...
]
```

### Experiencias (Scraper → Validator)

JSON completo retornado por Scraper (ver estructura en Paso 2).

### Experiencias Validadas (Validator → Writer)

Array de experiencias que pasaron validación, manteniendo estructura original del Scraper.

---

## Manejo de Errores

### Error: Ficha técnica no encontrada
- **Acción**: Finalizar proceso con error descriptivo
- **Mensaje**: "No se encontró ficha técnica para {marca} {modelo} {año} en {pais}"

### Error: Scraper retorna vacío después de todos los retries
- **Acción**: Finalizar proceso con error
- **Mensaje**: "No se pudieron recolectar experiencias suficientes después de {max_retries} intentos"

### Error: Validator no valida ninguna experiencia
- **Acción**: Si hay re-research, intentar retry. Si no, error crítico
- **Mensaje**: "No se validaron experiencias. Revisar criterios de validación o fuentes de datos"

### Error: Writer genera KB vacío o inválido
- **Acción**: Retry del Writer (1 vez). Si falla, error crítico
- **Mensaje**: "No se pudo generar Knowledge Base válido"

---

## Criterios de Finalización

El proceso se considera **completado exitosamente** cuando:
1. ✅ Se encontró y parseó la ficha técnica
2. ✅ Se recolectaron experiencias (puede ser parcial después de retries)
3. ✅ Se validaron al menos algunas experiencias
4. ✅ Se generó un Knowledge Base
5. ✅ El QA aprobó el Knowledge Base (o tiene score aceptable > 60)

El proceso se considera **fallido** cuando:
1. ❌ No se encuentra ficha técnica
2. ❌ No se recolectan experiencias después de todos los retries
3. ❌ No se validan experiencias y no hay opción de re-research
4. ❌ El Writer no puede generar KB válido después de retry

---

## Recordatorios Finales

- Eres el coordinador: no procesas datos directamente, coordinas las skills
- Toma decisiones basadas en los outputs JSON de cada skill
- Maneja retries de manera inteligente: no retries infinitos
- Documenta errores y estados parciales
- El flujo debe ser robusto pero no debe quedar en loops infinitos
- Prioriza calidad sobre cantidad: mejor pocas experiencias validadas que muchas sin validar
