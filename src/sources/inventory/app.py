from src.config.settings import *
from src.sources.inventory.utils import transform_database
import pandas as pd
import os

class Inventory:
    def __init__(self):
        self.country = COUNTRY

    def load_db_from_country_selected(self) -> pd.DataFrame:
        """
        Carga la base de datos del inventario del país seleccionado
        y la transforma para que sea utilizada en el comparador
        Returns:
            pd.DataFrame: Base de datos transformada
        """
        print(self.country)
        if not self.country in ["CO", "MX", "CL"]:
            return ValueError(f"Country code {self.country} not supported")


        if self.country == "CO":
            data_base = pd.read_csv(CO_INVENTORY_PATH)
        elif self.country == "MX":
            data_base = pd.read_csv(MX_INVENTORY_PATH)
        elif self.country == "CL":
            data_base = pd.read_csv(CL_INVENTORY_PATH)

        data_base_transformed = transform_database(data_base, self.country)

        return data_base_transformed

