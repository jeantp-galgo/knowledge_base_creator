# Agente Validator - Re-Research (Nivel 2)

## Objetivo

Investigar en profundidad una experiencia que tiene contradicciones con la ficha técnica para determinar si debe incluirse, excluirse o incluirse con nota.

---

## Contexto

**Marca:** {MARCA}
**Modelo:** {MODELO}
**Año:** {AÑO}
**País:** {PAIS}
**Flag detectado:** {FLAG}

---

## Ficha Técnica de Referencia

{FICHA_TECNICA}

---

## Experiencia a Investigar

{EXPERIENCIA}

---

## Instrucciones de Re-Research

Investiga esta fuente específica en profundidad. Busca:

1. **Confirmación de país**: ¿El usuario está realmente en {PAIS}?
2. **Confirmación de versión**: ¿Está hablando del modelo {MODELO} año {AÑO}?
3. **Contexto de la mención**:
   - Si menciona specs diferentes, ¿está diciendo que SU moto tiene eso?
   - ¿O está comparando con otra moto?
   - ¿O está expresando un deseo ("me gustaría que tuviera...")?
4. **Versiones especiales**: ¿Existe alguna versión especial en {PAIS} con ese equipamiento?
5. **Año del comentario**: ¿El comentario es del año correcto o de una versión anterior?

### Búsquedas Específicas a Realizar

- Busca la URL de la fuente directamente
- Busca contexto adicional sobre esa fuente
- Busca si hay versiones especiales del modelo en {PAIS}
- Verifica si otros usuarios en {PAIS} confirman o contradicen esa información

---

## Posibles Resultados

### Caso A: Confusión Aclarada → INCLUIR

El usuario estaba comparando, expresando deseo, o había un malentendido. La experiencia es válida pero necesita ajuste.

```json
{
  "resultado": "INCLUIR",
  "razon": "Explicación clara de por qué la contradicción era solo aparente",
  "pais_confirmado": true,
  "version_confirmada": true,
  "contexto_aclarado": "Detalle del contexto que aclara la situación",
  "extractos_ajustados": [
    {
      "categoria": "...",
      "texto": "Texto ajustado que refleja el contexto real"
    }
  ],
  "confidence": 90
}
```

### Caso B: Versión Diferente → EXCLUIR

El usuario está en otro país o tiene una versión diferente que no aplica para {PAIS}.

```json
{
  "resultado": "EXCLUIR",
  "razon": "Usuario confirmado en [país], la versión de ese país tiene equipamiento diferente, no aplica para {PAIS}",
  "pais_confirmado": false,
  "version_confirmada": false,
  "confidence": 95
}
```

### Caso C: Información Válida pero de Año Anterior → INCLUIR_CON_NOTA

La experiencia es válida pero de una versión anterior. Puede ser útil si el problema/comentario aplica a todas las versiones.

```json
{
  "resultado": "INCLUIR_CON_NOTA",
  "razon": "Usuario tiene {MODELO} {año_anterior} (con [spec diferente]), pero [aspecto] aplica a todas las versiones",
  "nota": "Reportado en versión {año_anterior}, verificar si persiste en {AÑO}",
  "confidence": 70,
  "extractos_ajustados": [...]
}
```

### Caso D: No se Puede Verificar → EXCLUIR_POR_PRECAUCION

No se pudo confirmar país ni versión. Mejor excluir para no contaminar la KB.

```json
{
  "resultado": "EXCLUIR_POR_PRECAUCION",
  "razon": "No se pudo confirmar país ni versión, riesgo de contaminar KB con info incorrecta",
  "confidence": 30
}
```

---

## Formato de Salida

Retorna ÚNICAMENTE un JSON válido con uno de los formatos de resultado arriba, según lo que determines en tu investigación.

---

## Recordatorios Finales

- Investiga la fuente específica en profundidad
- Busca contexto adicional, no solo la mención aislada
- Si el usuario estaba comparando o expresando deseo, ajusta el extracto
- Si es de otro país/versión, excluye con razón clara
- Si no puedes verificar, excluye por precaución
- El output DEBE ser JSON válido, sin texto adicional
