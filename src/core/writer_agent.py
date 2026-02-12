from typing import Dict, Any, List, Union
from .gemini_processor import GeminiProcessor
from .prompt_utils import read_prompt_from_file, replace_variables
from .base_knowledge import format_technical_specs
import json


class WriterAgent:
    """
    Agente especializado en generar Knowledge Base vivencial usando experiencias validadas.

    Responsabilidades:
    - Generar KB usando experiencias validadas + ficha técnica como ancla
    - Respetar la ficha técnica como ancla de verdad
    - Ser cuidadoso con generalizaciones cuando hay pocos datos
    - Usar lenguaje apropiado según cantidad de evidencia
    """

    def __init__(self, processor: GeminiProcessor = None):
        """
        Inicializa el WriterAgent.

        Args:
            processor: Instancia de GeminiProcessor. Si es None, se crea una nueva.
        """
        self.processor = processor or GeminiProcessor()
        self.prompt_template_path = "../src/data/input/prompts/knowledge_base_template.md"

    def write(
        self,
        experiencias_validadas: List[Dict[str, Any]],
        experiencias_verificadas: List[Dict[str, Any]],
        ficha_tecnica: Union[Dict[str, Any], str, List[Dict[str, Any]]],
        marca: str,
        modelo: str,
        año: int,
        pais: str,
        tipo: str = ""
    ) -> str:
        """
        Genera el Knowledge Base usando experiencias validadas y ficha técnica.

        Args:
            experiencias_validadas: Lista de experiencias validadas directamente (Nivel 1)
            experiencias_verificadas: Lista de experiencias verificadas con re-research (Nivel 2)
            ficha_tecnica: Ficha técnica (puede ser dict, string o lista)
            marca: Marca de la motocicleta
            modelo: Modelo de la motocicleta
            año: Año del modelo
            pais: País específico
            tipo: Tipo de moto (ej: "Urbana")

        Returns:
            String con el Knowledge Base generado en formato del template
        """
        # Leer y preparar el prompt
        prompt = read_prompt_from_file(self.prompt_template_path)

        # Preparar ficha técnica
        ficha_str = self._format_ficha_tecnica(ficha_tecnica, marca, modelo, año, pais)

        # Combinar todas las experiencias
        todas_experiencias = experiencias_validadas + experiencias_verificadas

        # Preparar experiencias como JSON string
        experiencias_str = json.dumps(todas_experiencias, ensure_ascii=False, indent=2)

        # Contar cantidad de experiencias por categoría para guiar al writer
        estadisticas = self._calcular_estadisticas(todas_experiencias)

        # Agregar instrucciones sobre generalizaciones
        instrucciones_generalizaciones = self._generar_instrucciones_generalizaciones(estadisticas)

        prompt = replace_variables(prompt, {
            "{marca}": marca,
            "{modelo}": modelo,
            "{año}": str(año),
            "{pais}": pais,
            "{tipo}": tipo,
            "{ficha_tecnica}": ficha_str
        })

        # Agregar sección de experiencias y restricciones al final del prompt
        prompt += f"""

---

## EXPERIENCIAS VALIDADAS

{experiencias_str}

---

## ESTADÍSTICAS DE EVIDENCIA

{estadisticas}

---

## INSTRUCCIONES SOBRE GENERALIZACIONES

{instrucciones_generalizaciones}

---

## RESTRICCIONES ADICIONALES PARA EL WRITER

1. **Respeto a la ficha técnica (ancla de verdad)**:
   - NUNCA contradigas la ficha técnica en specs técnicos
   - Si ficha dice "CBS", NO escribas "ABS"
   - Puedes mencionar percepciones que contrastan ("se siente más potente de lo que indica la ficha")

2. **Lenguaje según cantidad de evidencia**:
   - 1 ejemplo: "Un usuario reporta..." o "Se ha documentado un caso de..."
   - 2-3 ejemplos: "Algunos usuarios reportan..." o "Hay reportes de..."
   - 4+ ejemplos: "Los usuarios reportan..." o "Es común que..."
   - Para modificaciones: Si hay 1-2 ejemplos, di "Algunos usuarios modifican..." NO "Los usuarios modifican..."

3. **Modificaciones**:
   - Si hay 1-2 ejemplos: NO generalices. Di "Algunos usuarios han modificado..." o lista los casos específicos
   - Si hay 3+ ejemplos: Puedes hablar de "modificaciones comunes"
   - Si no hay información: Declara explícitamente "No hay información suficiente sobre modificaciones"

4. **Secciones con poca información**:
   - Si una categoría tiene muy pocos datos, decláralo explícitamente
   - Mejor decir "Información limitada sobre X" que inventar o generalizar

5. **Percepciones vs ficha técnica**:
   - PERMITIDO: "La ficha dice 125cc pero se siente como una 150cc" (percepción valiosa)
   - PERMITIDO: "Usuarios esperaban ABS pero tiene CBS" (en [OPINIONES_DIVIDIDAS])
   - PROHIBIDO: Escribir que tiene ABS cuando la ficha dice CBS
"""

        # Ejecutar generación con Gemini
        response = self.processor.send_prompt(prompt)

        return response

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
        Similar a ValidatorAgent pero enfocado en el uso del Writer.
        """
        lines = []

        # Determinar si ficha es dict, string o lista
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

        # Formatear technical_specs usando format_technical_specs
        specs_formateadas = format_technical_specs(technical_specs)

        return specs_formateadas

    def _calcular_estadisticas(self, experiencias: List[Dict[str, Any]]) -> str:
        """
        Calcula estadísticas sobre las experiencias para guiar al writer.
        """
        total_experiencias = len(experiencias)

        # Contar por categoría de extractos
        categorias = {}
        modificaciones = []
        comparaciones = []

        for exp in experiencias:
            extractos = exp.get("extractos_relevantes", []) or exp.get("extractos", [])
            for extracto in extractos:
                categoria = extracto.get("categoria", "otro")
                categorias[categoria] = categorias.get(categoria, 0) + 1

                if categoria == "modificaciones":
                    modificaciones.append(extracto.get("texto", ""))

        # Generar texto de estadísticas
        lines = []
        lines.append(f"Total de experiencias validadas: {total_experiencias}")
        lines.append("")
        lines.append("Distribución por categoría:")
        for cat, count in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  - {cat}: {count} extractos")

        lines.append("")
        lines.append(f"Ejemplos de modificaciones encontrados: {len(modificaciones)}")
        if len(modificaciones) > 0:
            for i, mod in enumerate(modificaciones[:3], 1):
                lines.append(f"  {i}. {mod[:100]}...")

        return "\n".join(lines)

    def _generar_instrucciones_generalizaciones(self, estadisticas: str) -> str:
        """
        Genera instrucciones específicas sobre cómo manejar generalizaciones.
        """
        # Extraer número de modificaciones de las estadísticas
        num_modificaciones = 0
        if "Ejemplos de modificaciones encontrados:" in estadisticas:
            try:
                line = [l for l in estadisticas.split("\n") if "Ejemplos de modificaciones" in l][0]
                num_modificaciones = int(line.split(":")[1].strip())
            except:
                pass

        lines = []
        lines.append("**IMPORTANTE: Manejo de Generalizaciones**")
        lines.append("")

        if num_modificaciones == 0:
            lines.append("- MODIFICACIONES: No hay información. Declara explícitamente 'No hay información suficiente sobre modificaciones'")
        elif num_modificaciones == 1:
            lines.append("- MODIFICACIONES: Solo hay 1 ejemplo. NO generalices. Di 'Un usuario ha modificado...' o 'Se ha documentado un caso de...' NO digas 'Los usuarios modifican...'")
        elif num_modificaciones == 2:
            lines.append("- MODIFICACIONES: Solo hay 2 ejemplos. Usa 'Algunos usuarios han modificado...' NO digas 'Los usuarios modifican...' o 'Es común modificar...'")
        else:
            lines.append(f"- MODIFICACIONES: Hay {num_modificaciones} ejemplos. Puedes usar 'Algunos usuarios modifican...' o listar las modificaciones encontradas")

        lines.append("")
        lines.append("**Regla general:**")
        lines.append("- 1 ejemplo = 'Un usuario reporta...' o 'Se ha documentado...'")
        lines.append("- 2-3 ejemplos = 'Algunos usuarios reportan...' o 'Hay reportes de...'")
        lines.append("- 4+ ejemplos = 'Los usuarios reportan...' o 'Es común que...'")
        lines.append("- Si no hay información suficiente, decláralo explícitamente")

        return "\n".join(lines)
