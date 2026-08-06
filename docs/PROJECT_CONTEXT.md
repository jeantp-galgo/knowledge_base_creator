# deep_research_models — Contexto del Proyecto

## Que es

Sistema de generacion automatica de bases de conocimiento (KB) experienciales sobre motocicletas para mercados latinoamericanos (Colombia, Mexico, Chile), usando Google Gemini con capacidades de investigacion web activa.

Las KBs capturan la experiencia real de poseer y usar una moto: que falla, como se siente en la calle, con quien se compara organicamente, si vale la pena. No son fichas tecnicas; son lo que un amigo con la moto te contaria. Son activos de datos reutilizables que pueden alimentar chatbots, contenido editorial y dashboards de percepcion de marca.

## Estado (2026-04-10)

### Completado
- Enfoque Direct Research operativo y validado en modelos de CO y MX
- Refactorizacion: se eliminaron los 4 agentes del pipeline anterior (Scraper, Validator, Writer, QA)

### En progreso
-

### Por hacer
- Procesar batch completo de modelos por pais

## Flujo general

```text
CSV Inventario
     |
     v
direct_research.ipynb
     |
     v
Seleccionar modelo (code)
     |
     v
Construir prompt con ficha tecnica + instrucciones de busqueda
     |
     v
Gemini (gemini-3-pro-preview) — busqueda web activa, multiple iteracion interna
     |
     v
KB generada (.md)  →  src/data/output/gemini/{PAIS}-{MARCA}_{MODELO}-direct.md
```

## Arquitectura

```
deep_research_models/
├── notebooks/
│   └── direct_research.ipynb        # Punto de entrada unico
├── src/
│   ├── config/settings.py           # Pais activo, rutas CSV
│   ├── core/
│   │   ├── gemini_processor.py      # Cliente Gemini — send_prompt() con google_search
│   │   ├── base_knowledge.py        # Formatea ficha tecnica para el prompt
│   │   └── prompt_utils.py          # Lee templates y reemplaza variables {VAR}
│   ├── sources/inventory/app.py     # Carga CSV de inventario por pais
│   └── data/
│       ├── input/prompts/
│       │   └── direct_research_template.md  # Template unico del prompt
│       ├── input/processed_codes/   # Codigos de modelos ya procesados por pais
│       └── output/gemini/           # KBs generadas (.md)
├── context/                         # Documentacion del proyecto
├── trash/                           # Archivos descartados (no usar)
├── .env_example
└── requirements.txt
```

| Archivo | Funcion |
|---|---|
| `notebooks/direct_research.ipynb` | Orquesta la generacion: carga DB, arma prompt, llama a Gemini, guarda KB |
| `src/core/gemini_processor.py` | Wrapper de Gemini: maneja recitation blocks, concatena outputs |
| `src/core/base_knowledge.py` | Convierte la lista de specs tecnicas en texto estructurado para el prompt |
| `src/core/prompt_utils.py` | `read_prompt_from_file`, `replace_variables`, `validate_prompt_variables` |
| `src/sources/inventory/app.py` | Carga el CSV del pais configurado como DataFrame |
| `src/data/input/prompts/direct_research_template.md` | Prompt con rol de investigador, 6 queries de busqueda y formato de salida |

## Output

Archivo `.md` de texto plano con 15 secciones fijas, guardado en:

```
src/data/output/gemini/{PAIS}-{MARCA}_{MODELO}-direct.md
```

Secciones: `[SEGMENTO]`, `[SENTIMIENTO]`, `[SENSACIONES]`, `[VENTAJAS]`, `[PROBLEMAS]`, `[CAUSA_EFECTO]`, `[RENDIMIENTO]`, `[CONFIABILIDAD]`, `[REVENTA]`, `[MODIFICACIONES]`, `[PERFIL_USUARIO]`, `[OPINIONES_DIVIDIDAS]`, `[LIMITACIONES]`, `[COMPARACIONES]`, `[SINTESIS]`

## Stack tecnico

| Tecnologia | Uso |
|---|---|
| Python 3.9+ | Lenguaje principal |
| Jupyter Notebook | Entorno de ejecucion |
| Google Gemini (`gemini-3-pro-preview`) | Modelo de investigacion y generacion |
| `google-genai` | SDK de Gemini (interactions API con grounded search) |
| pandas | Carga y filtracion del CSV de inventario |
| python-dotenv | Carga de variables de entorno |

## Requisitos

- `GEMINI_API_KEY` en el archivo `.env`
- CSVs de inventario por pais (`BaseCO.csv`, `BaseMX.csv`, `BaseCL.csv`) — rutas configuradas en `settings.py`, generados por el proyecto `historical_data`

## Relacion con otros proyectos

- `historical_data` genera los CSVs `BaseCO.csv`, `BaseMX.csv`, `BaseCL.csv` que este proyecto consume
- `deep_research_models_orchestrator` es una reimplementacion de este proyecto como skills de Claude Code
