---
name: validator-skill
description: This skill should be used when validating user experiences against official technical specifications. It operates in two levels - automatic validation (Level 1) and deep re-research (Level 2) for cases with contradictions.
---

# Validator Skill

## Purpose

Validate that user experiences correspond to the correct model and country by comparing them against the official technical spec sheet. Operates in two levels: automatic validation (Level 1) and re-research (Level 2) for ambiguous cases.

## Core Responsibility

Validate experiences against technical spec sheet to:
- Confirm they correspond to the correct model/country
- Detect contradictions between experiences and spec sheet
- Execute deep investigation (re-research) for ambiguous cases
- Classify experiences as: validated, verified (with re-research), or excluded

## Input Parameters

- `experiencias`: List of experiences from ScraperSkill
- `ficha_tecnica`: Technical spec sheet (can be dict, raw string, or list of specs)
- `marca`: Motorcycle brand
- `modelo`: Motorcycle model
- `año`: Model year
- `pais`: Specific country

## Output Format

### Level 1: Automatic Validation

Return JSON with structure:
```json
{
  "experiencias_validadas": [
    {
      "fuente": "URL",
      "pais_confirmado": true,
      "version_correcta": true,
      "confidence": 95,
      "extractos": [...],
      "menciones_specs_tecnicas": [...]
    }
  ],
  "experiencias_requieren_re_research": [
    {
      "fuente": "URL",
      "flag": "CONTRADICCION_FRENOS" | "CONTRADICCION_ALIMENTACION" | ...,
      "contradiccion_detectada": "Description",
      "experiencia_completa": {...}
    }
  ],
  "experiencias_excluidas_automatico": [
    {
      "fuente": "URL",
      "razon_exclusion": "Reason",
      "confidence_exclusion": 95
    }
  ]
}
```

### Level 2: Re-Research

For each experience with a flag, execute `re_research()` which returns:
```json
{
  "resultado": "INCLUIR" | "INCLUIR_CON_NOTA" | "EXCLUIR" | "EXCLUIR_POR_PRECAUCION",
  "razon": "Explanation",
  "confidence": 0-100,
  "pais_confirmado": true/false,
  "version_confirmada": true/false,
  "extractos_ajustados": [...] (optional),
  "nota": "..." (optional)
}
```

## Validation Process

### Level 1: Automatic Validation

**Cases that pass directly:**
- Confirmed country + mentioned specs match spec sheet → INCLUDE (confidence: 95%)

**Cases requiring re-research:**
- `CONTRADICCION_FRENOS`: User mentions different brake system (e.g., "ABS" but spec sheet says "CBS")
- `CONTRADICCION_ALIMENTACION`: User mentions different fuel system (e.g., "carburetor" but spec sheet says "Injection")
- `CONTRADICCION_CILINDRAJE`: User mentions different displacement
- `PAIS_INCIERTO`: Country is unclear and there are spec mentions
- `POSIBLE_VERSION_ANTERIOR`: Mentions suggest previous year version
- `ESPECIFICACION_AMBIGUA`: Mentions that don't match but aren't clearly contradictory

### Level 2: Re-Research

Investigate the specific source in depth to determine:
- Is the user in the correct country?
- Is the user talking about the correct model/year?
- Is the mention about their own bike or are they comparing?
- Does a special version exist with that equipment?

**Possible results:**
- **INCLUIR**: Confusion clarified, experience is valid (may require extract adjustment)
- **INCLUIR_CON_NOTA**: Valid information but from previous year, include with note
- **EXCLUIR**: Different version confirmed, doesn't apply to the country
- **EXCLUIR_POR_PRECAUCION**: Cannot verify, better to exclude

## Key Methods

### `validate()`
Execute automatic validation (Level 1) comparing experiences with spec sheet.

### `re_research()`
Execute deep investigation (Level 2) for a specific experience with a flag.

### `update_experience_after_re_research()`
Update an experience after re-research with the verification result.

## How to Use This Skill

```python
from src.core.validator_agent import ValidatorAgent

validator = ValidatorAgent()

# Level 1: Automatic validation
resultado = validator.validate(
    experiencias=experiencias,
    ficha_tecnica=ficha_tecnica,
    marca="Hero",
    modelo="Hunk 125R",
    año=2025,
    pais="Colombia"
)

# Level 2: Re-research for cases with flags
experiencias_re_research = resultado.get("experiencias_requieren_re_research", [])

for exp_re in experiencias_re_research:
    resultado_re = validator.re_research(
        experiencia=exp_re.get("experiencia_completa"),
        ficha_tecnica=ficha_tecnica,
        marca="Hero",
        modelo="Hunk 125R",
        año=2025,
        pais="Colombia",
        flag=exp_re.get("flag")
    )

    # Update experience
    experiencia_actualizada = validator.update_experience_after_re_research(
        experiencia_original=exp_re.get("experiencia_completa"),
        resultado_re_research=resultado_re
    )
```

## Implementation Details

- **Main implementation**: `src/core/validator_agent.py`
- **Validation prompt (Level 1)**: `src/data/input/prompts/validator_agent_template.md`
- **Re-research prompt (Level 2)**: `src/data/input/prompts/validator_re_research_template.md`
- **Base processor**: `src/core/gemini_processor.py`
- **Spec sheet formatting**: `src/core/base_knowledge.py`

## Important Notes

- This skill requires the technical spec sheet as input (unlike ScraperSkill)
- Its output is used as input for WriterSkill
- Re-research can be costly (performs additional web searches); consider batch processing
- This is the second stage of the pipeline, after ScraperSkill
- Accuracy in contradiction detection is critical to avoid false positives
- Balance between being thorough and being overly cautious
