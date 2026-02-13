---
name: qa-skill
description: This skill should be used when validating the quality of generated Knowledge Bases. It verifies consistency, appropriate generalizations, correct formatting, and ensures no invented information or contradictions exist.
---

# QA Skill

## Purpose

Validate the quality of the generated Knowledge Base. Verifies consistency, appropriate generalizations, correct format, and that there is no invented information or contradictions.

## Core Responsibility

Validate the final KB to ensure:
- Consistency with technical spec sheet (does not contradict critical specs)
- Appropriate generalizations based on evidence quantity
- Correct format according to template
- No internal contradictions
- All information is backed by validated experiences
- Correct use of spec sheet (as anchor, not as content)

## Input Parameters

- `knowledge_base`: Generated KB (string) - output from WriterSkill
- `ficha_tecnica`: Technical spec sheet (can be dict, raw string, or list of specs)
- `experiencias_validadas`: List of validated experiences used to generate the KB
- `experiencias_verificadas`: List of verified experiences used to generate the KB
- `marca`: Motorcycle brand
- `modelo`: Motorcycle model
- `año`: Model year
- `pais`: Specific country

## Output Format

Return JSON with validation result:
```json
{
  "validacion_aprobada": true | false,
  "score_calidad": 0-100,
  "problemas_criticos": [
    {
      "tipo": "CONTRADICCION_FICHA" | "GENERALIZACION_INAPROPIADA" | "FORMATO_INCORRECTO" | "CONTRADICCION_INTERNA" | "INFORMACION_INVENTADA" | "USO_INCORRECTO_FICHA",
      "seccion": "[SECTION] where the problem is",
      "descripcion": "Detailed problem description",
      "severidad": "alta" | "media" | "baja",
      "sugerencia_correccion": "How to correct it"
    }
  ],
  "advertencias": [
    {
      "tipo": "GENERALIZACION_LIMITE" | "INFORMACION_LIMITADA" | "OTRO",
      "seccion": "[SECTION]",
      "descripcion": "Warning about something that could be improved",
      "sugerencia": "Improvement suggestion"
    }
  ],
  "aspectos_correctos": [
    "List of well-implemented aspects"
  ],
  "resumen": "Overall validation summary"
}
```

## Validation Aspects

### 1. Consistency with Technical Spec Sheet

Verify that the KB does NOT contradict the spec sheet on critical specs:
- **Brake system**: If spec sheet says "CBS", KB must NOT say "ABS"
- **Fuel system**: If spec sheet says "Carbureted", KB must NOT say "Injection"
- **Displacement**: Must match spec sheet
- **Starting system**: Must match spec sheet

**ALLOWED:**
- Perceptions that contrast: "The spec sheet says 125cc but it feels like 150cc"
- Comparisons: "Compared to bikes with ABS, the CBS requires..."
- Opinions: "Users expected ABS but it has CBS"

**PROHIBITED:**
- Write that it has ABS when spec sheet says CBS
- Contradict any technical spec from the sheet

### 2. Appropriate Generalizations

Verify that language is appropriate based on evidence quantity:

**Modifications:**
- 1 example → Must say "A user has modified..." (NOT "Users modify...")
- 2 examples → Must say "Some users have modified..."
- 3+ examples → Can use "Some users modify..." or list

**Other aspects:**
- 1 example → "A user reports..." or "One case documented..."
- 2-3 examples → "Some users report..." or "There are reports of..."
- 4+ examples → "Users report..." or "It is common that..."

### 3. Correct Format

Verify:
- All required sections present: [SEGMENTO], [SENTIMIENTO], [SENSACIONES], [VENTAJAS], [PROBLEMAS], [CAUSA_EFECTO], [RENDIMIENTO], [CONFIABILIDAD], [REVENTA], [MODIFICACIONES], [PERFIL_USUARIO], [OPINIONES_DIVIDIDAS], [LIMITACIONES], [COMPARACIONES], [SINTESIS]
- Plain text format (no markdown, no bold, no italics)
- Headers with format `[SECTION]` followed by blank line
- Correct [PROBLEMAS] structure (Name, Frequency, Description, Context, Community solution)

### 4. Internal Contradictions

Verify that the KB does not contradict itself:
- If it says "very powerful" in one section, it should not say "low power" in another without explaining context
- Comparisons should be coherent
- Information should be consistent across sections

### 5. Information Backed by Experiences

Verify that:
- Does NOT invent problems that are not in the experiences
- Does NOT add advantages not mentioned in the experiences
- Does NOT complete information without evidence
- If there is insufficient information, explicitly declares it

### 6. Correct Use of Technical Spec Sheet

Verify that:
- The spec sheet is used as anchor, NOT as KB content
- Does NOT repeat technical information from the sheet as if it were user experience
- Uses the sheet for contrast, not for description

## Approval Criteria

The KB is approved if:
- ✅ NO contradictions with the spec sheet
- ✅ Generalizations are appropriate based on evidence
- ✅ Format is correct
- ✅ NO invented information
- ✅ Required sections are present

The KB is NOT approved if:
- ❌ There are critical contradictions with the spec sheet
- ❌ Generalizes inappropriately (e.g., "Users modify..." with 1 example)
- ❌ Critical sections are missing
- ❌ There is clearly invented information

## How to Use This Skill

```python
from src.core.qa_agent import QAAgent

qa = QAAgent()

resultado_qa = qa.validate(
    knowledge_base=knowledge_base,
    ficha_tecnica=ficha_tecnica,
    experiencias_validadas=experiencias_validadas,
    experiencias_verificadas=experiencias_verificadas,
    marca="Hero",
    modelo="Hunk 125R",
    año=2025,
    pais="Colombia"
)

# Verify result
if resultado_qa.get("validacion_aprobada"):
    print("✅ KB approved")
else:
    print("❌ KB has critical problems")
    for problema in resultado_qa.get("problemas_criticos", []):
        print(f"  - {problema.get('tipo')}: {problema.get('descripcion')}")
```

## Result Interpretation

- **validacion_aprobada: true**: The KB passes all critical validations
- **validacion_aprobada: false**: There are critical problems that must be corrected
- **score_calidad**: 0-100, indicates overall KB quality
- **problemas_criticos**: List of problems that must be corrected before using the KB
- **advertencias**: Suggested improvements but not critical
- **aspectos_correctos**: What is well implemented

## Implementation Details

- **Main implementation**: `src/core/qa_agent.py`
- **Prompt template**: `src/data/input/prompts/qa_agent_template.md`
- **Base processor**: `src/core/gemini_processor.py`
- **Spec sheet formatting**: `src/core/base_knowledge.py`

## Important Notes

- This skill validates the final output from WriterSkill
- This is the last stage of the pipeline before saving the KB
- Calculates evidence statistics to validate generalizations
- If the KB does not pass, it may require regeneration or manual correction
- This is the fourth and final stage of the complete pipeline
- Quality threshold should balance rigor with practicality
- Some warnings may be acceptable depending on use case
