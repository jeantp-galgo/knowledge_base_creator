import base64
import json
import os

from src.sources.database.sheets.reader import GoogleSheetReader

SPREADSHEET_ID = "1HX_Uz7b6Uug20wcotvRXB7QLruV16IP_0As3PLL5JPY"

COUNTRY_TABS = {
    "MX": "Base MX Moto",
    "CL": "Base CL Moto",
    "CO": "Base CO Moto",
}


def load_inventory(country: str):
    """
    Carga el inventario de motos desde Google Sheets para el país indicado.

    Args:
        country: Código de país ("MX", "CL" o "CO")

    Returns:
        pd.DataFrame con las columnas del inventario
    """
    raw = os.getenv("MKP_INVENTORY_BASE64")
    if not raw:
        raise EnvironmentError("La variable de entorno MKP_INVENTORY_BASE64 no está definida.")

    credentials = json.loads(base64.b64decode(raw))

    worksheet = COUNTRY_TABS.get(country)
    if not worksheet:
        raise ValueError(f"País '{country}' no soportado. Opciones válidas: {list(COUNTRY_TABS.keys())}")

    reader = GoogleSheetReader(credentials)
    data_base = reader.read_sheet({
        "sheet_id": SPREADSHEET_ID,
        "worksheet": worksheet,
    })
    return data_base.dropna(how="all")
