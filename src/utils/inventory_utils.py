import os
from config.paths import SRC_DIR
from utils.utils import get_country_code
import pandas as pd

def load_inventory_data(country:str):
    """Carga la base de inventario según el país"""
    inventory_paths = {
        "Colombia": r"C:\Users\JTRUJILLO\Documents\Galgo\Scripts\Data\historical_data\history\CO\BaseCOv2.csv",
        "Mexico": r"C:\Users\JTRUJILLO\Documents\Galgo\Scripts\Data\historical_data\history\MX\BaseMXv5.csv",
        "Chile": r"C:\Users\JTRUJILLO\Documents\Galgo\Scripts\Data\historical_data\history\CL-MOTORCYCLES\df_cl-motorcycles_history.csv"
    }

    path = inventory_paths.get(country)
    if not path:
        raise ValueError(f"País no soportado: {country}")

    df = pd.read_csv(path)
    return df, get_country_code(country)