import pandas as pd

def get_basic_data_model(df:pd.DataFrame, country:str) -> dict:
    """
    Obtiene los datos básicos de un modelo
    """
    return {
        "code": df["code"].iloc[0],
        "brand": df["brand"].iloc[0],
        "model": df["model"].iloc[0],
        "year": str(df["year"].iloc[0]),
        "country": {"CO": "Colombia", "MX": "Mexico", "CL": "Chile"}.get(country, country),
        "type": str(df["type"].iloc[0]),
        "publication_url": df["publication_url"].iloc[0],
        "publication_image_url": df["publication_image_url"].iloc[0],
    }