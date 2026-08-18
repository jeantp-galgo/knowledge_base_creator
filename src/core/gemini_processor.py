from google import genai

from src.config import settings
from src.core.exceptions import GeminiEmptyResponseError


class GeminiProcessor:
    def __init__(self, model: str | None = None):
        self.client = genai.Client()
        self.model = model or settings.GEMINI_MODEL

    def send_prompt(self, prompt:str) -> str:
        try:
            interaction = self.client.interactions.create(
                model=self.model,
                input=prompt,
                tools=[{'type': 'google_search'}]
            )
            return self.get_response(interaction)
        except Exception as e:
            error_text = str(e)
            lowered = error_text.lower()
            is_recitation_block = ("recitation" in lowered) or ("copyright" in lowered)
            if is_recitation_block:
                safe_suffix = (
                    "\n\n### Instrucción de seguridad de contenido\n"
                    "- No cites ni reproduzcas texto literal de fuentes externas.\n"
                    "- Parafrasea toda evidencia en tus propias palabras.\n"
                    "- Resume ideas en fragmentos breves y no consecutivos.\n"
                    "- No copies títulos completos, descripciones completas o transcripciones.\n"
                    "- Si una fuente requiere cita textual, omítela y reporta el hallazgo de forma agregada.\n"
                )
                safe_prompt = (prompt or "") + safe_suffix
                try:
                    retry_interaction = self.client.interactions.create(
                        model=self.model,
                        input=safe_prompt,
                        tools=[{'type': 'google_search'}]
                    )
                    return self.get_response(retry_interaction)
                except Exception as retry_e:
                    raise retry_e
            raise

    def get_response(self, interaction) -> str:
        final_output = ""
        for output in interaction.outputs:
            if hasattr(output, "text"):
                final_output += output.text
        if not final_output.strip():
            raise GeminiEmptyResponseError(
                "Gemini no devolvió texto en la interacción; no se genera el KB."
            )
        return final_output

