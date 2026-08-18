class ResearchError(Exception):
    """Error base del flujo de deep research."""


class ModelNotFoundError(ResearchError):
    """El código de modelo no existe en el inventario del país."""

    def __init__(self, code: str, country: str):
        self.code = code
        self.country = country
        super().__init__(
            f"No se encontró el código '{code}' en el inventario de {country}. "
            "Verifica el código en el inventario (Google Sheets)."
        )


class GeminiEmptyResponseError(ResearchError):
    """Gemini respondió sin contenido de texto utilizable."""


class KnowledgeBaseValidationError(ResearchError):
    """El KB generado no cumple la estructura esperada."""
