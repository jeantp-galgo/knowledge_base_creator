Contexto del Proyecto: Sistema Multi-Agente para Knowledge Base de Motos
Objetivo
Generar knowledge bases vivenciales sobre motocicletas que capturen experiencia real de usuarios del país específico, usando specs técnicas validadas como ancla de verdad para evitar mezclar versiones/mercados incorrectos.
Problema actual
Gemini en un solo paso mezcla:

Experiencias de diferentes países
Versiones con equipamiento distinto
Años/generaciones diferentes

Resultado: KB habla de características que la moto NO tiene en ese mercado, o descarta experiencias valiosas por confusión de fuentes.
Alcance

Países: Colombia, México, Chile (se procesa uno a la vez)
Enfoque: Una moto a la vez
Input proporcionado: marca, modelo, año, país


Arquitectura Multi-Agente (3 etapas)
ETAPA 1: Agente Scraper
Propósito: Obtener 2 tipos de información separados
A) Ficha técnica de referencia (ancla de verdad)
Qué busca:

Página oficial del fabricante para el país específico
Distribuidores oficiales del país
Marketplaces oficiales como fuente secundaria

Qué extrae:
json{
  "ficha_tecnica_referencia": {
    "marca": "Hero",
    "modelo": "Hunk 125R",
    "año": 2025,
    "pais": "Colombia",
    "cilindraje": 124.7,
    "sistema_frenos": "CBS (Frenos combinados)",
    "sistema_alimentacion": "Inyección electrónica",
    "tipo_arranque": "Eléctrico y pedal",
    "potencia_hp": 11.4,
    "peso_kg": 138,
    "fuente_oficial": "https://hero.com.co/hunk-125r",
    "fecha_consulta": "2025-01-15"
  }
}
Propósito de esta ficha:

Ancla de verdad para validar que experiencias hablen de la versión correcta
NO es contenido del KB (el KB es vivencial, no técnico)
Sirve para contrastar cuando usuarios dicen cosas como:

✅ "La ficha dice 125cc pero se siente como una 150cc" → Percepción positiva, INCLUIR
✅ "Dice que tiene 11hp pero se siente más potente" → Validación vivencial, INCLUIR
⚠️ "Los frenos ABS funcionan bien" → Si la ficha dice CBS, necesita verificación



Reglas:

Buscar SOLO del país especificado
Si no encuentra ficha oficial → marcar nivel_confianza: "bajo"
No extrapolar de otros países


B) Experiencias y opiniones de usuarios
Qué busca:

Foros de motociclistas del país
Reviews en YouTube (verificar que sea del país correcto)
Marketplaces con opiniones de compradores
Grupos de Facebook/redes sociales del país
Blogs de usuarios locales

Qué extrae:
json{
  "experiencias_usuarios": [
    {
      "fuente": "https://foromoto.com/hero-hunk-colombia/thread-123",
      "pais_identificado": "Colombia",
      "tipo_contenido": "review_propietario",
      "fecha_aprox": "2024",
      "extractos_relevantes": [
        {
          "categoria": "sensaciones_frenado",
          "texto": "El frenado CBS funciona bien en ciudad pero en carretera hay que anticiparse más"
        },
        {
          "categoria": "rendimiento_real",
          "texto": "Consume 45-50 km/l real en ciudad, no los 60 que promete la ficha"
        },
        {
          "categoria": "comodidad",
          "texto": "Las vibraciones a 80 km/h son molestas en viajes largos"
        }
      ],
      "menciones_specs_tecnicas": [
        {
          "spec": "sistema_frenos",
          "mencion": "CBS",
          "coincide_con_ficha": true
        },
        {
          "spec": "consumo",
          "valor_mencionado": "45-50 km/l",
          "contexto": "uso ciudad"
        }
      ]
    },
    {
      "fuente": "https://youtube.com/review-hero-hunk",
      "pais_identificado": "incierto",
      "observacion": "No se menciona país explícitamente, revisar contenido",
      "extractos_relevantes": [
        {
          "categoria": "sensaciones_frenado",
          "texto": "Los frenos ABS me salvaron en una frenada de emergencia"
        }
      ],
      "menciones_specs_tecnicas": [
        {
          "spec": "sistema_frenos",
          "mencion": "ABS",
          "coincide_con_ficha": false,
          "flag": "REQUIERE_VERIFICACION"
        }
      ]
    }
  ]
}
```

**Categorías de extractos a priorizar:**
- Sensaciones de manejo (estabilidad, vibraciones, frenado, respuesta acelerador)
- Problemas recurrentes
- Consumo real reportado
- Comodidad en diferentes usos
- Comportamiento en lluvia
- Confiabilidad en el tiempo
- Valor de reventa
- Comparaciones orgánicas con otros modelos
- Modificaciones populares

**Reglas:**
- Marcar país identificado en cada fuente
- Si país no es claro → flag: "REQUIERE_VERIFICACION"
- Extraer menciones de specs técnicas para cross-check posterior
- NO filtrar todavía, solo recolectar y etiquetar

---

### **ETAPA 2: Agente Validator**
**Propósito:** Validar que experiencias correspondan al modelo/país correcto mediante verificación en dos niveles

#### **Nivel 1: Validación automática (confianza alta)**

**Casos que pasan directamente:**
```
✅ País confirmado + specs mencionadas coinciden con ficha
Ejemplo:
- Fuente menciona "Colombia" explícitamente
- Usuario dice "los frenos CBS..."
- Ficha técnica Colombia: sistema_frenos = "CBS"
→ Confidence: 95%, INCLUIR sin más verificación
```

**Casos que requieren verificación (Nivel 2):**
```
⚠️ Contradicción entre experiencia y ficha técnica
Ejemplo 1:
- Usuario dice: "Los frenos ABS funcionan muy bien"
- Ficha técnica Colombia: sistema_frenos = "CBS"
→ Flag: CONTRADICCION_FRENOS, enviar a re-research

Ejemplo 2:
- Usuario dice: "El carburador se ahoga en frío"
- Ficha técnica 2025: sistema_alimentacion = "Inyección electrónica"
→ Flag: POSIBLE_VERSION_ANTERIOR, enviar a re-research

Nivel 2: Re-research (verificación profunda)
Cuando se detecta flag, el validator hace:
Acción 1: Verificar contexto de la fuente
python# Validator ejecuta búsqueda específica
re_research_prompt = f"""
Investiga esta fuente específica: {fuente_flaggeada}

Verifica:
1. ¿El usuario está en {pais}?
2. ¿Está hablando del modelo {modelo} año {año}?
3. ¿La mención de ABS es de su moto o está comparando con otro modelo?
4. ¿Existe una versión especial en {pais} con ese equipamiento?

Retorna:
- pais_confirmado: true/false
- version_confirmada: true/false
- contexto_aclarado: "explicación"
"""
Posibles resultados del re-research:
Caso A: Confusión aclarada → INCLUIR
json{
  "resultado": "INCLUIR",
  "razon": "Usuario menciona 'me gustaría que tuviera ABS como la Pulsar',
           estaba comparando, NO diciendo que su Hunk tiene ABS",
  "extracto_ajustado": "Le falta ABS comparado con competencia",
  "confidence": 90
}
Caso B: Versión diferente → EXCLUIR
json{
  "resultado": "EXCLUIR",
  "razon": "Usuario confirmado en India, la versión india SÍ tiene ABS,
           no aplica para Colombia",
  "confidence": 95
}
Caso C: Información válida pero de año anterior → MARCAR
json{
  "resultado": "INCLUIR_CON_NOTA",
  "razon": "Usuario tiene Hunk 125R 2023 (carburada),
           pero problema de vibraciones aplica a todas las versiones",
  "nota": "Reportado en versión 2023, verificar si persiste en 2025",
  "confidence": 70
}
Caso D: No se puede verificar → EXCLUIR con precaución
json{
  "resultado": "EXCLUIR_POR_PRECAUCION",
  "razon": "No se pudo confirmar país ni versión,
           riesgo de contaminar KB con info incorrecta",
  "confidence": 30
}

Output del Validator:
json{
  "ficha_validada": {
    "cilindraje": 124.7,
    "sistema_frenos": "CBS",
    "confidence": 95
  },

  "experiencias_validadas": [
    {
      "fuente": "foromoto.com/...",
      "pais_confirmado": true,
      "version_correcta": true,
      "confidence": 95,
      "extractos": ["..."]
    }
  ],

  "experiencias_verificadas_incluir": [
    {
      "fuente": "youtube.com/...",
      "resultado_re_research": "Usuario comparaba con otra moto,
                                no decía que su Hunk tiene ABS",
      "confidence": 90,
      "extractos_ajustados": ["Le falta ABS vs competencia"]
    }
  ],

  "experiencias_excluidas": [
    {
      "fuente": "blog-motos-india.com/...",
      "razon_exclusion": "Versión India confirmada,
                          equipamiento diferente a Colombia",
      "confidence_exclusion": 95
    }
  ],

  "casos_ambiguos_revision_manual": [
    {
      "fuente": "...",
      "problema": "Re-research no concluyente, revisar manualmente",
      "confidence": 50
    }
  ]
}

ETAPA 3: Agente Writer
Propósito: Generar KB vivencial usando experiencias validadas + ficha como ancla
Input:

Ficha técnica validada (ancla de verdad)
Experiencias validadas (contenido real del KB)
Experiencias verificadas con contexto ajustado
Tu template/prompt actual

Restricciones críticas:

Respeto al ancla técnica:

python# Si ficha dice sistema_frenos = "CBS"
# Writer NO puede escribir: "Los frenos ABS..."
# Writer SÍ puede escribir:
#   - "El frenado CBS se siente..."
#   - "Comparado con motos con ABS, el CBS requiere..."
#   - "Los usuarios extrañan el ABS de modelos superiores..."

Uso de percepciones vs ficha:

python# PERMITIDO y DESEABLE:
"La ficha dice 125cc pero se siente como una 150cc" → INCLUIR
"Dice 11hp pero tiene mejor respuesta que motos de más potencia" → INCLUIR

# Estas percepciones SON contenido valioso del KB

Manejo de comparaciones:

python# Si usuario dice: "Me gustaría que tuviera ABS como la Pulsar"
# Writer puede incluir en [OPINIONES_DIVIDIDAS] o [COMPARACIONES]:
"Usuarios que vienen de motos con ABS extrañan esa tecnología,
 aunque valoran el menor costo de mantenimiento del CBS"
Proceso:
pythonprompt_writer = f"""
{tu_prompt_actual}

FICHA TÉCNICA VALIDADA (ancla de verdad):
Sistema de frenos: {ficha['sistema_frenos']}
Sistema alimentación: {ficha['sistema_alimentacion']}
Cilindraje: {ficha['cilindraje']}

EXPERIENCIAS VALIDADAS:
{experiencias_validadas}

RESTRICCIONES:
- En [SENSACIONES] > Frenado: solo mencionar {ficha['sistema_frenos']}
- Consumo real: usar promedios de experiencias validadas
- Comparaciones con otros modelos: permitidas y deseables
- Percepciones que contrastan con ficha: INCLUIR (son valiosas)

PERMISOS:
- "Se siente más potente de lo que indica la ficha" → OK
- "Usuarios esperaban ABS pero tiene CBS" → OK en [OPINIONES_DIVIDIDAS]
- "Comparado con la Pulsar 200 (con ABS)..." → OK en [COMPARACIONES]
"""
```

**Output:** KB en formato de tu template actual

---

## Flujo completo resumido
```
INPUT: {marca: "Hero", modelo: "Hunk 125R", año: 2025, pais: "Colombia"}
   ↓
SCRAPER:
├─ Busca ficha oficial → sistema_frenos: "CBS"
└─ Recopila experiencias → algunas mencionan "ABS"
   ↓
VALIDATOR - Nivel 1:
├─ Experiencias que coinciden → INCLUIR ✓
├─ Experiencias con contradicción → Flag: REQUIERE_VERIFICACION
   ↓
VALIDATOR - Nivel 2 (Re-research):
├─ Verifica contexto de cada fuente flaggeada
├─ "Usuario comparaba, no decía que tiene ABS" → INCLUIR con ajuste ✓
├─ "Versión India, diferente equipamiento" → EXCLUIR
└─ "No se puede verificar" → EXCLUIR por precaución
   ↓
VALIDATOR Output:
├─ experiencias_validadas (alta confianza)
├─ experiencias_verificadas_incluir (con contexto ajustado)
└─ experiencias_excluidas (con razón)
   ↓
WRITER:
└─ Genera KB usando experiencias validadas + ancla técnica
   Resultado: KB consistente con versión correcta del país

Ventajas del enfoque
1. No descarta experiencias valiosas prematuramente

Re-research aclara contextos ambiguos
Comparaciones de usuarios son contenido valioso
Percepciones vs ficha técnica enriquecen el KB

2. Filtra contaminación de otros mercados

Verifica cuando hay sospecha real de mezcla de versiones
Excluye solo cuando hay certeza de incompatibilidad

3. Mantiene consistencia técnica

Ficha validada = ancla que writer respeta
Experiencias validadas = contenido rico y contextualizado

4. Trazabilidad completa

Cada experiencia incluida/excluida tiene justificación
Re-research documenta proceso de verificación
Auditable en caso de dudas