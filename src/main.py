import inquirer
import pyfiglet
import os
import platform
from colorama import Fore, Style, init
from steps.preprocessing import Preprocessing
from steps.analysis import Analysis
from steps.consensus import Consensus

# Inicializar colorama para compatibilidade com Windows
init(autoreset=True)

def clear_screen():
    """Função para limpar a tela do terminal"""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def show_title():
    clear_screen()
    
    # Gerar o título com pyfiglet
    title = pyfiglet.figlet_format("LLM4GREY")
    
    terminal_width = os.get_terminal_size().columns
    centered_title = "\n".join("\x1B[3m" + Fore.LIGHTRED_EX + line.center(terminal_width) for line in title.split("\n"))

    print(centered_title + Style.RESET_ALL)
    
    print(Fore.YELLOW + Style.BRIGHT + "🔍 Ferramenta de Triagem Automatizada de Literatura Cinza com LLMs 🔍\n".center(terminal_width))

def main():
    """Menu inicial para seleção de etapas e execução da ferramenta."""
    
    while True:
        show_title()

        stage_question = [
            inquirer.List(
                'stage',
                message="Escolha a etapa que deseja executar",
                choices=[
                    "Pré-processamento",
                    "Análise",
                    "Consenso",
                    "Sair"
                ]
            )
        ]
        selected_stage = inquirer.prompt(stage_question)['stage']

        if selected_stage == "Pré-processamento":
            Preprocessing().run()
        elif selected_stage == "Análise":
            Analysis().run()
        elif selected_stage == "Consenso":
            Consensus().run()
        elif selected_stage == "Sair":
            clear_screen()
            break  

        back_question = [
            inquirer.Confirm("back", message="Deseja voltar ao menu inicial?", default=True)
        ]
        if not inquirer.prompt(back_question)["back"]:
            clear_screen()
            print("\n👋 Saindo do sistema...\n")
            break  

if __name__ == "__main__":
    main()
