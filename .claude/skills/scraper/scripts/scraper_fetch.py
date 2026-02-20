from google import genai
import os
import json
from dotenv import load_dotenv
load_dotenv()


class GeminiScraper:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = "gemini-3-pro-preview"
        self.max_retries = 3

    def fetch(self, prompt: str) -> dict:
        """
        Ejecuta el prompt en Gemini con google_search y retorna JSON estructurado.
        El prompt debe ser construido por Claude usando el SKILL.md como guia.
        Reintenta hasta max_retries veces si el JSON retornado es invalido.

        Args:
            prompt: Prompt completo ya construido por Claude, incluyendo
                    el schema esperado, parametros de busqueda y restricciones.

        Returns:
            dict con clave "experiencias_usuarios" (lista de experiencias).
            En caso de fallo total: {"experiencias_usuarios": [], "error": "..."}
        """
        for attempt in range(1, self.max_retries + 1):
            raw = self._call_gemini(prompt)
            result = self._parse_json(raw)
            if result is not None:
                return result
            print(f"[GeminiScraper] Intento {attempt}/{self.max_retries}: JSON invalido, reintentando...")

        return {
            "experiencias_usuarios": [],
            "error": f"No se pudo obtener JSON valido despues de {self.max_retries} intentos"
        }

    def _call_gemini(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={"tools": [{"google_search": {}}]},
            )
            return response.text.strip()
        except Exception as e:
            print(f"[GeminiScraper] Error llamando Gemini: {e}")
            return ""

    def _parse_json(self, raw: str) -> dict | None:
        if not raw:
            return None
        text = raw
        # Remover bloques markdown si Gemini los incluye por error
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1])
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None


## Espacio para agregar otros proveedores (Tavily, Firecrawl, etc.)
## Todos deben implementar fetch(prompt: str) -> dict con el mismo contrato.


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Uso: python scraper_fetch.py <input.json> <output.json>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    scraper = GeminiScraper()
    resultado = scraper.fetch(data['prompt'])

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    count = len(resultado.get('experiencias_usuarios', []))
    print(f"[Scraper] Completado. Experiencias recolectadas: {count}")
    if 'error' in resultado:
        print(f"[Scraper] ERROR: {resultado['error']}")
