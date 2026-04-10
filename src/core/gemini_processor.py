from google import genai
import re

class GeminiProcessor:
    def __init__(self):
        self.client = genai.Client()
        self.model = 'gemini-3-pro-preview'

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
        try:
            for output in interaction.outputs:
                if hasattr(output, "text"):
                    final_output += output.text
            return final_output
        except Exception as e:
            return f"Error processing interaction outputs: {e}"

