import os
import inquirer
from steps.step import Step
from utils.dbmanager import DBManager
from utils.xmlreader import XMLReader
from actions.datasetcreator import DatasetCreator
from actions.embeddingscreator import EmbeddingsCreator
from config import FILE_MAPPINGS, RAW_DATA_DIR

class Preprocessing(Step):
    def __init__(self):
        self.db = DBManager()
        self.creator = DatasetCreator(self.db)
        self.embedder = EmbeddingsCreator(self.db)
        self.xml_reader = XMLReader()

    def run(self):
        task_question = [
            inquirer.List(
                "task",
                message="Escolha a tarefa a ser realizada:",
                choices=[
                    "1 - Importação dos Dados",
                    "2 - Criação do Dataset",
                    "3 - Geração de Embeddings"
                ]
            )
        ]
        task_choice = inquirer.prompt(task_question)["task"]

        if task_choice == "1 - Importação dos Dados":
            self.process_data()

        elif task_choice == "2 - Criação do Dataset":
            dataset_type = inquirer.prompt([
                inquirer.List(
                    "dataset_type",
                    message="Escolha o tipo de dataset:",
                    choices=["1 - Completo", "2 - Amostra"]
                )
            ])["dataset_type"]

            if dataset_type == "1 - Completo":
                self.creator.create_dataset()
            elif dataset_type == "2 - Amostra":
                self.creator.create_sample_dataset()

        elif task_choice == "3 - Geração de Embeddings":
            self.embedder.create_vector_fields()
            self.embedder.create_vector_indexes()
            self.embedder.reset_vectors()
            self.embedder.generate_embeddings()

        self.db.close()

    def process_data(self):
        print("\n🔄 Criando banco e populando dados...")
        self.db.create_tables()

        print("\n📥 Importando dados XML para o banco de dados...")
        for file_name, (table_name, columns) in FILE_MAPPINGS.items():
            file_path = os.path.join(RAW_DATA_DIR, file_name)

            if os.path.exists(file_path):
                print(f"📂 Processando {file_name} para a tabela {table_name}...")
                data = self.xml_reader.parse_xml(file_path, columns)

                if data:
                    formatted_data = [list(row.values()) for row in data]
                    self.db.insert_data(table_name, columns, formatted_data)
                    print(f"✅ Inseridos {len(formatted_data)} registros na tabela {table_name}")
                else:
                    print(f"⚠️ Nenhum dado encontrado no arquivo {file_name}.")
            else:
                print(f"⚠️ Arquivo {file_name} não encontrado, ignorando.")

        self.db.commit()
        print("✅ Banco criado e dados populados com sucesso!")
