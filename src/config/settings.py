from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

# Configuración inicial
COUNTRY = "CO" # "MX", "CL", "CO"

# Gemini settings
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
STORE_ID = os.getenv('STORE_ID')
KNOWLEDGE_BASE_STORE_FILENAME = "base_conocimiento_chatbot.md"
LAST_DOCUMENT_UPLOADED = "baseconocimientochatbotmd-0f1cpkw8a81j"

# Directorio de la aplicación
CURRENT_FILE = Path(__file__).resolve()
SRC_DIR = CURRENT_FILE.parents[1]

# MongoDB
MONGO_SETTINGS = {
    "DB_USERNAME": os.getenv("DB_USERNAME"),
    "DB_PASSWORD": os.getenv("DB_PASSWORD"),
}

# Base de inventario de cada país
CO_INVENTORY_PATH = r"C:\Users\JTRUJILLO\Documents\Galgo\Scripts\Data\historical_data\history\CO\BaseCOv2.csv"
MX_INVENTORY_PATH = r"C:\Users\JTRUJILLO\Documents\Galgo\Scripts\Data\historical_data\history\MX\BaseMXv5.csv"
CL_INVENTORY_PATH = r"C:\Users\JTRUJILLO\Documents\Galgo\Scripts\Data\historical_data\history\CL-MOTORCYCLES\df_cl-motorcycles_history.csv"