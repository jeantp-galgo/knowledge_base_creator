from google import genai

class GeminiProcessor:
    def __init__(self):
        self.client = genai.Client()
        self.model = 'gemini-3-pro-preview'

    def send_prompt(self, prompt:str) -> str:
        interaction = self.client.interactions.create(
            model=self.model,
            input=prompt,
            tools=[{'type': 'google_search'}]
        )
        return self.get_response(interaction)

    def get_response(self, interaction) -> str:
        final_output = ""
        for output in interaction.outputs:
            if hasattr(output, "text"):
                final_output += output.text
        return final_output

