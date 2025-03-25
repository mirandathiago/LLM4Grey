import os
import json
import time
from datetime import datetime
from tqdm import tqdm
from config import DATASETS_DIR, RESULTS_DIR, PROMPT_DIR, LLM_MODELS, RATE_LIMIT_THRESHOLD
from actions.modelrunner import ModelRunner

class AnalysisManager:
    """Executa a análise em todas as combinações de modelos, prompts e temperaturas."""

    def __init__(self, dataset, prompts, models, temperatures):
        self.dataset = dataset
        self.prompts = prompts
        self.models = models
        self.temperatures = temperatures
        self.dataset_path = os.path.join(DATASETS_DIR, dataset)
        self.results_dir = RESULTS_DIR
        self.prompt_dir = PROMPT_DIR

    def run(self):
        # Carregar dataset
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            discussions = json.load(f)

        # Criar pasta de logs
        log_folder = os.path.join(self.results_dir, "logs")
        os.makedirs(log_folder, exist_ok=True)

        # Executar todas as combinações
        total_combinations = len(self.models) * len(self.prompts) * len(self.temperatures)
        print(f"\n🚀 Iniciando {total_combinations} combinações...\n")

        for model_name in self.models:
            for prompt_name in self.prompts:
                prompt_path = os.path.join(self.prompt_dir, prompt_name)

                for temp in self.temperatures:
                    print(f"\n📌 Modelo: {model_name} | Prompt: {prompt_name} | Temp: {temp}\n")

                    # Criar pasta de saída
                    result_folder = os.path.join(
                        self.results_dir,
                        f"{self.dataset.split('.')[0]}_{prompt_name}"
                    )
                    os.makedirs(result_folder, exist_ok=True)

                    model_runner = ModelRunner(
                        model_name=model_name,
                        prompt_path=prompt_path,
                        temperature=temp
                    )

                    rate_limit = LLM_MODELS[model_name].get("rate_limit", False)
                    results = []
                    request_count = 0
                    pause_time = 0
                    start_time = time.time()

                    with tqdm(total=len(discussions), desc=f"{model_name} | T{temp}", unit="item") as pbar:
                        for discussion in discussions:
                            request_count += 1
                            try:
                                response = model_runner.analyze(discussion)
                                results.append(response)
                            except Exception as e:
                                print(f"⚠️ Erro na discussão ID {discussion.get('id')}: {e}")
                            pbar.update(1)

                            if rate_limit and request_count != len(discussions)  and  request_count % RATE_LIMIT_THRESHOLD == 0:
                                print(f"⏳ Pausando por 60s para evitar bloqueio da API de {model_name}...")
                                pause_start = time.time()
                                time.sleep(60)
                                pause_time += time.time() - pause_start

                    # Salvar resultados
                    output_file = os.path.join(
                        result_folder,
                        f"{model_name}-temp-{temp}.json"
                    )
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(results, f, indent=4)

                    print(f"✅ Resultados salvos em: {output_file}")

                    # Salvar log
                    log_data = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "model": model_name,
                        "prompt": prompt_name,
                        "temperature": temp,
                        "dataset": self.dataset,
                        "discussions_analyzed": request_count,
                        "execution_time_seconds": round(time.time() - start_time, 2),
                        "pause_time_seconds": round(pause_time, 2)
                    }

                    log_file = os.path.join(
                        log_folder,
                        f"log_{model_name}_{prompt_name}_t{temp}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    )
                    with open(log_file, "w", encoding="utf-8") as f:
                        json.dump(log_data, f, indent=4)

                    print(f"📄 Log salvo em: {log_file}")
