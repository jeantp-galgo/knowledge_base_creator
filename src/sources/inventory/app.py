import pandas as pd

from src.config import settings
from src.core.exceptions import ModelNotFoundError
from src.sources.database.sheets.inventory import load_inventory


class Inventory:
    def __init__(self, country: str | None = None):
        self.country = country or settings.COUNTRY

    def load_db_from_country_selected(self) -> pd.DataFrame:
        """
        Carga la base de datos del inventario del país seleccionado desde Google Sheets.

        Returns:
            pd.DataFrame: Base de datos del inventario

        Raises:
            ValueError: Si el país no está soportado o el inventario está vacío
        """
        if self.country not in settings.SUPPORTED_COUNTRIES:
            raise ValueError(
                f"Country code {self.country} not supported. "
                f"Soportados: {', '.join(settings.SUPPORTED_COUNTRIES)}"
            )

        data_base = load_inventory(self.country)
        if data_base.empty:
            raise ValueError(f"El inventario de {self.country} está vacío en Google Sheets.")

        return data_base

    def get_model_by_code(self, code: str) -> pd.Series:
        """
        Devuelve la fila del inventario correspondiente a un código de modelo.

        Raises:
            ModelNotFoundError: Si el código no existe en el inventario
        """
        data_base = self.load_db_from_country_selected()
        matches = data_base[data_base["code"] == code]

        if matches.empty:
            raise ModelNotFoundError(code, self.country)
        if len(matches) > 1:
            print(f"Aviso: {len(matches)} filas con code '{code}'; se usa la primera.")

        return matches.iloc[0]
