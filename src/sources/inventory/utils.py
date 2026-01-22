import pandas as pd

def transform_database(data_base_to_transform: pd.DataFrame, country_code: str) -> pd.DataFrame:
    """
    Transforma la base de datos del inventario del país seleccionado
    y la transforma para que sea utilizada en el comparador
    Returns:
        pd.DataFrame: Base de datos transformada
    """
    if not country_code in ["CO", "MX", "CL "]:
        return ValueError(f"Country code {country_code} not supported")

    data_base_to_transform['Fecha de actualización'] = pd.to_datetime(data_base_to_transform['Fecha de actualización'], dayfirst=True)
    last_date = data_base_to_transform['Fecha de actualización'].max().strftime('%d/%m/%Y')
    data_base_to_transform['Fecha de actualización'] = data_base_to_transform['Fecha de actualización'].dt.strftime('%d/%m/%Y')
    df_today = data_base_to_transform[data_base_to_transform['Fecha de actualización'] == last_date]

    # Filtrar por estado disponible o sin stock
    estados_validos = ["available", "no_stock"]
    df_today = df_today[df_today["Estado"].isin(estados_validos)]

    # Excluir los que tienen redirección
    df_today = df_today[df_today["tiene_redirección"] == False]

    # Seleccionar solo las columnas necesarias
    columnas_a_usar = ["Fecha de actualización", "code", "Marca", "Modelo", "Año", "Precio Neto", "Tipo"]
    df_columnas_seleccionadas = df_today[columnas_a_usar].copy()
    df_columnas_seleccionadas = df_columnas_seleccionadas.rename(columns={"Precio Neto": "Precio"})

    # Eliminar duplicados por código
    df_desduplicadas = df_columnas_seleccionadas.drop_duplicates(subset="code").copy()

    # Agregar columna de URL
    df_desduplicadas["url"] = df_desduplicadas["code"].apply(
        lambda x: f"https://www.galgo.com/{country_code.lower()}/motos/{x}"
    )

    # Definir columnas finales
    columnas_finales = ["Fecha de actualización", "code", "Marca", "Modelo", "Año", "Tipo", "Precio", "url"]
    return df_desduplicadas[columnas_finales]
