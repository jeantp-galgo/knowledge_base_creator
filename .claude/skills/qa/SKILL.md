---
name: qa
description: Valida la calidad de Knowledge Base generado sobre motocicletas. Verifica consistencia con fichas técnicas oficiales, generalizaciones apropiadas según nivel de evidencia, formato correcto de secciones, ausencia de información inventada y coherencia interna. Retorna JSON estructurado con puntaje de calidad (0-100), problemas críticos, advertencias y recomendaciones. Relevante para asegurar calidad y precisión de informes experienciales antes de finalización.
---

# Skill: QA - Validación de Knowledge Base

## Objetivo

Validar la calidad del Knowledge Base generado para la motocicleta especificada. Verificar consistencia, generalizaciones apropiadas, formato y que no haya información inventada. Tu validación determina si el Knowledge Base es aprobado o requiere correcciones.

---

## Contexto de Uso

Eres llamado por el Orchestrator con los siguientes parámetros:

- `knowledge_base`: Texto plano generado por el Writer (Knowledge Base completo)
- `experiencias_validadas`: Array de experiencias validadas usadas para generar el KB
- `estadisticas`: Objeto con estadísticas de evidencia:
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
    "nivel_evidencia": "bajo" | "medio" | "alto"
  }
  ```
- `ficha_tecnica`: Ficha técnica parseada (lista de diccionarios) - ancla de verdad para validación
- `marca`: Marca de la motocicleta
- `modelo`: Modelo específico
- `año`: Año del modelo
- `pais`: País del mercado

---

## Formato de Ficha Técnica

La ficha técnica que recibes es una lista de diccionarios con formato:
```python
[
  {'key': 'front_brakes', 'value': 'Disco CBS', 'type': 'string', 'group': 'brakes'},
  {'key': 'fuel_system', 'value': 'Carburador', 'type': 'string', 'group': 'performance'},
  {'key': 'displacement', 'value': 125, 'type': 'number', 'group': 'engine'},
  ...
]
```

**Cómo acceder a valores de la ficha**:
- Buscar en la lista el diccionario con `key` igual al campo que necesitas
- Extraer el `value` de ese diccionario
- Si el campo no existe o `value` es None: considerar como "NO DISPONIBLE"

**Campos críticos para validación**:
- `front_brakes` / `rear_brakes` → Sistema de frenos
- `fuel_system` → Sistema de alimentación
- `displacement` → Cilindraje
- `start_system` → Sistema de arranque

---

## Aspectos a Validar

### 1. Consistencia con Ficha Técnica

Verifica que el KB NO contradiga la ficha técnica en specs críticos:

- **Sistema de frenos**: Si ficha dice "CBS", el KB NO debe decir "ABS"
- **Sistema de alimentación**: Si ficha dice "Carburada", el KB NO debe decir "Inyección"
- **Cilindraje**: Si ficha dice "124.7 cc", el KB NO debe decir "150cc"
- **Sistema de arranque**: Debe coincidir con la ficha

**PERMITIDO**:
- Mencionar percepciones que contrastan: "La ficha dice 125cc pero se siente como 150cc"
- Comparaciones: "Comparado con motos con ABS, el CBS requiere..."
- Opiniones: "Usuarios esperaban ABS pero tiene CBS"

**PROHIBIDO**:
- Escribir que tiene ABS cuando la ficha dice CBS
- Escribir que tiene inyección cuando la ficha dice carburador
- Contradecir cualquier spec técnico de la ficha

**Tipo de problema**: `CONTRADICCION_FICHA`
**Severidad**: `alta` (crítico)

### 2. Generalizaciones Apropiadas

Verifica que el lenguaje sea apropiado según la cantidad de evidencia (usa las estadísticas proporcionadas):

**Modificaciones**:
- 1 ejemplo → Debe decir "Un usuario ha modificado..." o "Se ha documentado un caso de..."
- 2 ejemplos → Debe decir "Algunos usuarios han modificado..."
- 3+ ejemplos → Puede decir "Algunos usuarios modifican..." o listar las modificaciones

**Otros aspectos**:
- 1 ejemplo → "Un usuario reporta..." o "Se ha documentado..."
- 2-3 ejemplos → "Algunos usuarios reportan..." o "Hay reportes de..."
- 4+ ejemplos → "Los usuarios reportan..." o "Es común que..."

**PROHIBIDO**:
- Generalizar con "Los usuarios modifican..." cuando hay 1-2 ejemplos
- Usar "Es común..." cuando hay muy pocos datos
- Afirmar algo como general cuando es un caso aislado

**Tipo de problema**: `GENERALIZACION_INAPROPIADA`
**Severidad**: `media` o `alta` (dependiendo de la gravedad)

### 3. Formato Correcto

Verifica que el KB tenga:
- Todas las secciones requeridas: [SEGMENTO], [SENTIMIENTO], [SENSACIONES], [VENTAJAS], [PROBLEMAS], [CAUSA_EFECTO], [RENDIMIENTO], [CONFIABILIDAD], [REVENTA], [MODIFICACIONES], [PERFIL_USUARIO], [OPINIONES_DIVIDIDAS], [LIMITACIONES], [COMPARACIONES], [SINTESIS]
- Formato de texto plano (sin markdown, sin negritas, sin cursivas)
- Encabezados con formato [SECCION] seguidos de línea en blanco
- Estructura de [PROBLEMAS] correcta (Nombre, Frecuencia, Descripción, Contexto, Solución comunitaria)

**Tipo de problema**: `FORMATO_INCORRECTO`
**Severidad**: `media` o `alta` (dependiendo de qué falte)

### 4. Contradicciones Internas

Verifica que el KB no se contradiga a sí mismo:
- Si dice "muy potente" en una sección, no debe decir "poca potencia" en otra sin explicar el contexto
- Si menciona un problema, debe ser consistente en toda la descripción
- Las comparaciones deben ser coherentes

**Tipo de problema**: `CONTRADICCION_INTERNA`
**Severidad**: `media` o `alta`

### 5. Información Respalda por Experiencias

Verifica que la información del KB esté respaldada por las experiencias validadas:
- NO debe inventar problemas que no están en las experiencias
- NO debe agregar ventajas que no se mencionan en las experiencias
- NO debe completar información que no tiene evidencia
- Si no hay información suficiente, debe declararlo explícitamente

**Tipo de problema**: `INFORMACION_INVENTADA`
**Severidad**: `alta` (crítico)

### 6. Uso Correcto de Ficha Técnica

Verifica que:
- La ficha técnica se use como ancla, NO como contenido del KB
- NO repita información técnica de la ficha como si fuera experiencia de usuario
- Use la ficha para contrastar, no para describir

**Tipo de problema**: `USO_INCORRECTO_FICHA`
**Severidad**: `media`

---

## Cálculo de Score de Calidad

El `score_calidad` debe ser un número entre 0 y 100, calculado así:

- **Base**: 100 puntos
- **Problemas críticos (severidad alta)**: -20 puntos cada uno
- **Problemas medios (severidad media)**: -10 puntos cada uno
- **Problemas bajos (severidad baja)**: -5 puntos cada uno
- **Advertencias**: -2 puntos cada una (máximo -10 puntos por advertencias)

**Score mínimo para aprobación**: 60 puntos (configurable, pero recomendado)

---

## Criterios de Aprobación

`validacion_aprobada: true` SOLO cuando se cumplen TODAS las condiciones simultáneamente:
- ✅ NO hay contradicciones con la ficha técnica (tipo `CONTRADICCION_FICHA`)
- ✅ NO hay información inventada (tipo `INFORMACION_INVENTADA`)
- ✅ Las generalizaciones son apropiadas según la evidencia (o solo advertencias menores)
- ✅ El formato es correcto (todas las secciones presentes)
- ✅ Score de calidad >= 60

`validacion_aprobada: false` si se cumple CUALQUIERA de estas condiciones:
- ❌ Hay contradicciones críticas con la ficha técnica
- ❌ Hay información claramente inventada
- ❌ Generaliza inapropiadamente de manera grave (ej: "Los usuarios modifican..." con 1 ejemplo)
- ❌ Faltan secciones críticas
- ❌ Score de calidad < 60

**Nota**: Un KB puede tener `validacion_aprobada: false` y aun así no tener `CONTRADICCION_FICHA` ni `INFORMACION_INVENTADA` — por ejemplo, si acumula varios problemas de severidad media que bajan el score por debajo de 60. En ese caso, el rechazo se basa en el score, no en los tipos críticos.

---

## Formato de Salida

Retorna ÚNICAMENTE un JSON válido con esta estructura:

```json
{
  "validacion_aprobada": true | false,
  "score_calidad": 0-100,
  "problemas_criticos": [
    {
      "tipo": "CONTRADICCION_FICHA" | "GENERALIZACION_INAPROPIADA" | "FORMATO_INCORRECTO" | "CONTRADICCION_INTERNA" | "INFORMACION_INVENTADA" | "USO_INCORRECTO_FICHA",
      "seccion": "[SECCION] donde está el problema",
      "descripcion": "Descripción detallada del problema. Ejemplo: En [SENSACIONES] se menciona que la moto tiene ABS, pero la ficha técnica indica 'Disco CBS' para frenos delanteros.",
      "severidad": "alta" | "media" | "baja",
      "sugerencia_correccion": "Cómo corregirlo. Ejemplo: Cambiar 'ABS' por 'CBS' o mencionar que usuarios esperaban ABS pero tiene CBS."
    }
  ],
  "advertencias": [
    {
      "tipo": "GENERALIZACION_LIMITE" | "INFORMACION_LIMITADA" | "OTRO",
      // GENERALIZACION_LIMITE: lenguaje casi correcto pero en el límite (ej: 3 ejemplos y usa "Es común")
      // INFORMACION_LIMITADA: sección con muy pocos datos, podría haberse expandido más
      // OTRO: cualquier observación que no encaje en los tipos anteriores (ej: tono inapropiado, redacción confusa)
      "seccion": "[SECCION]",
      "descripcion": "Advertencia sobre algo que podría mejorarse. Ejemplo: En [MODIFICACIONES] se usa 'Algunos usuarios modifican...' pero solo hay 2 ejemplos. Considerar usar 'Algunos usuarios han modificado...'",
      "sugerencia": "Sugerencia de mejora"
    }
  ],
  "aspectos_correctos": [
    "Lista de aspectos que están bien implementados. Ejemplo: 'Formato de texto plano correcto', 'Todas las secciones presentes', 'Generalizaciones apropiadas en [VENTAJAS]'"
  ],
  "resumen": "Resumen general de la validación. Incluir score, principales problemas encontrados (si hay), y recomendación final."
}
```

---

## Ejemplos de Validación

### Ejemplo 1: Contradicción con Ficha Técnica

**Problema detectado**: KB dice "La moto cuenta con sistema de frenos ABS" pero ficha técnica dice `front_brakes: 'Disco CBS'`

**Output**:
```json
{
  "tipo": "CONTRADICCION_FICHA",
  "seccion": "[SENSACIONES]",
  "descripcion": "Se menciona que la moto tiene ABS, pero la ficha técnica indica 'Disco CBS' para frenos delanteros.",
  "severidad": "alta",
  "sugerencia_correccion": "Cambiar 'ABS' por 'CBS' o reformular como 'Usuarios esperaban ABS pero la versión en Colombia tiene CBS'"
}
```

### Ejemplo 2: Generalización Inapropiada

**Problema detectado**: En [MODIFICACIONES] dice "Los usuarios modifican..." pero estadísticas muestran solo 1 ejemplo

**Output**:
```json
{
  "tipo": "GENERALIZACION_INAPROPIADA",
  "seccion": "[MODIFICACIONES]",
  "descripcion": "Se generaliza con 'Los usuarios modifican...' pero solo hay 1 ejemplo documentado en las experiencias.",
  "severidad": "media",
  "sugerencia_correccion": "Cambiar a 'Un usuario ha modificado...' o 'Se ha documentado un caso de modificación...'"
}
```

### Ejemplo 3: Formato Incorrecto

**Problema detectado**: Falta la sección [COMPARACIONES]

**Output**:
```json
{
  "tipo": "FORMATO_INCORRECTO",
  "seccion": "Falta sección",
  "descripcion": "Falta la sección [COMPARACIONES] que es requerida según el formato.",
  "severidad": "alta",
  "sugerencia_correccion": "Agregar sección [COMPARACIONES] con el formato especificado, o declarar 'No se identificaron comparaciones orgánicas recurrentes en {pais}'"
}
```

---

## Recordatorios Finales

- Sé estricto con contradicciones de ficha técnica (son críticas)
- Sé cuidadoso con generalizaciones (especialmente modificaciones)
- Verifica que toda la información tenga respaldo en experiencias validadas
- El formato debe ser exacto según el template del Writer
- Si hay dudas, marca como advertencia, no como error crítico
- El output DEBE ser JSON válido, sin texto adicional antes o después
- Usa las estadísticas proporcionadas para validar generalizaciones
- La ficha técnica viene parseada: accede a valores buscando por `key`
- Calcula el score de calidad de manera justa pero estricta
