from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

COUNTRY = "CO" # "MX", "CL", "CO"

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