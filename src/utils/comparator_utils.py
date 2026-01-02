import pandas as pd
from utils.utils import get_country_code

def extract_top_3_models_from_comparator(df_top_3_models:pd.DataFrame,
                                        df_base_inventory:pd.DataFrame,
                                        code:str,
                                        pais:str,
                                        debug:bool = False) -> pd.DataFrame:
    """
    Extrae los 3 modelos comparados de la base de inventario
    Args:
        df_top_3_models: DataFrame con los 3 modelos comparados
        df_base_inventory: DataFrame con la base de inventario
        code: Código del modelo principal
        pais: País del modelo principal
        debug: Si es True, imprime los códigos disponibles
    Returns:
        List con los 3 modelos comparados
    """
    import ast
    import re
    country_code = get_country_code(pais)
    # Extraer los códigos de los modelos comparados (excluyendo el modelo principal)
    modelos_comparados = []

    for index, row in df_top_3_models.iterrows():
        available_codes = row["available_code"]
        # Si es una lista en string, conviértela a lista real
        if isinstance(available_codes, str):
            try:
                available_codes = ast.literal_eval(available_codes)
            except Exception:
                # En caso de fallo, intenta limpiar y separar
                available_codes = re.findall(rf"({country_code}\d{{3,}}-[\w-]+)", available_codes)

        # Limpiamos los códigos por si tienen espacios, corchetes, etc.
        available_codes = [c.strip(" []'\"") for c in available_codes]

        # Encontrar el código que NO es el modelo principal
        codigo_comparado = next((c for c in available_codes if c != code), None)
        # print("Código comparado:", codigo_comparado)

        # Buscar en df_base_inventory para obtener Marca y Modelo
        modelo_info = df_base_inventory[df_base_inventory["code"] == codigo_comparado]

        if not modelo_info.empty:
            modelos_comparados.append({
                "marca": modelo_info.iloc[0]["Marca"],
                "modelo": modelo_info.iloc[0]["Modelo"]
            })

    # Verificar que tenemos 3 modelos
    if debug:
        print(f"Modelos comparados encontrados: {len(modelos_comparados)}")
        for i, m in enumerate(modelos_comparados, 1):
            print(f"{i}. {m['marca']} {m['modelo']}")

        print("Output: \n", modelos_comparados)

    return modelos_comparados