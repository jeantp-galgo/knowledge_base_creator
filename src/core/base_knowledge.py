import pandas as pd
import json
import ast
from typing import List, Dict, Any, Optional


def format_technical_specs(technical_specs: Optional[List[Dict[str, Any]]]) -> str:
    """
    Filtra y formatea los campos técnicos relevantes para la ficha técnica.
    Solo incluye campos críticos, importantes para UX y útiles como contexto.

    Args:
        technical_specs: Lista de diccionarios con estructura {key, value, type, group}
                        Puede venir como lista, string JSON o string de Python

    Returns:
        String formateado con los campos relevantes, o "NO DISPONIBLE" si no hay datos
    """
    # Si es None o está vacío, retornar NO DISPONIBLE
    if technical_specs is None:
        return "NO DISPONIBLE"

    # Si viene como string (desde CSV), intentar parsearlo
    if isinstance(technical_specs, str):
        # Si es string vacío o "NO DISPONIBLE", retornar
        if not technical_specs.strip() or technical_specs.strip().upper() == "NO DISPONIBLE":
            return "NO DISPONIBLE"

        try:
            # Intentar parsear como literal de Python (más común en pandas)
            technical_specs = ast.literal_eval(technical_specs)
        except (ValueError, SyntaxError):
            try:
                # Si falla, intentar como JSON
                technical_specs = json.loads(technical_specs)
            except (json.JSONDecodeError, ValueError):
                # Si ambos fallan, retornar NO DISPONIBLE
                return "NO DISPONIBLE"

    # Verificar que ahora sea una lista
    if not isinstance(technical_specs, list):
        return "NO DISPONIBLE"

    # Definir campos relevantes por categoría (usando los keys reales del ejemplo)
    # Críticos (alto riesgo de error entre versiones/países)
    critical_keys = {
        'front_brakes', 'rear_brakes',
        'fuel_system',
        'start_system'
    }

    # Importantes para experiencia de usuario
    ux_keys = {
        'total_weight',
        # 'seat_to_ground',  # altura del asiento
        'tank_capacity',
        'efficiency',  # rendimiento de combustible
        'displacement'  # cilindrada
    }

    # Útiles como contexto
    context_keys = {
        'engine_type',
        'transmission_type',
        'gears',
        'front_suspension', 'rear_suspension'
    }

    # Combinar todos los keys relevantes
    relevant_keys = critical_keys | ux_keys | context_keys

    # Crear diccionario para acceso rápido
    specs_dict = {}
    for spec in technical_specs:
        if not isinstance(spec, dict):
            continue

        key = spec.get('key', '')
        value = spec.get('value')

        # Solo procesar si el key es relevante
        if key in relevant_keys and value is not None:
            # Normalizar valores vacíos o "NO DISPONIBLE"
            if isinstance(value, str):
                value_upper = value.upper().strip()
                if value_upper in ['NO DISPONIBLE', 'N/A', 'NA', '', 'NONE', 'NULL']:
                    continue
            elif isinstance(value, (int, float)) and (value == 0 or pd.isna(value)):
                continue

            specs_dict[key] = {
                'value': value,
                'type': spec.get('type', 'string'),
                'group': spec.get('group', 'general')
            }

    if not specs_dict:
        return "NO DISPONIBLE"

    # Formatear agrupado por categoría para mejor legibilidad
    formatted_lines = []

    # CAMPOS CRÍTICOS
    critical_found = False
    for key in critical_keys:
        if key in specs_dict:
            if not critical_found:
                formatted_lines.append("CAMPOS CRÍTICOS:")
                critical_found = True

            value = specs_dict[key]['value']
            formatted_value = _format_value(value, key)
            formatted_lines.append(f"- {_get_display_name(key)}: {formatted_value}")

    if critical_found:
        formatted_lines.append("")  # Línea en blanco

    # IMPORTANTES PARA EXPERIENCIA DE USUARIO
    ux_found = False
    for key in ux_keys:
        if key in specs_dict:
            if not ux_found:
                formatted_lines.append("IMPORTANTES PARA EXPERIENCIA DE USUARIO:")
                ux_found = True

            value = specs_dict[key]['value']
            formatted_value = _format_value(value, key)
            formatted_lines.append(f"- {_get_display_name(key)}: {formatted_value}")

    if ux_found:
        formatted_lines.append("")  # Línea en blanco

    # ÚTILES COMO CONTEXTO
    context_found = False
    for key in context_keys:
        if key in specs_dict:
            if not context_found:
                formatted_lines.append("ÚTILES COMO CONTEXTO:")
                context_found = True

            value = specs_dict[key]['value']
            formatted_value = _format_value(value, key)
            formatted_lines.append(f"- {_get_display_name(key)}: {formatted_value}")

    return "\n".join(formatted_lines)


def _format_value(value: Any, key: str) -> str:
    """
    Formatea el valor según su tipo y el campo.
    Agrega unidades cuando sea apropiado.
    """
    if isinstance(value, (int, float)):
        # Agregar unidades según el campo
        if key == 'displacement':
            return f"{value} cc"
        elif key == 'total_weight':
            return f"{value} kg"
        elif key == 'seat_to_ground':
            return f"{value} mm"
        elif key == 'tank_capacity':
            return f"{value} litros"
        elif key == 'efficiency':
            return f"{value} km/l"
        elif key == 'gears':
            return f"{int(value)} velocidades"
        else:
            return str(value)
    else:
        return str(value)


def _get_display_name(key: str) -> str:
    """
    Convierte el key técnico a un nombre legible en español.
    """
    display_names = {
        'front_brakes': 'Freno delantero',
        'rear_brakes': 'Freno trasero',
        'fuel_system': 'Sistema de alimentación',
        'start_system': 'Sistema de arranque',
        'total_weight': 'Peso total',
        'seat_to_ground': 'Altura del asiento',
        'tank_capacity': 'Capacidad del tanque',
        'efficiency': 'Rendimiento de combustible',
        'displacement': 'Cilindrada',
        'engine_type': 'Tipo de motor',
        'transmission_type': 'Tipo de transmisión',
        'gears': 'Número de cambios',
        'front_suspension': 'Suspensión delantera',
        'rear_suspension': 'Suspensión trasera'
    }
    return display_names.get(key, key.replace('_', ' ').title())


def get_basic_data_model(df: pd.DataFrame, country: str) -> dict:
    """
    Obtiene los datos básicos de un modelo
    """
    # Obtener technical_specs del DataFrame
    technical_specs_raw = None
    if "technical_specs" in df.columns:
        technical_specs_raw = df["technical_specs"].iloc[0]
        # Si es NaN o None, convertir a None explícitamente
        if pd.isna(technical_specs_raw):
            technical_specs_raw = None

    # Formatear technical_specs
    technical_specs_formatted = format_technical_specs(technical_specs_raw)

    return {
        "code": df["code"].iloc[0],
        "brand": df["brand"].iloc[0],
        "model": df["model"].iloc[0],
        "year": str("2025"), #str(df["year"].iloc[0]), # Se fija un año ya que parece alucinar con un año tan reciente (2026 - hoy 11 de febrero) y tan poca info del modelo en el año.
        "country": {"CO": "Colombia", "MX": "Mexico", "CL": "Chile"}.get(country, country),
        "type": str(df["type"].iloc[0]),
        "publication_url": df["publication_url"].iloc[0],
        "publication_image_url": df["publication_image_url"].iloc[0],
        "technical_specs": technical_specs_formatted,
    }