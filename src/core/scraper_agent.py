from typing import Dict, Any
from .gemini_processor import GeminiProcessor
from .prompt_utils import read_prompt_from_file, replace_variables
import json
import os


class ScraperAgent:
    """
    Agente especializado en recolectar información sobre motocicletas.

    Responsabilidades:
    - Recolectar experiencias y opiniones de usuarios del país específico
    - Extraer información estructurada sin filtrar
    - Etiquetar fuentes con país identificado
    """

    def __init__(self, processor: GeminiProcessor = None):
        """
        Inicializa el ScraperAgent.

        Args:
            processor: Instancia de GeminiProcessor. Si es None, se crea una nueva.
        """
        self.processor = processor or GeminiProcessor()
        # Ruta relativa desde la raíz del proyecto
        self.prompt_template_path = "../src/data/input/prompts/scraper_agent_template.md"

    def scrape(self, marca: str, modelo: str, año: int, pais: str) -> Dict[str, Any]:
        """
        Ejecuta el proceso de scraping para obtener experiencias de usuarios.

        Args:
            marca: Marca de la motocicleta
            modelo: Modelo de la motocicleta
            año: Año del modelo
            pais: País específico (Colombia, México, Chile)

        Returns:
            Dict con estructura:
            {
                "experiencias_usuarios": [
                    {
                        "fuente": "...",
                        "pais_identificado": "...",
                        "tipo_contenido": "...",
                        "fecha_aprox": "...",
                        "extractos_relevantes": [...],
                        "menciones_specs_tecnicas": [...],
                        "observacion": "..." (opcional)
                    }
                ]
            }
        """
        # Leer y preparar el prompt
        prompt = read_prompt_from_file(self.prompt_template_path)
        prompt = replace_variables(prompt, {
            "{MARCA}": marca,
            "{MODELO}": modelo,
            "{AÑO}": str(año),
            "{PAIS}": pais
        })

        # Ejecutar búsqueda con Gemini
        response = self.processor.send_prompt(prompt)

        # Extraer JSON de la respuesta
        return self._parse_response(response)

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Extrae el JSON estructurado de la respuesta de Gemini.

        Args:
            response: Respuesta de texto de Gemini

        Returns:
            Dict con las experiencias parseadas, o estructura de error si falla
        """
        # Intentar extraer JSON de la respuesta
        # Gemini puede devolver texto con JSON embebido
        try:
            # Buscar bloque JSON en la respuesta
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                if json_end == -1:
                    # Si no encuentra el cierre, buscar hasta el final
                    json_str = response[json_start:].strip()
                else:
                    json_str = response[json_start:json_end].strip()
            elif "```" in response:
                # JSON sin etiqueta de lenguaje
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                if json_end == -1:
                    json_str = response[json_start:].strip()
                else:
                    json_str = response[json_start:json_end].strip()
            else:
                # Intentar parsear toda la respuesta como JSON
                json_str = response.strip()

            # Limpiar posibles caracteres residuales
            json_str = json_str.strip()

            # Si empieza con { o [, intentar parsear
            if json_str.startswith(("{", "[")):
                return json.loads(json_str)
            else:
                # Buscar el primer { en la respuesta
                first_brace = json_str.find("{")
                if first_brace != -1:
                    # Buscar el último } balanceado
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

            # Si no se pudo extraer, retornar error
            return {
                "error": "No se pudo encontrar JSON válido en la respuesta",
                "raw_response": response
            }

        except json.JSONDecodeError as e:
            # Si falla el parsing, retornar estructura con error
            return {
                "error": f"Error parsing JSON response: {e}",
                "raw_response": response
            }
        except Exception as e:
            # Cualquier otro error
            return {
                "error": f"Error inesperado al procesar respuesta: {e}",
                "raw_response": response
            }
