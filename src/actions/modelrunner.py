import importlib
import json
from config import LLM_MODELS
from output.format import OutputFormat

class ModelRunner:

    def __init__(self, model_name, prompt_path, temperature=0.0):
        self.model_name = model_name
        self.prompt_path = prompt_path
        self.temperature = temperature
        self.model_info = LLM_MODELS.get(model_name)

        if not self.model_info:
            raise ValueError(f"❌ Modelo '{model_name}' não encontrado na configuração.")

        # Importa dinamicamente o módulo do modelo
        module = importlib.import_module(f"models.{self.model_info['file']}")
        class_name = self.model_info['file'].replace("-", "_").capitalize()

        if not hasattr(module, class_name):
            raise ImportError(
                f"❌ O módulo 'models/{self.model_info['file']}.py' não contém a classe '{class_name}'."
            )

        self.model_class = getattr(module, class_name)

    def analyze(self, discussion):

        model_instance = self.model_class(api_key=self.model_info["api_key"])

        with open(f"{self.prompt_path}/system.txt", "r", encoding="utf-8") as f:
            system_prompt = f.read().strip()

        with open(f"{self.prompt_path}/user.txt", "r", encoding="utf-8") as f:
            user_prompt = f.read().strip()

        comments_text = "\n".join([f"- {comment['text']}" for comment in discussion.get("comments", [])])
        user_prompt = (
            user_prompt
            .replace("<title>", discussion.get("title", ""))
            .replace("<body>", discussion.get("body", ""))
            .replace("<comments>", comments_text)
        )

        raw_response = model_instance.execute(system_prompt, user_prompt, self.temperature)

        try:
            json_response = json.loads(raw_response)
        except json.JSONDecodeError:
            raise ValueError(f"❌ Resposta inválida do modelo '{self.model_name}':\n{raw_response}")

        try:
            validated = OutputFormat(**json_response)
            return {
                "id": discussion["id"],
                "inclusion": validated.inclusion,
                "confidence": validated.confidence,
                "justification": validated.justification,
            }
        except Exception as e:
            raise ValueError(f"❌ Erro ao validar resposta do modelo '{self.model_name}': {e}")
