# Knowledge Base Generator

Sistema de agente orquestador con skills especializadas usando Claude Code, que automatiza el flujo de investigación, validación y generación de informes experienciales sobre motocicletas.

## Estructura del Proyecto

```
knowledge-base-generator/
│
├── .claude/
│   └── skills/
│       ├── orchestrator/
│       │   └── SKILL.md          # Coordinador principal del flujo
│       ├── scraper/
│       │   ├── SKILL.md          # Recolecta experiencias de usuarios
│       │   └── scripts/
│       │       └── scraper_fetch.py  # Script genérico para scraping
│       ├── validator/
│       │   └── SKILL.md          # Valida experiencias contra ficha técnica
│       ├── writer/
│       │   └── SKILL.md          # Genera Knowledge Base estructurado
│       └── qa/
│           └── SKILL.md          # Valida calidad del KB generado
│
├── inputs/
│   └── base_inventory/
│       └── BaseCO.csv            # Base de datos con fichas técnicas
│
├── outputs/                       # Knowledge Bases generados (organizados por país)
│   ├── Colombia/
│   │   ├── KB/                    # Knowledge Bases por marca
│   │   │   ├── Bajaj/
│   │   │   ├── TVS/
│   │   │   └── ...
│   │   └── estadisticas/           # Metadatos por marca
│   │       ├── Bajaj/
│   │       ├── TVS/
│   │       └── ...
│   └── ...
│
├── docs/
│   └── project_context.md        # Contexto del proyecto
│
├── requirements.txt               # Dependencias Python
└── README.md
```

## Instalación

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
GEMINI_API_KEY=tu_api_key_de_gemini_aqui
```

**Nota**: El script `scraper_fetch.py` usa `python-dotenv` para cargar estas variables automáticamente.

## Cómo Ejecutar

### Opción 1: Ejecutar desde Claude Code (Recomendado)

1. **Abrir Claude Code** en esta carpeta del proyecto
2. **Iniciar conversación** con Claude Code
3. **Ejecutar el Orchestrator** con un prompt como:

```
Ejecuta el Orchestrator para generar un Knowledge Base con estos parámetros:
- marca: Victory
- modelo: MRX 125 F TK
- año: 2027
- pais: Colombia
- tipo: Todo Terreno
```

Claude Code leerá automáticamente el `SKILL.md` del Orchestrator y ejecutará el flujo completo.

### Opción 2: Ejecutar Skills Individuales

Si quieres probar una skill específica:

```
Ejecuta la skill Scraper con estos parámetros:
- marca: Victory
- modelo: MRX 125 F TK
- año: 2027
- pais: Colombia
- tipo: Todo Terreno
```

## Flujo del Sistema

```
Orchestrator (inicia el proceso)
    ↓
1. Carga ficha técnica desde BaseCO.csv
    ↓
2. Scraper → Recolecta experiencias usando Gemini/Firecrawl/Tavily
    ↓
3. Validator → Valida experiencias contra ficha técnica
    ↓ (si requiere re-research)
   Orchestrator → Retry Scraper con contexto de fallos
    ↓ (si aprueba)
4. Writer → Genera Knowledge Base estructurado
    ↓
5. QA → Valida calidad del KB
    ↓
6. Orchestrator → Guarda resultado en outputs/
```

## Skills Disponibles

### Orchestrator
- Coordina todo el flujo
- Maneja retries y decisiones
- Carga ficha técnica desde CSV
- Guarda resultados finales

### Scraper
- Recolecta experiencias vivenciales de usuarios
- Usa script genérico (Gemini/Firecrawl/Tavily)
- Retorna JSON estructurado

### Validator
- Valida experiencias contra ficha técnica
- Marca contradicciones para re-research
- Retorna experiencias validadas

### Writer
- Genera Knowledge Base en texto plano
- Usa formato estricto con secciones definidas
- Aplica generalizaciones según evidencia

### QA
- Valida calidad del KB generado
- Verifica consistencia con ficha técnica
- Calcula score de calidad (0-100)

## Dependencias

- `google-genai`: Para usar Gemini API (scraper)
- `python-dotenv`: Para cargar variables de entorno
- `pandas`: Para leer y procesar CSV de fichas técnicas

## Notas Importantes

1. **Ficha Técnica**: El Orchestrator busca automáticamente en `inputs/base_inventory/BaseCO.csv` usando marca, modelo y año. El archivo se puede conseguir ejecutando el proyecto de historical_data

2. **Scraper Genérico**: El script `scraper_fetch.py` puede usar diferentes proveedores. Actualmente configurado para Gemini, pero puede adaptarse a Firecrawl, Tavily, etc.

3. **Variables de Entorno**: Asegúrate de tener `GEMINI_API_KEY` en tu archivo `.env`.

4. **Outputs**: Los Knowledge Bases generados se guardan en `outputs/{pais}/KB/{marca}/` organizados por país y marca, con formato: `{marca}_{modelo}_{año}_{pais}_KB.txt`. Los metadatos se guardan en `outputs/{pais}/estadisticas/{marca}/` con formato: `{marca}_{modelo}_{año}_{pais}_META.json`

## Troubleshooting

### Error: "No module named 'google.genai'"
- Ejecuta: `pip install -r requirements.txt`

### Error: "GEMINI_API_KEY not found"
- Verifica que tengas un archivo `.env` con la variable `GEMINI_API_KEY`

### Error: "Ficha técnica no encontrada"
- Verifica que el CSV `inputs/base_inventory/BaseCO.csv` tenga la combinación marca/modelo/año que buscas
