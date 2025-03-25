import os
import inquirer
from steps.step import Step
from config import LLM_MODELS, PROMPT_TECHNIQUES, DATASETS_DIR
from actions.analysismanager import AnalysisManager

class Analysis(Step):

    def run(self):
        datasets = [
            file for file in os.listdir(DATASETS_DIR)
            if file.endswith(".json") and "_human_review" not in file
        ]
        if not datasets:
            print("❌ Nenhum dataset disponível. Gere um dataset antes de iniciar a análise.")
            return

        dataset_question = [
            inquirer.List(
                "dataset",
                message="Escolha o dataset para análise:",
                choices=datasets
            )
        ]
        dataset_choice = inquirer.prompt(dataset_question)["dataset"]

        while True:
            model_question = [
                inquirer.Checkbox(
                    'models',
                    message="Selecione os modelos LLM para análise:",
                    choices=list(LLM_MODELS.keys())
                )
            ]
            selected_models = inquirer.prompt(model_question)['models']
            if selected_models:
                break
            print("⚠️ Você deve selecionar pelo menos um modelo.\n")

        while True:
            prompt_question = [
                inquirer.Checkbox(
                    'prompts',
                    message="Selecione os prompts a serem utilizados:",
                    choices=PROMPT_TECHNIQUES
                )
            ]
            selected_prompts = inquirer.prompt(prompt_question)['prompts']
            if selected_prompts:
                break
            print("⚠️ Você deve selecionar pelo menos um prompt.\n")

        temperature_choices = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        while True:
            temperature_question = [
                inquirer.Checkbox(
                    'temperatures',
                    message="Selecione as temperaturas a serem testadas:",
                    choices=[str(t) for t in temperature_choices]
                )
            ]
            temp_input = inquirer.prompt(temperature_question)['temperatures']
            if temp_input:
                selected_temperatures = [float(t) for t in temp_input]
                break
            print("⚠️ Você deve selecionar pelo menos uma temperatura.\n")

        print("\n🔍 Resumo da configuração:")
        print(f"📁 Dataset: {dataset_choice}")
        print(f"🧠 Modelos: {', '.join(selected_models)}")
        print(f"📝 Prompts: {', '.join(selected_prompts)}")
        print(f"🔥 Temperaturas: {', '.join(map(str, selected_temperatures))}\n")

        confirm_question = [
            inquirer.Confirm("confirm", message="Deseja iniciar a análise com essas configurações?", default=True)
        ]
        if not inquirer.prompt(confirm_question)["confirm"]:
            print("⏹️ Análise cancelada pelo usuário.")
            return

        manager = AnalysisManager(
            dataset=dataset_choice,
            models=selected_models,
            prompts=selected_prompts,
            temperatures=selected_temperatures
        )
        manager.run()
