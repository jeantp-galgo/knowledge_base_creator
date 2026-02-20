Proyecto: Knowledge Base Generator
Objetivo: Construir un sistema de agente orquestador con skills especializadas usando Claude Code, que automatice el flujo de investigación, validación y generación de informes.
Approach: Claude Code integrado con Gemini para obtener y procesar información de manera automática, sin depender de servicios o APIs externas adicionales.
Estructura de carpetas:
knowledge-base-generator/
│
├── .claude/
│   └── skills/
│       ├── orchestrator/
│       │   └── SKILL.md
│       ├── scraper/
│       │   ├── SKILL.md
│       │   └── scripts/
│       │       └── gemini_fetch.py
│       ├── validator/
│       │   └── SKILL.md
│       ├── writer/
│       │   └── SKILL.md
│       └── qa/
│           └── SKILL.md
│
├── inputs/
├── outputs/
├── docs/
│   └── project_context.md
└── README.md
Skills y su naturaleza:
Skill            ¿Script?  Por qué
Orchestrator     ❌        Define el contexto del proyecto y el flujo completo.
Scraper          ✅        Usa Gemini para consultar, extraer y estructurar datos de interés.
Validator        ❌        Razonamiento puro de Claude.
Writer           ❌        Generación de texto de Claude con instrucciones.
QA               ❌        Evaluación de Claude con criterios definidos.

Flujo del agente:
Orchestrator (carga contexto del proyecto)
    ↓
Scraper → obtiene datos relevantes usando Gemini
    ↓
Validator → verifica los datos recolectados
    ↓ si falla
Orchestrator → llama Scraper de nuevo con contexto del fallo
    (excluded_data, failed_sources) → evita repetir información fallida
    ↓ si aprueba
Writer → genera informe
    ↓
QA → aprueba o rechaza

Decisiones técnicas clave:

No existe skill separada de "researcher" para los reintentos. El orquestador decide cuándo y cómo reintentar, brindando contexto al Scraper sobre los datos problemáticos.
El Scraper puede recibir parámetros como excluded_data o failed_sources para no repetir información rechazada.
La calidad del sistema depende en gran medida de la claridad y detalle de los SKILL.md, especialmente el del orchestrator.
El orchestrator controla los flujos de retry, interpreta el resultado del Validator y determina cuándo finalizar el proceso.