# Deep Research Models - Knowledge Base Generator

## Descripción del Proyecto

Sistema automatizado para generar bases de conocimiento experienciales sobre motocicletas usando inteligencia artificial. Estas bases de conocimiento son activos de datos independientes diseñados para ser consumidos por múltiples sistemas (chatbots, dashboards, generación de contenido, análisis comparativo, etc.).

## Objetivo Principal

Capturar la experiencia real y emocional de poseer y usar una motocicleta, NO las especificaciones técnicas de manuales.

El sistema responde preguntas como:
- "¿Realmente vale la pena?"
- "¿Qué me va a molestar después de 6 meses de uso?"
- "¿Me va a dejar tirado?"
- "¿Es mejor que la competencia en la práctica diaria?"

Es el tipo de información que un amigo que YA tiene la moto te contaría tomando cerveza, no lo que dice el vendedor o el folleto.

## Tecnología Base

**Motor de IA**: Google Gemini (gemini-3-pro-preview)
- Capacidad de deep research nativa (búsqueda web automática)
- Manejo de contextos largos
- Respeta estructuras de output definidas

**Lenguaje**: Python 3.x
- Framework: Jupyter Notebooks para orquestación
- Módulos especializados bajo `src/`

## Tipo de Información Generada

Los informes se enfocan en experiencias reales de usuarios, NO en especificaciones técnicas:
- Problemas comunes reportados por dueños
- Sensaciones de manejo (estabilidad, vibración, frenado)
- Comparaciones orgánicas con otras motos
- Consumo real de combustible
- Modificaciones populares
- Confiabilidad a largo plazo
- Valor de reventa

## Usos de la Base de Conocimiento

La base de conocimiento es agnóstica al consumidor final:
- Alimentar chatbots o asistentes conversacionales
- Generar contenido editorial (blogs, fichas, comparativas)
- Dashboards de análisis de percepción por marca/modelo/país
- Soporte a decisiones de inventario o pricing
- Cualquier sistema que necesite entender cómo los usuarios viven una moto en un país específico

## Consideraciones Importantes

- Se genera un informe por cada moto **POR PAÍS** (Colombia, México, Chile)
- La misma moto puede tener experiencias diferentes por país
- Los informes complementan la información técnica, no la reemplazan
- El sistema adapta búsquedas según el tipo de moto (urbana, deportiva, adventure, etc.)
- Ficha técnica como "ancla de verdad" para validar experiencias

## Arquitectura Multi-Skills

El sistema implementa una arquitectura modular basada en **skills especializadas**. Cada skill es una capacidad independiente que encapsula lógica, prompts y procesamiento para una tarea específica del pipeline.

### Las 4 Skills Principales

#### 1. ScraperSkill (Recolección)
**Nombre**: `scraper-skill`
**Responsabilidad**: Recolectar experiencias de usuarios sin filtrar ni validar

**Archivos clave**:
- Documentación: `.context/skills/scraper_skill.md`
- Implementación: `src/core/scraper_agent.py`
- Prompt: `src/data/input/prompts/scraper_agent_template.md`
- Procesador base: `src/core/gemini_processor.py`

**Funcionalidad**:
- Busca en foros, YouTube, marketplaces, redes sociales, blogs
- Extrae experiencias etiquetadas (país, tipo de contenido, fecha)
- NO valida ni filtra, solo recolecta y etiqueta
- NO tiene acceso a la ficha técnica

**Output**: JSON con estructura `experiencias_usuarios` (fuente, país identificado, extractos relevantes, menciones de specs)

**Uso**:
```python
from src.core.scraper_agent import ScraperAgent
scraper = ScraperAgent()
resultado = scraper.scrape(marca="Hero", modelo="Hunk 125R", año=2025, pais="Colombia")
```

#### 2. ValidatorSkill (Validación de dos niveles)
**Nombre**: `validator-skill`
**Responsabilidad**: Validar que las experiencias correspondan al modelo/país correcto comparando con ficha técnica

**Archivos clave**:
- Documentación: `.context/skills/validator_skill.md`
- Implementación: `src/core/validator_agent.py`
- Prompts: `src/data/input/prompts/validator_agent_template.md`, `validator_re_research_template.md`
- Formateo de ficha: `src/core/base_knowledge.py`

**Funcionalidad**:
- **Nivel 1 - Validación automática**: Compara menciones de specs con ficha técnica
  - Experiencias que pasan directamente → validadas
  - Experiencias con contradicciones → marcadas para re-research
  - Experiencias claramente incorrectas → excluidas

- **Nivel 2 - Re-research**: Investigación profunda para casos ambiguos
  - Detecta flags: `CONTRADICCION_FRENOS`, `CONTRADICCION_ALIMENTACION`, `PAIS_INCIERTO`, etc.
  - Ejecuta búsqueda específica para aclarar confusión
  - Clasifica: INCLUIR, INCLUIR_CON_NOTA, EXCLUIR, EXCLUIR_POR_PRECAUCION

**Output**:
- `experiencias_validadas`: Lista de experiencias confirmadas (Level 1)
- `experiencias_requieren_re_research`: Lista con flags de contradicción
- `experiencias_excluidas_automatico`: Lista de experiencias rechazadas

**Uso**:
```python
from src.core.validator_agent import ValidatorAgent
validator = ValidatorAgent()

# Level 1: Validación automática
resultado = validator.validate(
    experiencias=experiencias,
    ficha_tecnica=ficha_tecnica,
    marca="Hero", modelo="Hunk 125R", año=2025, pais="Colombia"
)

# Level 2: Re-research para casos con flags
for exp_re in resultado.get("experiencias_requieren_re_research", []):
    resultado_re = validator.re_research(
        experiencia=exp_re.get("experiencia_completa"),
        ficha_tecnica=ficha_tecnica,
        marca="Hero", modelo="Hunk 125R", año=2025, pais="Colombia",
        flag=exp_re.get("flag")
    )
```

#### 3. WriterSkill (Generación de KB)
**Nombre**: `writer-skill`
**Responsabilidad**: Generar la base de conocimiento final usando experiencias validadas

**Archivos clave**:
- Documentación: `.context/skills/writer_skill.md`
- Implementación: `src/core/writer_agent.py`
- Prompt: `src/data/input/prompts/knowledge_base_template.md`
- Formateo de ficha: `src/core/base_knowledge.py`

**Funcionalidad**:
- Combina experiencias validadas + verificadas (del re-research)
- Calcula estadísticas para determinar nivel de generalización apropiado
- Genera instrucciones dinámicas de generalización
- Respeta ficha técnica como "ancla de verdad" (no la contradice)
- Genera contenido experiencial, NO técnico

**Reglas de generalización automática**:
- 1 ejemplo → "Un usuario reporta..."
- 2-3 ejemplos → "Algunos usuarios reportan..."
- 4+ ejemplos → "Usuarios reportan..." / "Es común que..."

**Formato de output**:
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

**Uso**:
```python
from src.core.writer_agent import WriterAgent
writer = WriterAgent()

knowledge_base = writer.write(
    experiencias_validadas=experiencias_validadas,
    experiencias_verificadas=experiencias_verificadas,
    ficha_tecnica=ficha_tecnica,
    marca="Hero", modelo="Hunk 125R", año=2025, pais="Colombia", tipo="Urbana"
)
```

#### 4. QASkill (Control de Calidad)
**Nombre**: `qa-skill`
**Responsabilidad**: Validar calidad de la KB generada antes de publicación

**Archivos clave**:
- Documentación: `.context/skills/qa_skill.md`
- Implementación: `src/core/qa_agent.py`
- Prompt: `src/data/input/prompts/qa_agent_template.md`

**Funcionalidad**:
- Verifica consistencia con ficha técnica (no contradice specs críticos)
- Valida generalizaciones apropiadas basadas en cantidad de evidencia
- Revisa formato correcto según template
- Detecta contradicciones internas
- Verifica que no hay información inventada

**Criterios de validación**:
- ✅ Aprobar: Sin contradicciones críticas, generalizaciones apropiadas, formato correcto
- ❌ Rechazar: Contradice ficha técnica, generaliza inapropiadamente, información inventada

**Output**: JSON con resultado de validación
```json
{
  "validacion_aprobada": true/false,
  "score_calidad": 0-100,
  "problemas_criticos": [...],
  "advertencias": [...],
  "aspectos_correctos": [...],
  "resumen": "..."
}
```

**Uso**:
```python
from src.core.qa_agent import QAAgent
qa = QAAgent()

resultado_qa = qa.validate(
    knowledge_base=knowledge_base,
    ficha_tecnica=ficha_tecnica,
    experiencias_validadas=experiencias_validadas,
    experiencias_verificadas=experiencias_verificadas,
    marca="Hero", modelo="Hunk 125R", año=2025, pais="Colombia"
)

if resultado_qa.get("validacion_aprobada"):
    # Guardar KB
else:
    # Revisar problemas críticos
```

### Flujo de Ejecución Completo

```
┌─────────────┐
│  CSV/Input  │
│  Database   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ ScraperSkill    │ → Recolectar experiencias de internet
│ (sin filtrar)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ValidatorSkill  │
│                 │
│ Level 1:        │ → Validación automática vs ficha técnica
│ - Validadas     │
│ - Re-research   │
│ - Excluidas     │
│                 │
│ Level 2:        │ → Re-research profundo para casos ambiguos
│ - Verificadas   │
│ - Excluidas     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ WriterSkill     │ → Generar KB experiencial con
│                 │   generalizaciones apropiadas
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ QASkill         │ → Control de calidad final
│                 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  KB Final (.md) │ → Base de conocimiento publicable
└─────────────────┘
```

### Independencia de Skills

Cada skill puede usarse:
- **Independientemente**: Para procesar solo una etapa
- **En conjunto**: Siguiendo el flujo completo del pipeline
- **En paralelo**: Múltiples instancias para diferentes modelos

### Componentes Compartidos

**GeminiProcessor** (`src/core/gemini_processor.py`):
- Cliente compartido para interactuar con Gemini API
- Todas las skills lo usan como procesador base
- Configurado con `google_search` tool para deep research

**BaseKnowledge** (`src/core/base_knowledge.py`):
- Formateo de fichas técnicas
- Extracción de campos críticos, importantes para UX y contextuales
- Normalización de datos desde CSV
- Usado por ValidatorSkill, WriterSkill y QASkill

**PromptUtils** (`src/core/prompt_utils.py`):
- Lectura de templates desde archivos .md
- Reemplazo de variables en prompts
- Validación de variables reemplazadas

## Estructura del Proyecto

```
deep_research_models/
├── .context/                          # Documentación del proyecto
│   ├── context.md                     # Este archivo (documentación principal)
│   ├── skills/                        # Documentación de cada skill
│   │   ├── scraper_skill.md
│   │   ├── validator_skill.md
│   │   ├── writer_skill.md
│   │   ├── qa_skill.md
│   │   └── SKILLS_UPDATE_SUMMARY.md
│   ├── chatbot/                       # Docs sobre integración chatbot
│   └── firecrawl/                     # Docs sobre alternativas de scraping
│
├── src/                               # Código fuente
│   ├── config/                        # Configuración
│   │   └── settings.py                # Variables de entorno y config
│   │
│   ├── core/                          # Módulos principales (skills)
│   │   ├── gemini_processor.py        # Cliente de Gemini (shared)
│   │   ├── base_knowledge.py          # Formateo de fichas técnicas (shared)
│   │   ├── prompt_utils.py            # Utilidades de prompts (shared)
│   │   ├── scraper_agent.py           # ScraperSkill
│   │   ├── validator_agent.py         # ValidatorSkill
│   │   ├── writer_agent.py            # WriterSkill
│   │   └── qa_agent.py                # QASkill
│   │
│   ├── sources/                       # Fuentes de datos
│   │   └── inventory/                 # Inventario de motos por país
│   │       └── app.py                 # Loader de base de datos
│   │
│   ├── data/                          # Datos de entrada/salida
│   │   ├── input/
│   │   │   ├── prompts/               # Templates de prompts (.md)
│   │   │   │   ├── scraper_agent_template.md
│   │   │   │   ├── validator_agent_template.md
│   │   │   │   ├── validator_re_research_template.md
│   │   │   │   ├── knowledge_base_template.md
│   │   │   │   ├── qa_agent_template.md
│   │   │   │   └── comparisons_template.md
│   │   │   └── processed_codes/       # Tracking de códigos procesados
│   │   └── output/                    # KBs generadas
│   │
│   └── utils/                         # Utilidades adicionales
│
├── notebooks/                         # Jupyter notebooks para orquestación
│   ├── testing.ipynb                  # Testing del pipeline completo
│   ├── app.ipynb                      # Aplicación principal
│   └── update_knowledge_base.ipynb    # Actualización de KBs existentes
│
├── scripts/                           # Scripts auxiliares
│
├── .env                               # Variables de entorno (NO versionado)
├── .env_example                       # Ejemplo de variables de entorno
├── .gitignore
├── DECISIONS.md                       # Architecture Decision Records (ADR)
├── STATUS.txt                         # Estado actual del proyecto
└── requirements.txt                   # Dependencias Python
```

## Configuración y Setup

### Variables de Entorno

El proyecto requiere configuración en archivo `.env`:

```bash
# Gemini API
GEMINI_API_KEY=your_api_key_here

# País de procesamiento (CO, MX, CL)
COUNTRY=CO

# Rutas de bases de datos
DATABASE_PATH_CO=path/to/colombia_inventory.csv
DATABASE_PATH_MX=path/to/mexico_inventory.csv
DATABASE_PATH_CL=path/to/chile_inventory.csv
```

### Instalación

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows)
venv\Scripts\activate

# Activar entorno (Linux/Mac)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env_example .env
# Editar .env con tus credenciales
```

### Dependencias Principales

- `google-genai`: Cliente oficial de Google Gemini
- `pandas`: Manipulación de datos (CSVs, inventarios)
- `jupyter`: Notebooks para orquestación
- `python-dotenv`: Gestión de variables de entorno

### Ejecución

**Opción 1: Jupyter Notebook (recomendado para testing)**
```bash
jupyter notebook
# Abrir notebooks/testing.ipynb
```

**Opción 2: Script Python (para producción)**
```python
# Ejemplo de uso del pipeline completo
from src.core.scraper_agent import ScraperAgent
from src.core.validator_agent import ValidatorAgent
from src.core.writer_agent import WriterAgent
from src.core.qa_agent import QAAgent
from src.sources.inventory.app import Inventory

# Cargar datos
db_loader = Inventory()
df = db_loader.load_db_from_country_selected()

# Filtrar modelo específico
df_model = df[df["code"] == "CO2961-hero-hunk-125-r"]

# Ejecutar pipeline
scraper = ScraperAgent()
validator = ValidatorAgent()
writer = WriterAgent()
qa = QAAgent()

# 1. Scraping
experiencias = scraper.scrape(marca="Hero", modelo="Hunk 125R", año=2025, pais="Colombia")

# 2. Validación (Level 1 + Level 2)
resultado_val = validator.validate(
    experiencias=experiencias.get("experiencias_usuarios"),
    ficha_tecnica=df_model["technical_specs"].iloc[0],
    marca="Hero", modelo="Hunk 125R", año=2025, pais="Colombia"
)

# Re-research para casos ambiguos
experiencias_verificadas = []
for exp in resultado_val.get("experiencias_requieren_re_research", []):
    resultado_re = validator.re_research(
        experiencia=exp.get("experiencia_completa"),
        ficha_tecnica=df_model["technical_specs"].iloc[0],
        marca="Hero", modelo="Hunk 125R", año=2025, pais="Colombia",
        flag=exp.get("flag")
    )
    if resultado_re.get("resultado") in ["INCLUIR", "INCLUIR_CON_NOTA"]:
        experiencias_verificadas.append(
            validator.update_experience_after_re_research(
                exp.get("experiencia_completa"), resultado_re
            )
        )

# 3. Generación de KB
kb = writer.write(
    experiencias_validadas=resultado_val.get("experiencias_validadas"),
    experiencias_verificadas=experiencias_verificadas,
    ficha_tecnica=df_model["technical_specs"].iloc[0],
    marca="Hero", modelo="Hunk 125R", año=2025, pais="Colombia", tipo="Urbana"
)

# 4. QA
qa_result = qa.validate(
    knowledge_base=kb,
    ficha_tecnica=df_model["technical_specs"].iloc[0],
    experiencias_validadas=resultado_val.get("experiencias_validadas"),
    experiencias_verificadas=experiencias_verificadas,
    marca="Hero", modelo="Hunk 125R", año=2025, pais="Colombia"
)

if qa_result.get("validacion_aprobada"):
    # Guardar KB
    with open(f'CO-Hero_Hunk_125R-knowledge_base.md', 'w', encoding='utf-8') as f:
        f.write(kb)
```

## Formato de Datos

### Input: Ficha Técnica (Technical Specs)

La ficha técnica viene como lista de diccionarios desde el CSV:

```python
[
  {
    "key": "front_brakes",
    "value": "Disco",
    "type": "string",
    "group": "brakes"
  },
  {
    "key": "fuel_system",
    "value": "Carburada",
    "type": "string",
    "group": "performance"
  },
  {
    "key": "displacement",
    "value": 124.7,
    "type": "number",
    "group": "engine"
  }
  // ...
]
```

**Campos críticos** (alto riesgo de error entre versiones):
- `front_brakes`, `rear_brakes`
- `fuel_system`
- `start_system`

**Campos importantes para UX**:
- `total_weight`
- `tank_capacity`
- `efficiency`
- `displacement`

**Campos de contexto**:
- `engine_type`
- `transmission_type`
- `gears`
- `front_suspension`, `rear_suspension`

### Output: Knowledge Base (.md)

Archivo Markdown con estructura definida:

```markdown
[SEGMENTO]
Tipo según BD: Urbana
Segmento identificado por usuarios: Naked Urbana de entrada / Sport económica

[SENTIMIENTO]
Percibida como una "moto grande" en cuerpo de 125cc...

[SENSACIONES]
Estabilidad: ...
Vibraciones: ...
Frenado: ...

[VENTAJAS]
Alta frecuencia (70%+):
- Estética de mayor cilindrada
- Iluminación Full LED

[PROBLEMAS]
Problema 1:
Frecuencia: Alta
Descripción: ...
Contexto: ...
Solución comunitaria: ...

[RENDIMIENTO]
Consumo real reportado: 150-180 km/galón...

[CONFIABILIDAD]
Información disponible: ...

[REVENTA]
Facilidad de venta: ...

[MODIFICACIONES]
- Recarburación (Jetting)
- Estética: fender delete

[PERFIL_USUARIO]
Edad aproximada: 18-30 años...

[OPINIONES_DIVIDIDAS]
Carburador vs Inyección: ...

[LIMITACIONES]
Información escasa: Durabilidad a 50k km...

[COMPARACIONES]
Modelo comparado: TVS Raider 125
Por qué los usuarios los comparan: ...
En qué gana: ...
En qué pierde: ...

[SINTESIS]
Ideal para joven universitario...
No recomendable para quien busca piques...
```

## Decisiones Arquitectónicas Importantes

Ver archivo `DECISIONS.md` para el registro completo de ADRs (Architecture Decision Records).

**Decisiones clave**:

1. **ADR-001**: Usar Gemini en lugar de OpenAI
   - Deep research nativo, mejor manejo de contextos largos

2. **ADR-003**: Output en archivos .md
   - Versionable, human-readable, fácil de consumir por LLMs

3. **ADR-005**: Notebooks solo para orquestación
   - Lógica de negocio en módulos bajo `src/`
   - Notebooks para ejecutar pipeline y explorar resultados

4. **ADR-006**: Prompts en archivos .md externos
   - Fácil de editar sin tocar código
   - Versionable en Git

## Próximas Mejoras

Según `STATUS.txt`:
- [ ] Integración de comparador de motos (top 3 competidores)
- [ ] Prompts específicos por tipo de moto (urbana, deportiva, etc.)
- [ ] Manejo de errores si Gemini falla
- [ ] Sistema de tracking de códigos procesados (en progreso)

## Referencias Adicionales

- **Documentación de skills**: `.context/skills/`
- **Decisiones arquitectónicas**: `DECISIONS.md`
- **Estado del proyecto**: `STATUS.txt`
- **Integración chatbot**: `.context/chatbot/como_funciona_chatbot.txt`
- **Alternativas de scraping**: `.context/firecrawl/`

