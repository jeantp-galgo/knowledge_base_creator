from typing import Dict, Any, List, Union
from .gemini_processor import GeminiProcessor
from .prompt_utils import read_prompt_from_file, replace_variables
from .base_knowledge import format_technical_specs
import json


class QAAgent:
    """
    Agente especializado en validar la calidad del Knowledge Base generado.

    Responsabilidades:
    - Verificar consistencia con ficha técnica
    - Validar generalizaciones apropiadas
    - Detectar contradicciones internas
    - Verificar formato correcto
    - Identificar información no respaldada
    """

    def __init__(self, processor: GeminiProcessor = None):
        """
        Inicializa el QAAgent.

        Args:
            processor: Instancia de GeminiProcessor. Si es None, se crea una nueva.
        """
        self.processor = processor or GeminiProcessor()
        self.prompt_template_path = "src/data/input/prompts/qa_agent_template.md"

    def validate(
        self,
        knowledge_base: str,
        ficha_tecnica: Union[Dict[str, Any], str, List[Dict[str, Any]]],
        experiencias_validadas: List[Dict[str, Any]],
        experiencias_verificadas: List[Dict[str, Any]],
        marca: str,
        modelo: str,
        año: int,
        pais: str
    ) -> Dict[str, Any]:
        """
        Valida la calidad del Knowledge Base generado.

        Args:
            knowledge_base: KB generado (string)
            ficha_tecnica: Ficha técnica (puede ser dict, string o lista)
            experiencias_validadas: Lista de experiencias validadas usadas
            experiencias_verificadas: Lista de experiencias verificadas usadas
            marca: Marca de la motocicleta
            modelo: Modelo de la motocicleta
            año: Año del modelo
            pais: País específico

        Returns:
            Dict con resultado de la validación QA
        """
        # Leer y preparar el prompt
        prompt = read_prompt_from_file(self.prompt_template_path)

        # Preparar ficha técnica
        ficha_str = self._format_ficha_tecnica(ficha_tecnica, marca, modelo, año, pais)

        # Combinar todas las experiencias
        todas_experiencias = experiencias_validadas + experiencias_verificadas

        # Preparar experiencias como JSON string
        experiencias_str = json.dumps(todas_experiencias, ensure_ascii=False, indent=2)

        # Calcular estadísticas de evidencia
        estadisticas = self._calcular_estadisticas(todas_experiencias)

        prompt = replace_variables(prompt, {
            "{MARCA}": marca,
            "{MODELO}": modelo,
            "{AÑO}": str(año),
            "{PAIS}": pais,
            "{FICHA_TECNICA}": ficha_str,
            "{KNOWLEDGE_BASE}": knowledge_base,
            "{EXPERIENCIAS}": experiencias_str,
            "{ESTADISTICAS}": estadisticas
        })

        # Ejecutar validación con Gemini
        response = self.processor.send_prompt(prompt)

        # Extraer JSON de la respuesta
        return self._parse_response(response)

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
        """
        if isinstance(ficha, dict):
            marca_val = ficha.get('brand', marca) or marca
            modelo_val = ficha.get('model', modelo) or modelo
            año_val = ficha.get('year', año) or año
            pais_val = ficha.get('country', pais) or pais
            technical_specs = ficha.get('technical_specs')
        elif isinstance(ficha, str):
            marca_val = marca
            modelo_val = modelo
            año_val = año
            pais_val = pais
            technical_specs = ficha
        elif isinstance(ficha, list):
            marca_val = marca
            modelo_val = modelo
            año_val = año
            pais_val = pais
            technical_specs = ficha
        else:
            marca_val = marca
            modelo_val = modelo
            año_val = año
            pais_val = pais
            technical_specs = None

        specs_formateadas = format_technical_specs(technical_specs)

        lines = []
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
        lines.append(specs_formateadas)

        return "\n".join(lines)

    def _calcular_estadisticas(self, experiencias: List[Dict[str, Any]]) -> str:
        """
        Calcula estadísticas sobre las experiencias para validar generalizaciones.
        """
        total_experiencias = len(experiencias)

        categorias = {}
        modificaciones = []

        for exp in experiencias:
            extractos = exp.get("extractos_relevantes", []) or exp.get("extractos", [])
            for extracto in extractos:
                categoria = extracto.get("categoria", "otro")
                categorias[categoria] = categorias.get(categoria, 0) + 1

                if categoria == "modificaciones":
                    modificaciones.append(extracto.get("texto", ""))

        lines = []
        lines.append(f"Total de experiencias: {total_experiencias}")
        lines.append("")
        lines.append("Distribución por categoría:")
        for cat, count in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  - {cat}: {count} extractos")

        lines.append("")
        lines.append(f"Ejemplos de modificaciones encontrados: {len(modificaciones)}")
        if len(modificaciones) > 0:
            for i, mod in enumerate(modificaciones, 1):
                lines.append(f"  {i}. {mod[:150]}")

        return "\n".join(lines)

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Extrae el JSON estructurado de la respuesta de Gemini.
        """
        try:
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

            if json_str.startswith(("{", "[")):
                return json.loads(json_str)
            else:
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
