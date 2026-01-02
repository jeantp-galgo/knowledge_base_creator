
def get_country_code(pais:str) -> str:
    """
    Obtiene el código del país
    """
    return {
        "Colombia": "CO",
        "Mexico": "MX",
        "Chile": "CL"
    }[pais]