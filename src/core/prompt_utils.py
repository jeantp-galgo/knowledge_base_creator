from typing import Dict, Any

def replace_variables(prompt: str, variables: dict) -> str:
    for key, value in variables.items():
        prompt = prompt.replace(key, value)
    return prompt

def read_prompt_from_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def validate_prompt_variables(prompt: str = None) -> Dict[str, Any]:
    """
    Valida que no queden variables sin reemplazar en el prompt.

    Args:
        prompt: Prompt a validar. Si es None, usa get_prompt_template()

    Returns:
        Dict con:
        - "valid": bool - True si no hay variables sin reemplazar
        - "missing_variables": List[str] - Lista de variables encontradas sin reemplazar
        - "locations": Dict[str, List[int]] - Líneas donde aparece cada variable (opcional)
    """
    import re

    if prompt is None:
        raise ValueError("Prompt is required")

    # Variables que deberían estar reemplazadas
    expected_variables = {
        "{MARCA}", "{MODELO}", "{AÑO}", "{PAIS}", "{TIPO}", "{FICHA TECNICA}"
    }

    # Buscar todas las variables en formato {variable}
    pattern = r'\{[A-Za-zÁÉÍÓÚÑáéíóúñ\s]+\}'
    found_variables = set(re.findall(pattern, prompt))

    # Encontrar variables que no están en la lista de esperadas (probablemente sin reemplazar)
    # También buscar variantes comunes que podrían estar mal escritas
    missing = []
    for var in found_variables:
        # Normalizar para comparar (mayúsculas, sin espacios extra)
        var_normalized = var.upper().strip()
        # Si no es una variable esperada, probablemente está sin reemplazar
        if var not in expected_variables:
            # Verificar si es una variante común mal escrita
            variants = {
                "{año}": "{AÑO}",
                "{marca}": "{MARCA}",
                "{modelo}": "{MODELO}",
                "{pais}": "{PAIS}",
                "{tipo}": "{TIPO}",
                "{ficha tecnica}": "{FICHA TECNICA}",
                "{ficha_tecnica}": "{FICHA TECNICA}"
            }
            if var in variants:
                missing.append(f"{var} (debería ser {variants[var]})")
            else:
                missing.append(var)

    # Opcional: encontrar ubicaciones (números de línea)
    locations = {}
    if missing:
        lines = prompt.split('\n')
        for var in missing:
            # Extraer solo el nombre de la variable sin el mensaje de sugerencia
            var_name = var.split(' ')[0] if ' ' in var else var
            var_locations = []
            for i, line in enumerate(lines, 1):
                if var_name in line:
                    var_locations.append(i)
            if var_locations:
                locations[var_name] = var_locations

    return {
        "valid": len(missing) == 0,
        "missing_variables": missing,
        "locations": locations
    }