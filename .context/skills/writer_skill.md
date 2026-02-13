---
name: writer-skill
description: This skill should be used when generating the final experiential Knowledge Base using validated experiences and the technical spec sheet as a truth anchor. It generates a structured report capturing real user experiences, not technical specifications.
---

# Writer Skill

## Purpose

Generate the final experiential Knowledge Base using validated experiences and the technical spec sheet as the truth anchor. Produces a structured report that captures the real user experience, not technical specifications.

## Core Responsibility

Generate the final KB that:
- Uses validated experiences as primary content
- Respects the spec sheet as truth anchor (does not contradict it)
- Uses appropriate generalizations based on evidence quantity
- Generates experiential and emotional content, not technical content

## Input Parameters

- `experiencias_validadas`: List of directly validated experiences (Level 1 from ValidatorSkill)
- `experiencias_verificadas`: List of re-research verified experiences (Level 2 from ValidatorSkill)
- `ficha_tecnica`: Technical spec sheet (can be dict, raw string, or list of specs)
- `marca`: Motorcycle brand
- `modelo`: Motorcycle model
- `año`: Model year
- `pais`: Specific country
- `tipo`: Motorcycle type (e.g., "Urbana", "Deportiva") - optional

## Output Format

Returns a string with the Knowledge Base in structured format with the following sections:

```
[SEGMENTO]
[SENTIMIENTO]
[SENSACIONES]
[VENTAJAS]
[PROBLEMAS]
[CAUSA_EFECTO]
[RENDIMIENTO]
[CONFIABILIDAD]
[REVENTA]
[MODIFICACIONES]
[PERFIL_USUARIO]
[OPINIONES_DIVIDIDAS]
[LIMITACIONES]
[COMPARACIONES]
[SINTESIS]
```

## Generation Process

1. **Combine experiences**: Merge validated + verified experiences
2. **Calculate statistics**: Count evidence per category to guide generalizations
3. **Generate generalization instructions**: Adjust language based on data quantity
4. **Generate KB**: Use the template with all restrictions and permissions

## Critical Constraints

### Respect for Technical Spec Sheet (Truth Anchor)

- **PROHIBITED**: Contradict technical specs from the spec sheet
  - If spec sheet says "CBS", DO NOT write "ABS"
  - If spec sheet says "Carbureted", DO NOT write "Injection"

- **ALLOWED**: Mention perceptions that contrast
  - "The spec sheet says 125cc but it feels like 150cc" ✅
  - "Says 11hp but feels more powerful" ✅

- **ALLOWED**: Comparisons and opinions
  - "Compared to bikes with ABS, the CBS requires..." ✅
  - "Users expected ABS but it has CBS" ✅ (in [OPINIONES_DIVIDIDAS])

### Appropriate Generalizations

The WriterSkill automatically calculates statistics and adjusts language:

- **1 example**: "A user reports..." or "One case documented..."
- **2-3 examples**: "Some users report..." or "There are reports of..."
- **4+ examples**: "Users report..." or "It is common that..."

**Special care with modifications:**
- 1-2 examples → "Some users have modified..." (DO NOT generalize)
- 3+ examples → Can use "Some users modify..." or list modifications

## Special Features

### Automatic Statistics Calculation

The WriterSkill calculates:
- Total experiences
- Distribution by category (sensations, problems, consumption, etc.)
- Number of modification examples

These statistics are used to generate specific instructions on how to handle generalizations.

### Dynamic Generalization Instructions

Based on statistics, the WriterSkill generates specific instructions:
- If there is 1 modification → Instructs: "DO NOT generalize, say 'A user has modified...'"
- If there are 2 modifications → Instructs: "Use 'Some users have modified...'"
- If there are 3+ → Allows more generalization

## How to Use This Skill

```python
from src.core.writer_agent import WriterAgent

writer = WriterAgent()

knowledge_base = writer.write(
    experiencias_validadas=experiencias_validadas,
    experiencias_verificadas=experiencias_verificadas,
    ficha_tecnica=ficha_tecnica,
    marca="Hero",
    modelo="Hunk 125R",
    año=2025,
    pais="Colombia",
    tipo="Urbana"  # optional
)

# Save KB
with open('knowledge_base.md', 'w', encoding='utf-8') as f:
    f.write(knowledge_base)
```

## Output Format Details

The KB follows the format of the `knowledge_base_template.md` template:
- Plain text (no markdown, no bold)
- Sections with format `[SECTION]` followed by blank line
- Specific [PROBLEMAS] structure (Name, Frequency, Description, Context, Community solution)
- Exact section order

## Implementation Details

- **Main implementation**: `src/core/writer_agent.py`
- **Prompt template**: `src/data/input/prompts/knowledge_base_template.md`
- **Base processor**: `src/core/gemini_processor.py`
- **Spec sheet formatting**: `src/core/base_knowledge.py`

## Important Notes

- This skill requires already validated experiences (output from ValidatorSkill)
- Uses the spec sheet as anchor, NOT as KB content
- The KB is experiential, NOT technical (does not repeat specs from the sheet)
- This is the third stage of the pipeline, after ValidatorSkill
- Its output is validated with QASkill
- Focus on the "why" over the "what" - emotional and practical insights
- The tone should feel like advice from a friend who owns the bike, not a sales brochure
