import os
import re
import json
from pathlib import Path
from app.config import settings
from dotenv import load_dotenv
load_dotenv()


def render_template(template_path, output_path):
    with open(template_path, 'r') as f:
        content = f.read()

    # Замена всех ${VAR} на значения из .env
    pattern = re.compile(r'\$\{([A-Z0-9_]+)\}', re.IGNORECASE)

    def replace_env(match):
        var_name = match.group(1)
        return os.getenv(var_name, "")

    def replace_settingsenv(match):
        var_name = match.group(1)
        value = getattr(settings, var_name, None)
        if value is None:
            raise ValueError(f"Переменная '{var_name}' не найдена в settings")
        return str(value)

    rendered_content = pattern.sub(replace_settingsenv, content)

    with open(output_path, 'w') as f:
        f.write(rendered_content)

if __name__ == "__main__":
    template_file = "tbcrealm.json.template"
    output_file = "tbcrealm.json"

    if not Path(template_file).exists():
        raise FileNotFoundError(f"Template file '{template_file}' not found.")

    render_template(template_file, output_file)
    print(f"Файл {output_file} успешно создан.")