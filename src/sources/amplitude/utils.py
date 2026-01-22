import pandas as pd

def process_labels_data(data):
    if not data:
        return None

    # Extraer 'labels' y 'values' de 'data'
    labels = data["data"].get("labels", [])[1:]
    values = data["data"].get("values", [])[1:]

    # Definir nombres para columnas de etiquetas basado en su jerarquía (por ejemplo, país y región)
    label_columns = [f"Label_{i+1}" for i in range(len(labels[0]))] if labels and labels[0] else []

    # Generar nombres de columnas para valores (métricas) como Metric_1, Metric_2, etc.
    value_columns = [f"Metric_{i+1}" for i in range(len(values[0]))] if values and values[0] else []

    # Crear listas planas para cada columna de etiquetas y valores
    label_data = [[label[i] if i < len(label) else None for i in range(len(label_columns))] for label in labels]
    value_data = [[value[i] if i < len(value) else None for i in range(len(value_columns))] for value in values]

    # Crear DataFrames de etiquetas y valores
    df_labels = pd.DataFrame(label_data, columns=label_columns)
    df_values = pd.DataFrame(value_data, columns=value_columns)

    # Combinar etiquetas y valores en un solo DataFrame
    df = pd.concat([df_labels, df_values], axis=1)

    print("Datos procesados correctamente")

    return df

def process_series_data(data):
    """
    Procesa datos de Amplitude que vienen en formato de series temporales.

    Args:
        data (dict): Diccionario con la estructura de datos de Amplitude

    Returns:
        pd.DataFrame: DataFrame con los datos procesados
    """
    if not data or 'data' not in data:
        return None

    # Extraer fechas (valores X)
    dates = data['data'].get('xValues', [])

    # Extraer etiquetas de series (modelos de productos)
    series_labels = []
    series_labels_data = data['data'].get('seriesLabels', [])

    # Manejar diferentes estructuras de datos para las etiquetas
    for label_info in series_labels_data:
        if isinstance(label_info, (list, tuple)):
            # Si es una lista/tupla, tomar el segundo elemento si existe
            if len(label_info) > 1:
                series_labels.append(label_info[1])
            else:
                series_labels.append(f"Serie_{len(series_labels)}")
        else:
            # Si no es una lista/tupla, usar el valor directamente
            series_labels.append(str(label_info))

    # Extraer valores de las series
    series_data = data['data'].get('series', [])

    # Crear diccionario para almacenar datos
    df_data = {}

    # Procesar cada modelo
    for i, series in enumerate(series_data):
        if i < len(series_labels):
            model_name = series_labels[i]

            # Extraer valores para cada fecha
            values = []
            for point in series:
                values.append(point.get('value', 0))

            # Almacenar en el diccionario
            df_data[model_name] = values

    # Crear DataFrame con los datos procesados
    df = pd.DataFrame(df_data, index=dates)

    # Transponer para que los modelos sean filas y las fechas columnas
    df = df.transpose()

    print("Datos de series procesados correctamente")

    return df

def process_data(data):
    if type(data) == dict:
        if 'series' in data['data']:
            print("Series")
            df = process_series_data(data)
        elif 'labels' in data['data']:
            print("Labels")
            df = process_labels_data(data)

    return df