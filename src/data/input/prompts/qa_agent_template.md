# Agente QA - Validación de Knowledge Base

## Objetivo

Validar la calidad del Knowledge Base generado para {MARCA} {MODELO} {AÑO} en {PAIS}. Verificar consistencia, generalizaciones apropiadas, formato y que no haya información inventada.

---

## Ficha Técnica de Referencia (Ancla de Verdad)

{FICHA_TECNICA}

---

## Knowledge Base a Validar

{KNOWLEDGE_BASE}

---

## Experiencias Validadas Usadas

{EXPERIENCIAS}

---

## Estadísticas de Evidencia

{ESTADISTICAS}

---

## Aspectos a Validar

### 1. Consistencia con Ficha Técnica

Verifica que el KB NO contradiga la ficha técnica en specs críticos:

- **Sistema de frenos**: Si ficha dice "CBS", el KB NO debe decir "ABS"
- **Sistema de alimentación**: Si ficha dice "Carburada", el KB NO debe decir "Inyección"
- **Cilindraje**: Si ficha dice "124.7 cc", el KB NO debe decir "150cc"
- **Sistema de arranque**: Debe coincidir con la ficha

**PERMITIDO:**
- Mencionar percepciones que contrastan: "La ficha dice 125cc pero se siente como 150cc"
- Comparaciones: "Comparado con motos con ABS, el CBS requiere..."
- Opiniones: "Usuarios esperaban ABS pero tiene CBS"

**PROHIBIDO:**
- Escribir que tiene ABS cuando la ficha dice CBS
- Escribir que tiene inyección cuando la ficha dice carburador
- Contradecir cualquier spec técnico de la ficha

### 2. Generalizaciones Apropiadas

Verifica que el lenguaje sea apropiado según la cantidad de evidencia:

**Modificaciones:**
- 1 ejemplo → Debe decir "Un usuario ha modificado..." o "Se ha documentado un caso de..."
- 2 ejemplos → Debe decir "Algunos usuarios han modificado..."
- 3+ ejemplos → Puede decir "Algunos usuarios modifican..." o listar las modificaciones

**Otros aspectos:**
- 1 ejemplo → "Un usuario reporta..." o "Se ha documentado..."
- 2-3 ejemplos → "Algunos usuarios reportan..." o "Hay reportes de..."
- 4+ ejemplos → "Los usuarios reportan..." o "Es común que..."

**PROHIBIDO:**
- Generalizar con "Los usuarios modifican..." cuando hay 1-2 ejemplos
- Usar "Es común..." cuando hay muy pocos datos
- Afirmar algo como general cuando es un caso aislado

### 3. Formato Correcto

Verifica que el KB tenga:
- Todas las secciones requeridas: [SEGMENTO], [SENTIMIENTO], [SENSACIONES], [VENTAJAS], [PROBLEMAS], [CAUSA_EFECTO], [RENDIMIENTO], [CONFIABILIDAD], [REVENTA], [MODIFICACIONES], [PERFIL_USUARIO], [OPINIONES_DIVIDIDAS], [LIMITACIONES], [COMPARACIONES], [SINTESIS]
- Formato de texto plano (sin markdown, sin negritas, sin cursivas)
- Encabezados con formato [SECCION] seguidos de línea en blanco
- Estructura de [PROBLEMAS] correcta (Nombre, Frecuencia, Descripción, Contexto, Solución comunitaria)

### 4. Contradicciones Internas

Verifica que el KB no se contradiga a sí mismo:
- Si dice "muy potente" en una sección, no debe decir "poca potencia" en otra sin explicar el contexto
- Si menciona un problema, debe ser consistente en toda la descripción
- Las comparaciones deben ser coherentes

### 5. Información Respalda por Experiencias

Verifica que la información del KB esté respaldada por las experiencias validadas:
- NO debe inventar problemas que no están en las experiencias
- NO debe agregar ventajas que no se mencionan en las experiencias
- NO debe completar información que no tiene evidencia
- Si no hay información suficiente, debe declararlo explícitamente

### 6. Uso Correcto de Ficha Técnica

Verifica que:
- La ficha técnica se use como ancla, NO como contenido del KB
- NO repita información técnica de la ficha como si fuera experiencia de usuario
- Use la ficha para contrastar, no para describir

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
      "descripcion": "Descripción detallada del problema",
      "severidad": "alta" | "media" | "baja",
      "sugerencia_correccion": "Cómo corregirlo"
    }
  ],
  "advertencias": [
    {
      "tipo": "GENERALIZACION_LIMITE" | "INFORMACION_LIMITADA" | "OTRO",
      "seccion": "[SECCION]",
      "descripcion": "Advertencia sobre algo que podría mejorarse",
      "sugerencia": "Sugerencia de mejora"
    }
  ],
  "aspectos_correctos": [
    "Lista de aspectos que están bien implementados"
  ],
  "resumen": "Resumen general de la validación"
}
```

---

## Criterios de Aprobación

El KB se aprueba si:
- ✅ NO hay contradicciones con la ficha técnica
- ✅ Las generalizaciones son apropiadas según la evidencia
- ✅ El formato es correcto
- ✅ NO hay información inventada
- ✅ Las secciones requeridas están presentes

El KB NO se aprueba si:
- ❌ Hay contradicciones críticas con la ficha técnica
- ❌ Generaliza inapropiadamente (ej: "Los usuarios modifican..." con 1 ejemplo)
- ❌ Faltan secciones críticas
- ❌ Hay información claramente inventada

---

## Recordatorios Finales

- Sé estricto con contradicciones de ficha técnica (son críticas)
- Sé cuidadoso con generalizaciones (especialmente modificaciones)
- Verifica que toda la información tenga respaldo en experiencias
- El formato debe ser exacto según el template
- Si hay dudas, marca como advertencia, no como error crítico
- El output DEBE ser JSON válido, sin texto adicional
