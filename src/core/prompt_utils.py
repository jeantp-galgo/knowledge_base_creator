def replace_variables(prompt: str, variables: dict) -> str:
    for key, value in variables.items():
        prompt = prompt.replace(key, value)
    return prompt

def read_prompt_from_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()