---
name: scraper-skill
description: This skill should be used when collecting user experiences and opinions about motorcycles from public internet sources (forums, YouTube, marketplaces, social media, blogs). It focuses exclusively on gathering information without validation or filtering.
---

# Scraper Skill

## Purpose

Collect user experiences and opinions about motorcycles from public internet sources including forums, YouTube, marketplaces, social media, and blogs. This skill is the first stage in the knowledge base generation pipeline.

## Core Responsibility

**Collection only - NO validation, NO filtering.** Gather the maximum amount of experiences and label them correctly (identified country, content type, etc.) so other skills can process them.

## Input Parameters

- `marca`: Motorcycle brand (e.g., "Hero")
- `modelo`: Motorcycle model (e.g., "Hunk 125R")
- `año`: Model year (e.g., 2025)
- `pais`: Specific country (e.g., "Colombia", "México", "Chile")

## Output Format

Return JSON with the following structure:
```json
{
  "experiencias_usuarios": [
    {
      "fuente": "URL de la fuente",
      "pais_identificado": "Colombia" | "incierto" | "otro_pais",
      "tipo_contenido": "review_propietario" | "video_youtube" | "comentario_foro" | ...,
      "fecha_aprox": "2024" | "2024-03" | "desconocida",
      "extractos_relevantes": [
        {
          "categoria": "sensaciones_frenado" | "rendimiento_real" | "comodidad" | ...,
          "texto": "Texto de la experiencia"
        }
      ],
      "menciones_specs_tecnicas": [
        {
          "spec": "sistema_frenos" | "sistema_alimentacion" | ...,
          "mencion": "Texto exacto mencionado por el usuario"
        }
      ],
      "observacion": "..." (opcional)
    }
  ]
}
```

## Search Strategies

Execute multiple varied queries to cover all possible sources:
- Search in: motorcycle forums, YouTube, marketplaces, social media, blogs
- DO NOT specify concrete domains; search broadly for the most useful sources
- Deep extraction: Read complete content, not just snippets
- Identify country in each source (mark as "incierto" if unclear)

## Prioritized Categories

Focus on collecting experiences related to:
- Riding sensations (stability, vibrations, braking, throttle response)
- Recurring problems
- Real fuel consumption reported
- Comfort in different use cases
- Behavior in rain
- Long-term reliability
- Resale value
- Organic comparisons with other models
- Popular modifications

## Critical Constraints

- **DO NOT filter experiences**: Include ALL, even if country is uncertain
- **DO NOT validate**: Only collect and label; validation is ValidatorSkill's responsibility
- **DO NOT compare with technical spec sheet**: Only extract spec mentions for later validation
- **Country-specific priority**: Prioritize information from indicated country, but DO NOT discard others (only label them)

## How to Use This Skill

To invoke the scraper functionality:

```python
from src.core.scraper_agent import ScraperAgent

scraper = ScraperAgent()
resultado = scraper.scrape(
    marca="Hero",
    modelo="Hunk 125R",
    año=2025,
    pais="Colombia"
)

experiencias = resultado.get("experiencias_usuarios", [])
```

## Implementation Details

- **Main implementation**: `src/core/scraper_agent.py`
- **Prompt template**: `src/data/input/prompts/scraper_agent_template.md`
- **Base processor**: `src/core/gemini_processor.py`

## Important Notes

- This skill does NOT have access to the technical spec sheet
- Its output is used as input for ValidatorSkill
- This is the first stage of the KB (Knowledge Base) generation pipeline
- Focus on breadth of collection rather than quality filtering
- The labeling accuracy is crucial for downstream validation
