from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

# Países soportados (única fuente de verdad)
SUPPORTED_COUNTRIES = ("CO", "MX", "CL")
COUNTRY_NAMES = {"CO": "Colombia", "MX": "Mexico", "CL": "Chile"}

# Configuración inicial (overrideable vía .env)
COUNTRY = os.getenv("COUNTRY", "MX")

# Gemini settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-pro-preview")

# Directorio de la aplicación
CURRENT_FILE = Path(__file__).resolve()
SRC_DIR = CURRENT_FILE.parents[1]

# Prompts y salida
PROMPT_TEMPLATE_PATH = SRC_DIR / "data" / "input" / "prompts" / "direct_research_template.md"
KB_OUTPUT_DIR = SRC_DIR / "data" / "output" / "KB"
