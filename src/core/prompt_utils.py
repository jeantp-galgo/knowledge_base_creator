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

    # Buscar placeholders en formato {PLACEHOLDER}
    # Limitamos a letras/acentos/espacios/underscore para evitar falsos positivos con JSON.
    pattern = r'\{[A-Za-zÁÉÍÓÚÑáéíóúñ_\s]+\}'
    found_variables = sorted(set(re.findall(pattern, prompt)))

    # Cualquier placeholder encontrado en el prompt final se considera faltante.
    # Si ya se reemplazó correctamente, found_variables debería ser vacío.
    missing = found_variables

    # Opcional: encontrar ubicaciones (números de línea)
    locations = {}
    if missing:
        lines = prompt.split('\n')
        for var in missing:
            var_locations = []
            for i, line in enumerate(lines, 1):
                if var in line:
                    var_locations.append(i)
            if var_locations:
                locations[var] = var_locations

    return {
        "valid": len(missing) == 0,
        "missing_variables": missing,
        "locations": locations
    }