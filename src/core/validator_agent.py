from typing import Dict, Any, List, Optional, Union
from .gemini_processor import GeminiProcessor
from .prompt_utils import read_prompt_from_file, replace_variables, validate_prompt_variables
from .base_knowledge import format_technical_specs
from src.config.settings import VALIDATOR_AGENT_TEMPLATE_PATH, VALIDATOR_RE_RESEARCH_TEMPLATE_PATH
import json


class ValidatorAgent:
    """
    Agente especializado en validar experiencias de usuarios contra ficha técnica.

    Responsabilidades:
    - Validar que experiencias correspondan al modelo/país correcto
    - Detectar contradicciones entre experiencias y ficha técnica
    - Ejecutar re-research para casos ambiguos
    - Clasificar experiencias en validadas, verificadas, excluidas
    """

    def __init__(self, brand: str, model: str, year: int, experiencias: List[Dict[str, Any]], ficha_tecnica: Union[Dict[str, Any], str, List[Dict[str, Any]]], country: str):
        """
        Inicializa el ValidatorAgent.

        Args:
            brand: Marca de la motocicleta
            model: Modelo de la motocicleta
            year: Año del modelo
            experiencias: Lista de experiencias del ScraperAgent
            ficha_tecnica: Ficha técnica (puede ser dict, string o lista)
            country: País específico
        """
        self.processor = GeminiProcessor()
        # Datos del modelo
        self.brand = brand
        self.model = model
        self.year = year
        self.country = country
        self.experiencias = experiencias
        self.ficha_tecnica = ficha_tecnica
        # Rutas de los prompts
        self.prompt_template_path = VALIDATOR_AGENT_TEMPLATE_PATH
        self.re_research_template_path = VALIDATOR_RE_RESEARCH_TEMPLATE_PATH

    def get_prompt_template(self) -> str:
        prompt = replace_variables(read_prompt_from_file(self.prompt_template_path), {
            "{MARCA}": self.brand,
            "{MODELO}": self.model,
            "{AÑO}": str(self.year),
            "{FICHA_TECNICA}": self._format_ficha_tecnica(self.ficha_tecnica, self.brand, self.model, self.year, self.country),
            "{PAIS}": self.country,
            "{EXPERIENCIAS}": json.dumps(self.experiencias, ensure_ascii=False, indent=2)
        })
        return prompt

    def validate(self) -> Dict[str, Any]:
        """
        Valida experiencias contra la ficha técnica (Nivel 1: Validación automática).

        Args:
            ficha_tecnica: Puede ser:
                - Dict con ficha técnica (formato de get_basic_data_model con 'technical_specs' formateado)
                - Dict con 'technical_specs' como string o lista raw
                - String con lista de specs (formato raw)
                - Lista de dicts con specs

        Returns:
            Dict con estructura de validación inicial y casos que requieren re-research
        """
        # Leer y preparar el prompt
        prompt = self.get_prompt_template()

        # Ejecutar validación con Gemini
        response = self.processor.send_prompt(prompt)

        # Extraer JSON de la respuesta
        return self._parse_response(response)

    def re_research(
        self,
        experiencia: Dict[str, Any],
        flag: str
    ) -> Dict[str, Any]:
        """
        Ejecuta re-research (Nivel 2) para una experiencia con flag.

        Args:
            experiencia: Experiencia que requiere verificación
            flag: Tipo de flag detectado (ej: "CONTRADICCION_FRENOS")

        Returns:
            Dict con resultado del re-research
        """
        # Leer y preparar el prompt de re-research
        prompt = read_prompt_from_file(self.re_research_template_path)

        # Preparar ficha técnica (usa la de la instancia)
        ficha_str = self._format_ficha_tecnica(self.ficha_tecnica, self.brand, self.model, self.year, self.country)

        # Preparar experiencia como JSON string
        experiencia_str = json.dumps(experiencia, ensure_ascii=False, indent=2)

        prompt = replace_variables(prompt, {
            "{MARCA}": self.brand,
            "{MODELO}": self.model,
            "{AÑO}": str(self.year),
            "{PAIS}": self.country,
            "{FICHA_TECNICA}": ficha_str,
            "{EXPERIENCIA}": experiencia_str,
            "{FLAG}": flag
        })

        # Ejecutar re-research con Gemini
        response = self.processor.send_prompt(prompt)

        # Extraer JSON de la respuesta
        return self._parse_response(response)

    def update_experience_after_re_research(
        self,
        experiencia_original: Dict[str, Any],
        resultado_re_research: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Actualiza una experiencia después del re-research.

        Args:
            experiencia_original: Experiencia original del ScraperAgent
            resultado_re_research: Resultado del re_research() con resultado, razon, extractos_ajustados, etc.

        Returns:
            Experiencia actualizada según el resultado del re-research
        """
        resultado = resultado_re_research.get("resultado", "")

        # Crear copia de la experiencia original
        experiencia_actualizada = experiencia_original.copy()

        if resultado == "INCLUIR":
            # Agregar información del re-research
            experiencia_actualizada["validacion_re_research"] = {
                "resultado": "INCLUIR",
                "razon": resultado_re_research.get("razon", ""),
                "confidence": resultado_re_research.get("confidence", 0),
                "pais_confirmado": resultado_re_research.get("pais_confirmado", False),
                "version_confirmada": resultado_re_research.get("version_confirmada", False)
            }

            # Si hay extractos ajustados, reemplazarlos
            if "extractos_ajustados" in resultado_re_research:
                experiencia_actualizada["extractos_relevantes"] = resultado_re_research["extractos_ajustados"]

        elif resultado == "INCLUIR_CON_NOTA":
            experiencia_actualizada["validacion_re_research"] = {
                "resultado": "INCLUIR_CON_NOTA",
                "razon": resultado_re_research.get("razon", ""),
                "nota": resultado_re_research.get("nota", ""),
                "confidence": resultado_re_research.get("confidence", 0)
            }

            if "extractos_ajustados" in resultado_re_research:
                experiencia_actualizada["extractos_relevantes"] = resultado_re_research["extractos_ajustados"]

        elif resultado == "EXCLUIR":
            experiencia_actualizada["validacion_re_research"] = {
                "resultado": "EXCLUIR",
                "razon": resultado_re_research.get("razon", ""),
                "confidence": resultado_re_research.get("confidence", 0)
            }

        elif resultado == "EXCLUIR_POR_PRECAUCION":
            experiencia_actualizada["validacion_re_research"] = {
                "resultado": "EXCLUIR_POR_PRECAUCION",
                "razon": resultado_re_research.get("razon", ""),
                "confidence": resultado_re_research.get("confidence", 0)
            }

        return experiencia_actualizada

    def _format_ficha_tecnica(
        self,
        ficha: Union[Dict[str, Any], str, List[Dict[str, Any]]],
        marca: str = "",
        modelo: str = "",
        año: str = "",
        pais: str = ""
    ) -> str:
        """
        Formatea la ficha técnica para incluir en el prompt.

        Args:
            ficha: Puede ser:
                - Dict con ficha completa (de get_basic_data_model)
                - Dict con solo 'technical_specs' (string o lista raw)
                - String con lista de specs raw
                - Lista de dicts con specs
            marca: Marca (si ficha no la incluye)
            modelo: Modelo (si ficha no la incluye)
            año: Año (si ficha no la incluye)
            pais: País (si ficha no la incluye)

        Returns:
            String formateado con la ficha técnica
        """
        lines = []

        # Determinar si ficha es dict, string o lista
        if isinstance(ficha, dict):
            # Si es dict completo (de get_basic_data_model)
            marca_val = ficha.get('brand', marca) or marca
            modelo_val = ficha.get('model', modelo) or modelo
            año_val = ficha.get('year', año) or año
            pais_val = ficha.get('country', pais) or pais
            technical_specs = ficha.get('technical_specs')
        elif isinstance(ficha, str):
            # Si es string, asumir que es la lista raw de specs
            marca_val = marca
            modelo_val = modelo
            año_val = año
            pais_val = pais
            technical_specs = ficha
        elif isinstance(ficha, list):
            # Si es lista, asumir que es la lista de specs
            marca_val = marca
            modelo_val = modelo
            año_val = año
            pais_val = pais
            technical_specs = ficha
        else:
            # Fallback
            marca_val = marca
            modelo_val = modelo
            año_val = año
            pais_val = pais
            technical_specs = None

        # Agregar información básica
        if marca_val:
            lines.append(f"Marca: {marca_val}")
        if modelo_val:
            lines.append(f"Modelo: {modelo_val}")
        if año_val:
            lines.append(f"Año: {año_val}")
        if pais_val:
            lines.append(f"País: {pais_val}")
        lines.append("")
        lines.append("Especificaciones Técnicas:")

        # Formatear technical_specs usando format_technical_specs
        # Esta función maneja string, lista, etc.
        specs_formateadas = format_technical_specs(technical_specs)
        lines.append(specs_formateadas)

        return "\n".join(lines)

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Extrae el JSON estructurado de la respuesta de Gemini.

        Args:
            response: Respuesta de texto de Gemini

        Returns:
            Dict con la validación parseada, o estructura de error si falla
        """
        try:
            # Buscar bloque JSON en la respuesta
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                if json_end == -1:
                    json_str = response[json_start:].strip()
                else:
                    json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                if json_end == -1:
                    json_str = response[json_start:].strip()
                else:
                    json_str = response[json_start:json_end].strip()
            else:
                json_str = response.strip()

            json_str = json_str.strip()

            # Si empieza con { o [, intentar parsear
            if json_str.startswith(("{", "[")):
                return json.loads(json_str)
            else:
                # Buscar el primer { en la respuesta
                first_brace = json_str.find("{")
                if first_brace != -1:
                    brace_count = 0
                    last_brace = first_brace
                    for i in range(first_brace, len(json_str)):
                        if json_str[i] == "{":
                            brace_count += 1
                        elif json_str[i] == "}":
                            brace_count -= 1
                            if brace_count == 0:
                                last_brace = i
                                break
                    if brace_count == 0:
                        json_str = json_str[first_brace:last_brace + 1]
                        return json.loads(json_str)

            return {
                "error": "No se pudo encontrar JSON válido en la respuesta",
                "raw_response": response
            }

        except json.JSONDecodeError as e:
            return {
                "error": f"Error parsing JSON response: {e}",
                "raw_response": response
            }
        except Exception as e:
            return {
                "error": f"Error inesperado al procesar respuesta: {e}",
                "raw_response": response
            }
