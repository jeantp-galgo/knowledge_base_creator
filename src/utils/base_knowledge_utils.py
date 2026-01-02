import pandas as pd

def get_basic_data_model(df:pd.DataFrame, pais:str) -> dict:
    """
    Obtiene los datos básicos de un modelo
    """
    return {
        "code": df["code"].iloc[0],
        "marca": df["Marca"].iloc[0],
        "modelo": df["Modelo"].iloc[0],
        "año": str(df["Año"].iloc[0]),
        "pais": pais,
        "tipo": str(df["Tipo"].iloc[0]),
        "url": df["url"].iloc[0],
    }