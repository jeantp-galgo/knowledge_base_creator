# Deep Research Models - Knowledge Base Generator

## Descripcion del Proyecto

Sistema automatizado para generar bases de conocimiento experienciales sobre motocicletas usando inteligencia artificial. Estas bases de conocimiento son activos de datos independientes disenados para ser consumidos por multiples sistemas (chatbots, dashboards, generacion de contenido, analisis comparativo, etc.).

## Objetivo Principal

Capturar la experiencia real y emocional de poseer y usar una motocicleta, NO las especificaciones tecnicas de manuales.

El sistema responde preguntas como:
- "Realmente vale la pena?"
- "Que me va a molestar despues de 6 meses de uso?"
- "Me va a dejar tirado?"
- "Es mejor que la competencia en la practica diaria?"

Es el tipo de informacion que un amigo que YA tiene la moto te contaria tomando cafe, no lo que dice el vendedor o el folleto.

## Tecnologia Base

**Motor de IA**: Google Gemini (`gemini-3-pro-preview`)
- Capacidad de deep research nativa (busqueda web automatica via `google_search` tool)
- Manejo de contextos largos
- Respeta estructuras de output definidas

**Lenguaje**: Python 3.x
- Notebooks Jupyter para orquestacion (en `notebooks/`)
- Modulos especializados bajo `src/`

## Tipo de Informacion Generada

Los informes se enfocan en experiencias reales de usuarios, NO en especificaciones tecnicas:
- Problemas comunes reportados por duenos
- Sensaciones de manejo (estabilidad, vibracion, frenado)
- Comparaciones organicas con otras motos
- Consumo real de combustible
- Modificaciones populares
- Confiabilidad a largo plazo
- Valor de reventa

## Usos de la Base de Conocimiento

La base de conocimiento es agnostica al consumidor final:
- Alimentar chatbots o asistentes conversacionales
- Generar contenido editorial (blogs, fichas, comparativas)
- Dashboards de analisis de percepcion por marca/modelo/pais
- Soporte a decisiones de inventario o pricing
- Cualquier sistema que necesite entender como los usuarios viven una moto en un pais especifico

## Consideraciones Importantes

- Se genera un informe por cada moto **POR PAIS** (Colombia, Mexico, Chile)
- La misma moto puede tener experiencias diferentes por pais
- Los informes complementan la informacion tecnica, no la reemplazan
- El sistema adapta busquedas segun el tipo de moto (urbana, deportiva, adventure, etc.)
- La ficha tecnica es el "ancla de verdad" para validar experiencias

---

## Arquitectura Multi-Skills

El sistema implementa una arquitectura modular basada en **skills especializadas**. Cada skill es una capacidad independiente que encapsula logica, prompts y procesamiento para una tarea especifica del pipeline.

```
CSV Inventario -> ScraperAgent -> ValidatorAgent (L1 + L2) -> WriterAgent -> QAAgent -> KB (.md)
                                                                          |
                                                         models_data_recollected/*.json (cache intermedio)
```

### Las 4 Skills Principales

---

#### 1. ScraperAgent (`src/core/scraper_agent.py`)

**Responsabilidad**: Recolectar experiencias de usuarios de internet sin filtrar ni validar.

**Inicializacion**:
```python
scraper = ScraperAgent(brand="Hero", model="Hunk 125 R", year="2025", country="Colombia")
```

**Metodo principal**: `scrape() -> Dict`

**Funcionamiento**:
1. Lee el template de prompt desde `SCRAPER_AGENT_TEMPLATE_PATH`
2. Reemplaza variables `{MARCA}`, `{MODELO}`, `{AÑO}`, `{PAIS}`
3. Valida que no queden variables sin reemplazar (`validate_prompt_variables`)
4. Envia el prompt a Gemini via `GeminiProcessor.send_prompt()` (con `google_search` habilitado)
5. Parsea la respuesta como JSON (con fallbacks multiples: `json`, ` ```json `, busqueda de primer `{`)

**Busca en**: foros de motociclistas, YouTube (reviews del pais), Facebook/redes sociales, blogs, marketplaces con opiniones.

**Output JSON**:
```json
{
  "experiencias_usuarios": [
    {
      "fuente": "https://...",
      "pais_identificado": "Colombia",
      "tipo_contenido": "review_propietario",
      "fecha_aprox": "2024",
      "extractos_relevantes": [
        { "categoria": "problemas", "texto": "..." },
        { "categoria": "sensaciones_frenado", "texto": "..." }
      ],
      "menciones_specs_tecnicas": [
        { "spec": "sistema_frenos", "mencion": "CBS", "coincide_ficha": true }
      ]
    }
  ]
}
```

**Categorias de extractos**: `sensaciones_frenado`, `problemas`, `consumo`, `comodidad`, `confiabilidad`, `reventa`, `comparaciones`, `modificaciones`, `otro`.

**Reglas**: NO valida, NO filtra. Solo recolecta y etiqueta. NO tiene acceso a la ficha tecnica en esta etapa.

---

#### 2. ValidatorAgent (`src/core/validator_agent.py`)

**Responsabilidad**: Validar que las experiencias correspondan al modelo/pais correcto comparando contra la ficha tecnica.

**Inicializacion**:
```python
validator = ValidatorAgent(
    brand="Hero", model="Hunk 125 R", year="2025",
    experiencias=[...],          # lista de experiencias del Scraper
    ficha_tecnica=TECHNICAL_SPECS,  # string, lista o dict
    country="Colombia"
)
```

**Metodos principales**:

- `validate() -> Dict` -- Nivel 1: Validacion automatica
- `re_research(experiencia, ficha_tecnica, flag) -> Dict` -- Nivel 2: Re-investigacion profunda
- `update_experience_after_re_research(experiencia_original, resultado_re) -> Dict` -- Actualiza experiencia con veredicto del re-research
- `get_prompt_template() -> str` -- Retorna el prompt listo para inspeccion

**Nivel 1 - Validacion automatica**:

Compara cada experiencia contra la ficha tecnica. Clasifica en:

| Categoria | Criterio |
|---|---|
| `experiencias_validadas` | Pais confirmado + specs coinciden (confidence >= 90%) |
| `experiencias_requieren_re_research` | Existe contradiccion o ambiguedad, se agrega `flag` |
| `experiencias_excluidas_automatico` | Claramente de otro modelo/pais/version (confidence >= 90%) |

**Flags de contradiccion**:
- `CONTRADICCION_FRENOS` -- Menciona ABS cuando la ficha dice CBS, o viceversa
- `CONTRADICCION_ALIMENTACION` -- Menciona carburador cuando ficha dice inyeccion
- `CONTRADICCION_CILINDRAJE` -- Cilindrada mencionada no coincide con ficha
- `PAIS_INCIERTO` -- No se puede determinar si la fuente es del pais correcto
- `POSIBLE_VERSION_ANTERIOR` -- Podria ser de un modelo de anio anterior
- `ESPECIFICACION_AMBIGUA` -- La mencion es poco clara

**Nivel 2 - Re-research**:

Para cada experiencia con flag, ejecuta busqueda especifica con Gemini para aclarar la contradiccion. Veredictos posibles:

| Resultado | Significado | Accion |
|---|---|---|
| `INCLUIR` | Contradiccion aclarada, experiencia valida | Se agrega a `experiencias_verificadas` |
| `INCLUIR_CON_NOTA` | Valida pero de version diferente | Se agrega con nota aclaratoria |
| `EXCLUIR` | Confirmado de otro modelo/pais | Se descarta |
| `EXCLUIR_POR_PRECAUCION` | No se pudo verificar | Se descarta por seguridad |

**Formato interno ficha tecnica** (acepta `dict`, `str` o `List[Dict]`):
```
Marca: Hero
Modelo: Hunk 125 R
Ano: 2025
Pais: Colombia

Especificaciones Tecnicas:
CAMPOS CRITICOS:
- Freno delantero: Disco
- Freno trasero: Tambor
- Sistema de alimentacion: Carburada
- Sistema de arranque: Electrico y pedal

IMPORTANTES PARA EXPERIENCIA DE USUARIO:
- Peso total: 138 kg
- Capacidad del tanque: 10 litros
- Rendimiento de combustible: 45 km/l
- Cilindrada: 124.7 cc

UTILES COMO CONTEXTO:
- Tipo de motor: Monocilindrico
- Tipo de transmision: Manual
- Numero de cambios: 5 velocidades
- Suspension delantera: Horquilla telescopica
- Suspension trasera: Mono amortiguador
```

---

#### 3. WriterAgent (`src/core/writer_agent.py`)

**Responsabilidad**: Generar la base de conocimiento final usando experiencias validadas.

**Inicializacion**:
```python
writer = WriterAgent(
    brand="Hero", model="Hunk 125 R", year="2025",
    tipo="Urbana",
    ficha_tecnica=TECHNICAL_SPECS,
    experiencias_validadas=[...],    # Nivel 1
    experiencias_verificadas=[...],  # Nivel 2
    country="Colombia",
    processor=None  # Opcional: reutilizar instancia de GeminiProcessor
)
```

**Metodo principal**: `write() -> str`

**Funcionamiento**:
1. Lee template desde `KNOWLEDGE_BASE_TEMPLATE_PATH`
2. Reemplaza variables basicas del template: `{MARCA}`, `{MODELO}`, `{AÑO}`, `{PAIS}`, `{TIPO}`, `{FICHA TECNICA}`
3. Combina `experiencias_validadas + experiencias_verificadas` en una lista total
4. Calcula estadisticas por categoria de extractos (metodo `_calcular_estadisticas`)
5. Genera instrucciones dinamicas de generalizacion (metodo `_generar_instrucciones_generalizaciones`)
6. Agrega al final del prompt: experiencias en JSON, estadisticas y restricciones de generalizacion
7. Valida variables sin reemplazar y envia a Gemini
8. Retorna el texto del KB directamente (sin parsear como JSON -- es texto libre estructurado)

**Reglas de generalizacion automatica** (basadas en conteo de evidencia):
- 1 ejemplo: "Un usuario reporta..." o "Se ha documentado un caso de..."
- 2-3 ejemplos: "Algunos usuarios reportan..." o "Hay reportes de..."
- 4+ ejemplos: "Los usuarios reportan..." o "Es comun que..."

**Restricciones al Writer**:
- NUNCA contradice la ficha tecnica en specs criticos
- NO repite specs como contenido ("tiene frenos CBS" no es contenido vivencial)
- SI permite percepciones que contrastan con specs ("se siente mas potente de lo que indica la ficha")
- SI permite comparaciones con equipamiento diferente ("comparado con motos con ABS...")
- Declara explicitamente cuando la informacion es insuficiente, NO inventa

**Output**: String en formato de 14 secciones (ver formato KB mas abajo).

---

#### 4. QAAgent (`src/core/qa_agent.py`)

**Responsabilidad**: Validar la calidad de la KB generada antes de publicar.

**Inicializacion**:
```python
qa = QAAgent(processor=None)  # Opcional: reutilizar GeminiProcessor
```

**Metodo principal**: `validate(knowledge_base, ficha_tecnica, experiencias_validadas, experiencias_verificadas, marca, modelo, ano, pais) -> Dict`

**Funcionamiento**:
1. Lee template desde `QA_AGENT_TEMPLATE_PATH`
2. Reemplaza variables: `{MARCA}`, `{MODELO}`, `{AÑO}`, `{PAIS}`, `{FICHA_TECNICA}`, `{KNOWLEDGE_BASE}`, `{EXPERIENCIAS}`, `{ESTADISTICAS}`
3. Calcula estadisticas de evidencia (mismo metodo que WriterAgent)
4. Envia a Gemini y parsea respuesta como JSON

**Dimensiones de validacion**:
1. Consistencia con ficha tecnica (sin contradicciones en specs criticos)
2. Generalizaciones apropiadas (lenguaje proporcional a evidencia)
3. Formato correcto (14 secciones, sin markdown, headers correctos)
4. Consistencia interna (sin contradicciones entre secciones)
5. Contenido respaldado por evidencia (nada inventado)
6. Uso correcto de la ficha como ancla (no como fuente de contenido)

**Output JSON**:
```json
{
  "validacion_aprobada": true,
  "score_calidad": 87,
  "problemas_criticos": [],
  "advertencias": ["..."],
  "aspectos_correctos": ["..."],
  "resumen": "..."
}
```

**Criterios de aprobacion**:
- `validacion_aprobada: true` con `score_calidad >= 80`
- Sin `problemas_criticos`

---

### Flujo de Ejecucion Completo

```
[CSV Inventario]
       |
       v
[Inventory.load_db_from_country_selected()]
       |
       v Fila del DataFrame (brand, model, year, type, technical_specs)
       |
       v
[1. ScraperAgent.scrape()]
       |
       v {"experiencias_usuarios": [...]}
       |
       v
[2. ValidatorAgent.validate()]  <-- Nivel 1
       |
       +-> experiencias_validadas
       +-> experiencias_excluidas_automatico
       +-> experiencias_requieren_re_research (con flag)
                |
                v
       [ValidatorAgent.re_research()] x N  <-- Nivel 2 (uno por cada flaggeada)
                |
                v
       experiencias_verificadas (INCLUIR / INCLUIR_CON_NOTA)
       experiencias_excluidas (EXCLUIR / EXCLUIR_POR_PRECAUCION)
       |
       v Guardado intermedio en models_data_recollected/*.json
       |
       v
[3. WriterAgent.write()]
       |
       v texto KB en formato 14 secciones
       |
       v
[4. QAAgent.validate()]
       |
       +-> validacion_aprobada: true  --> Guardar como src/data/output/gemini/{PAIS}-{MARCA}_{MODELO}-knowledge_base.md
       +-> validacion_aprobada: false --> Revisar problemas_criticos y regenerar
```

---

### Componentes Compartidos

**GeminiProcessor** (`src/core/gemini_processor.py`):
- Cliente centralizado para la API de Google Gemini
- Modelo: `gemini-3-pro-preview`
- Usa `google_search` tool para habilitar deep research nativo
- Todas las skills lo usan como procesador base
- `send_prompt(prompt: str) -> str`: envia prompt y concatena todos los outputs de texto

**BaseKnowledge** (`src/core/base_knowledge.py`):
- `format_technical_specs(technical_specs) -> str`: filtra y formatea specs relevantes para los prompts
  - Acepta `list`, `str` (JSON o Python literal) o `None`
  - Agrupa en: CAMPOS CRITICOS, IMPORTANTES PARA EXPERIENCIA DE USUARIO, UTILES COMO CONTEXTO
  - Agrega unidades (cc, kg, litros, km/l, velocidades)
  - Traduce keys tecnicos a espanol legible
- `get_basic_data_model(df, country) -> dict`: extrae y normaliza datos de una fila del DataFrame

**PromptUtils** (`src/core/prompt_utils.py`):
- `read_prompt_from_file(file_path) -> str`: lee template .md desde disco
- `replace_variables(prompt, variables: dict) -> str`: reemplaza `{VARIABLE}` en el prompt
- `validate_prompt_variables(prompt) -> dict`: detecta variables sin reemplazar usando regex `\{[A-Za-z...]+\}`
  - Variables esperadas (no se reportan como faltantes): `{MARCA}`, `{MODELO}`, `{AÑO}`, `{PAIS}`, `{TIPO}`, `{FICHA TECNICA}`
  - Cualquier otra variable encontrada se reporta como potencialmente sin reemplazar

**ProcessCodes** (`src/utils/process_codes.py`):
- `load_processed_codes(filepath) -> Set[str]`: carga codigos ya procesados desde `.txt`
- `save_processed_codes(filepath, codes) -> None`: agrega nuevos codigos al archivo de tracking
- Ruta: `src/data/input/processed_codes/{filepath}.txt`

---

## Estructura del Proyecto

```
deep_research_models/
|
+-- .context/                              # Documentacion del proyecto
|   +-- context.md                         # Este archivo
|   +-- refactor_documentation.md          # Doc del refactor multi-agente original
|   +-- gemini_deep_research.md            # Notas sobre Gemini
|   +-- firecrawl/                         # Alternativas de scraping (no implementado)
|
+-- .claude/                               # Configuracion de Claude Code
|   +-- agents/
|       +-- prompt-engineer.md             # Agente especializado en prompts
|
+-- .cursor/                               # Skills para Cursor
|   +-- skills/
|       +-- scraper.md, validator.md, writer.md, qa.md
|
+-- src/                                   # Codigo fuente principal
|   +-- config/
|   |   +-- settings.py                   # Variables de entorno, rutas, configuracion
|   |
|   +-- core/                             # Modulos de las 4 skills
|   |   +-- gemini_processor.py           # Cliente Gemini (compartido)
|   |   +-- base_knowledge.py             # Formateo de fichas tecnicas (compartido)
|   |   +-- prompt_utils.py               # Utilidades de prompts (compartido)
|   |   +-- scraper_agent.py              # ScraperAgent
|   |   +-- validator_agent.py            # ValidatorAgent
|   |   +-- writer_agent.py               # WriterAgent
|   |   +-- qa_agent.py                   # QAAgent
|   |   +-- base_comparator.py            # Comparador (en desarrollo, no funcional)
|   |
|   +-- sources/
|   |   +-- inventory/
|   |       +-- app.py                    # Inventory: carga CSV por pais
|   |       +-- utils.py                  # transform_database (no usado actualmente, ver ADR-007)
|   |   +-- amplitude/
|   |       +-- app.py                    # Carga eventos de Amplitude (no activo)
|   |       +-- utils.py
|   |
|   +-- utils/
|   |   +-- process_codes.py             # Tracking de codigos procesados
|   |   +-- datetime_utils.py
|   |
|   +-- data/
|       +-- input/
|       |   +-- prompts/                  # Templates de prompts en Markdown
|       |   |   +-- scraper_agent_template.md
|       |   |   +-- validator_agent_template.md
|       |   |   +-- validator_re_research_template.md
|       |   |   +-- knowledge_base_template.md
|       |   |   +-- qa_agent_template.md
|       |   |   +-- comparisons_template.md
|       |   |   +-- backup/               # Backups de versiones anteriores de prompts
|       |   +-- processed_codes/          # Tracking de codigos ya procesados
|       |       +-- processed_codes_co.txt
|       +-- models_data_recollected/      # Cache intermedio (JSON scraping + validacion)
|       |   +-- CO-Hero_Hunk 125 R.json
|       |   +-- CO-Bajaj_Pulsar N 125 FI.json
|       +-- output/
|           +-- gemini/                   # KBs generadas
|           |   +-- CO-Hero_Hunk 125 R-knowledge_base.md
|           |   +-- CO-Bajaj_Pulsar N 125 FI-knowledge_base.md
|           |   +-- test/                 # KBs de prueba (formato fecha-code-pais.md)
|           +-- logs/
|               +-- knowledge_base_update_log.txt
|
+-- notebooks/                            # Orquestacion del pipeline
|   +-- testing.ipynb                     # Pipeline completo de prueba (notebook principal)
|   +-- app.ipynb                         # Pipeline de produccion
|   +-- update_knowledge_base.ipynb       # Actualizacion de KBs existentes
|
+-- trash/                                # Archivos de trabajo descartados o anteriores
|
+-- venv/                                 # Entorno virtual Python (no versionado)
+-- .env                                  # Variables de entorno (NO versionado)
+-- .env_example                          # Ejemplo de .env
+-- .gitignore
+-- PRD.md                                # Product Requirements Document completo
+-- DECISIONS.md                          # Architecture Decision Records (ADR)
+-- requirements.txt                      # Dependencias Python
```

---

## Configuracion y Setup

### Variables de Entorno (`.env`)

```bash
GEMINI_API_KEY=your_api_key_here

# MongoDB (para integraciones futuras)
DB_USERNAME=...
DB_PASSWORD=...

# Otros
STORE_ID=...
```

### Configuracion en `settings.py`

```python
# Pais activo (cambiar segun que inventario se quiere procesar)
COUNTRY = "CO"  # "MX" | "CL" | "CO"

# Rutas absolutas a los CSVs de inventario (propias de cada maquina)
CO_INVENTORY_PATH = r"C:\...\BaseCO.csv"
MX_INVENTORY_PATH = r"C:\...\BaseMX.csv"
CL_INVENTORY_PATH = r"C:\...\BaseCL.csv"

# Rutas de prompts (relativas desde notebooks/)
SCRAPER_AGENT_TEMPLATE_PATH = "../src/data/input/prompts/scraper_agent_template.md"
VALIDATOR_AGENT_TEMPLATE_PATH = "../src/data/input/prompts/validator_agent_template.md"
VALIDATOR_RE_RESEARCH_TEMPLATE_PATH = "../src/data/input/prompts/validator_re_research_template.md"
KNOWLEDGE_BASE_TEMPLATE_PATH = "../src/data/input/prompts/knowledge_base_template.md"
QA_AGENT_TEMPLATE_PATH = "../src/data/input/prompts/qa_agent_template.md"
COMPARISONS_TEMPLATE_PATH = "../src/data/input/prompts/comparisons_template.md"
```

**Nota importante**: Las rutas de prompts son relativas desde el directorio donde se ejecuta el codigo. Si se ejecuta desde `notebooks/`, las rutas `../src/...` funcionan correctamente.

### Instalacion

```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt

cp .env_example .env
# Editar .env con tus credenciales de Gemini
```

### Dependencias Principales

- `google-genai`: Cliente oficial de Google Gemini
- `pandas`: Manipulacion de datos (CSVs, DataFrames)
- `jupyter`: Notebooks para orquestacion
- `python-dotenv`: Gestion de variables de entorno

---

## Formato de Datos

### Input: Ficha Tecnica desde CSV

La columna `technical_specs` del CSV viene como lista de diccionarios (a veces como string que requiere `ast.literal_eval` o `json.loads`):

```python
[
  {"key": "front_brakes",  "value": "Disco",    "type": "string", "group": "brakes"},
  {"key": "rear_brakes",   "value": "Tambor",   "type": "string", "group": "brakes"},
  {"key": "fuel_system",   "value": "Carburada","type": "string", "group": "performance"},
  {"key": "start_system",  "value": "Electrico","type": "string", "group": "performance"},
  {"key": "displacement",  "value": 124.7,      "type": "number", "group": "engine"},
  {"key": "total_weight",  "value": 138,        "type": "number", "group": "dimensions"},
  {"key": "tank_capacity", "value": 10,         "type": "number", "group": "dimensions"},
  {"key": "efficiency",    "value": 45,         "type": "number", "group": "performance"},
  {"key": "engine_type",   "value": "Monocilindrico", "type": "string", "group": "engine"},
  {"key": "gears",         "value": 5,          "type": "number", "group": "transmission"}
]
```

**Campos criticos** (tolerancia cero para contradicciones):
- `front_brakes`, `rear_brakes`
- `fuel_system`
- `start_system`

**Campos importantes UX**:
- `total_weight`, `tank_capacity`, `efficiency`, `displacement`

**Campos de contexto**:
- `engine_type`, `transmission_type`, `gears`, `front_suspension`, `rear_suspension`

### Output: Knowledge Base (.md)

Archivo de texto plano (sin markdown, sin negritas) con 14 secciones:

```
[SEGMENTO]
Tipo segun BD: Urbana
Segmento identificado por usuarios: ...

[SENTIMIENTO]
...

[SENSACIONES]
Estabilidad: ...
Vibraciones: ...
Frenado: ...
...

[VENTAJAS]
Muy mencionado (mayoria de usuarios):
- ...

[PROBLEMAS]
Nombre del problema: ...
Frecuencia: Alta | Media | Baja
Descripcion: ...
Contexto: ...
Solucion comunitaria: ...

[CAUSA_EFECTO]
Causa: ...
Efecto: ...

[RENDIMIENTO]
Consumo real reportado: ...

[CONFIABILIDAD]
Informacion disponible: ...

[REVENTA]
Facilidad de venta: ...

[MODIFICACIONES]
- ...

[PERFIL_USUARIO]
Edad aproximada: ...

[OPINIONES_DIVIDIDAS]
Tema: ...
Posicion A: ...
Posicion B: ...

[LIMITACIONES]
Informacion escasa: ...

[COMPARACIONES]
Modelo comparado: ...
Por que los usuarios los comparan: ...
En que gana: ...
En que pierde: ...

[SINTESIS]
...
```

### Cache Intermedio: models_data_recollected/*.json

Se guarda el resultado del Scraping + Validacion para no repetir esas etapas si solo se necesita regenerar la KB:

```json
{
  "experiencias_validadas": [...],
  "experiencias_verificadas_incluir": [...],
  "experiencias_excluidas": [...]
}
```

Nombre de archivo: `{PAIS_CODE}-{BRAND}_{MODEL}.json` (ej: `CO-Hero_Hunk 125 R.json`)

---

## Ejecucion: Flujo en el Notebook

El archivo principal es `notebooks/testing.ipynb`. Sigue esta secuencia de celdas:

```python
# 1. Setup y carga de inventario
import sys; sys.path.append('../')
from src.core.scraper_agent import ScraperAgent
from src.core.validator_agent import ValidatorAgent
from src.core.writer_agent import WriterAgent
from src.sources.inventory.app import Inventory
from src.config.settings import COUNTRY

db_loader = Inventory()
df = db_loader.load_db_from_country_selected()

# 2. Seleccionar modelo
df_model = df[df["code"] == "CO2961-hero-hunk-125-r"]
BRAND = df_model["brand"].iloc[0]
MODEL = df_model["model"].iloc[0]
YEAR = "2025"
TYPE = df_model["type"].iloc[0]
COUNTRY_NAME = {"CO": "Colombia", "MX": "Mexico", "CL": "Chile"}[COUNTRY]
TECHNICAL_SPECS = df_model["technical_specs"].iloc[0]

# 3. FASE 1: Scraping
scraper = ScraperAgent(brand=BRAND, model=MODEL, year=YEAR, country=COUNTRY_NAME)
experiencias_extraidas = scraper.scrape()

# 4. FASE 2: Validacion Nivel 1
validator = ValidatorAgent(
    brand=BRAND, model=MODEL, year=YEAR,
    experiencias=experiencias_extraidas.get("experiencias_usuarios"),
    ficha_tecnica=TECHNICAL_SPECS,
    country=COUNTRY_NAME
)
resultado_validacion = validator.validate()

# 5. FASE 2: Validacion Nivel 2 (Re-research)
experiencias_verificadas = []
experiencias_excluidas = []
for exp_re in resultado_validacion.get("experiencias_requieren_re_research", []):
    resultado_re = validator.re_research(
        experiencia=exp_re.get("experiencia_completa", {}),
        ficha_tecnica=TECHNICAL_SPECS,
        flag=exp_re.get("flag")
    )
    experiencia_actualizada = validator.update_experience_after_re_research(
        experiencia_original=exp_re.get("experiencia_completa", {}),
        resultado_re_research=resultado_re
    )
    if resultado_re.get("resultado") in ["INCLUIR", "INCLUIR_CON_NOTA"]:
        experiencias_verificadas.append(experiencia_actualizada)
    else:
        experiencias_excluidas.append(experiencia_actualizada)

# 6. Guardar cache intermedio
experiencias_finales = {
    "experiencias_validadas": resultado_validacion.get("experiencias_validadas", []),
    "experiencias_verificadas_incluir": experiencias_verificadas,
    "experiencias_excluidas": resultado_validacion.get("experiencias_excluidas_automatico", []) + experiencias_excluidas
}
with open(f'../src/data/models_data_recollected/{COUNTRY}-{BRAND}_{MODEL}.json', 'w') as f:
    json.dump(experiencias_finales, f, ensure_ascii=False, indent=2)

# 7. FASE 3: Generacion de KB
experiencias_validadas = experiencias_finales["experiencias_validadas"]
experiencias_verificadas = experiencias_finales["experiencias_verificadas_incluir"]

writer = WriterAgent(
    brand=BRAND, model=MODEL, year=YEAR, tipo=TYPE,
    ficha_tecnica=TECHNICAL_SPECS,
    experiencias_validadas=experiencias_validadas,
    experiencias_verificadas=experiencias_verificadas,
    country=COUNTRY_NAME
)
knowledge_base = writer.write()

# 8. Guardar KB
with open(f'../src/data/output/gemini/{COUNTRY}-{BRAND}_{MODEL}-knowledge_base.md', 'w') as f:
    f.write(knowledge_base)

# 9. FASE 4: QA (pendiente de integrar en el notebook principal)
# from src.core.qa_agent import QAAgent
# qa = QAAgent()
# resultado_qa = qa.validate(knowledge_base, TECHNICAL_SPECS, experiencias_validadas, experiencias_verificadas, BRAND, MODEL, YEAR, COUNTRY_NAME)
```

---

## Decisiones Arquitectonicas (ADR)

Ver `DECISIONS.md` para el registro completo. Resumen:

| ADR | Titulo | Estado |
|-----|--------|--------|
| ADR-001 | Usar Gemini en lugar de OpenAI | Activo |
| ADR-002 | Usar datos del comparador de Galgo para competidores | Por implementar |
| ADR-003 | Output en archivos .md | Activo |
| ADR-004 | Descargar eventos raw de Amplitude | No activo |
| ADR-005 | Notebooks solo para orquestacion, logica en modulos | Activo |
| ADR-006 | Prompts en archivos .md externos con variables | Activo |
| ADR-007 | Eliminar transformacion de datos de la base | Activo |

---

## Estado Actual y Proximas Mejoras

### Implementado y funcional
- ScraperAgent: operativo
- ValidatorAgent (Nivel 1 + Nivel 2): operativo
- WriterAgent: operativo
- QAAgent: implementado pero no integrado en notebook principal
- Inventory loader: operativo
- ProcessCodes (tracking de codigos): implementado

### Pendiente / En desarrollo
- Integracion de QAAgent en el notebook de produccion
- BaseComparator (identificar top 3 competidores desde datos de Amplitude): en esqueleto
- Prompts especificos por tipo de moto (Urbana, Deportiva, Adventure)
- Manejo de errores y reintentos ante fallos de Gemini API
- Notebook de batch processing para multiples modelos en secuencia

---

## Referencias

- **PRD completo**: `PRD.md`
- **Decisiones arquitectonicas**: `DECISIONS.md`
- **Notas sobre Gemini Deep Research**: `.context/gemini_deep_research.md`
- **Alternativas de scraping**: `.context/firecrawl/`
- **Skills Cursor**: `.cursor/skills/`
