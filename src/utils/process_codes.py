from typing import Set
from src.config.settings import SRC_DIR

def load_processed_codes(filepath: str):
    """ Cargar el archivo con los códigos ya ejecutados """
    try:
        with open(f"{SRC_DIR}/data/input/processed_codes/{filepath}.txt", "r") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        print(f"Archivo no encontrado: {filepath}. Retornando set vacío.")
        return set()
    except Exception as e:
        print(f"Error al cargar los códigos procesados: {e}")
        return set()

def save_processed_codes(filepath: str, codes: Set[str]):
    """ Guardar códigos ya ejecutados """
    try:
        with open(f"{SRC_DIR}/data/input/processed_codes/{filepath}.txt", "a", encoding="utf-8") as f:
            for code in codes:
                f.write(f"{code}\n")
        print("Códigos guardados")
    except FileNotFoundError:
        print(f"No se pudo guardar, archivo o carpeta no encontrada: {filepath}")
    except Exception as e:
        print(f"Error al guardar los códigos procesados: {e}")
