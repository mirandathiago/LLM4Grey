import os
import json
import random
import psycopg
from config import DATASETS_DIR, DISCUSSIONS_FILE, INCLUDED_FILE 

class DatasetCreator:
    def __init__(self, db_manager):
        if not db_manager or not hasattr(db_manager, "cursor"):
            raise ValueError("❌ Erro: Criador recebeu um objeto de banco de dados inválido.")

        self.db = db_manager
        self.datasets_dir = DATASETS_DIR
        self.discussions_file = DISCUSSIONS_FILE
        self.included_file = INCLUDED_FILE

        if not os.path.exists(self.datasets_dir):
            os.makedirs(self.datasets_dir)

    def get_unique_dataset_name(self, prefix=""):
        while True:
            dataset_name = input(f"📂 Nome do arquivo para salvar o dataset {prefix} (sem extensão): ").strip()
            dataset_path = os.path.join(self.datasets_dir, f"{dataset_name}.json")

            if os.path.exists(dataset_path):
                print(f"⚠️ O arquivo {dataset_name}.json já existe. Escolha outro nome.")
            else:
                return dataset_name

    def extract_post_ids(self):
        if not os.path.exists(self.discussions_file):
            print("❌ Arquivo discussions.txt não encontrado!")
            return []

        with open(self.discussions_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            print("⚠️ O arquivo discussions.txt está vazio. Nenhuma ação será tomada.")
            return []

        post_ids = sorted(set(int(line.strip().split("/")[-1]) for line in lines if line.strip()))
        return post_ids

    def read_included_ids(self):
        included_ids = set()
        if os.path.exists(self.included_file):
            with open(self.included_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            post_id = int(line.split("/")[-1])
                            included_ids.add(post_id)
                        except ValueError:
                            print(f"⚠️ Erro ao processar a linha '{line}' em included.txt. Pulando...")
        return included_ids

    def fetch_posts_and_comments(self, post_ids):
        posts_data = []

        for post_id in post_ids:
            try:
                self.db.cursor.execute(
                    "SELECT Id, Title, Body, Score, CreationDate, ViewCount, Tags, AnswerCount, FavoriteCount, OwnerUserId FROM Posts WHERE Id = %s",
                    (post_id,)
                )
                post = self.db.cursor.fetchone()

                if not post:
                    print(f"⚠️ Post {post_id} não encontrado. Pulando...")
                    continue

                self.db.cursor.execute(
                    "SELECT Text, Score, UserId FROM Comments WHERE PostId = %s AND UserId = %s",
                    (post_id, post[9])
                )
                comments = [{"text": row[0], "score": row[1], "userId": row[2]} for row in self.db.cursor.fetchall()]

                posts_data.append({
                    "id": post[0],
                    "title": post[1],
                    "body": post[2],
                    "score": post[3],
                    "creationdate": str(post[4]),
                    "viewcount": post[5],
                    "tags": post[6],
                    "answercount": post[7],
                    "favoritecount": post[8],
                    "userId": post[9],
                    "comments": comments
                })
            except psycopg.Error as e:
                print(f"❌ Erro ao buscar post {post_id}: {e}")

        return posts_data

    def create_dataset(self):
        post_ids = self.extract_post_ids()
        if not post_ids:
            print("⚠️ Nenhum ID encontrado no discussions.txt.")
            return

        dataset_name = self.get_unique_dataset_name()
        full_data = self.fetch_posts_and_comments(post_ids)

        dataset_path = os.path.join(self.datasets_dir, f"{dataset_name}.json")
        with open(dataset_path, "w", encoding="utf-8") as f:
            json.dump(full_data, f, indent=4)

        print(f"✅ Dataset completo salvo com {len(full_data)} posts em: {dataset_path}")
        self.create_human_review_file(post_ids, dataset_name)

    def create_sample_dataset(self):
        post_ids = self.extract_post_ids()
        included_ids = self.read_included_ids()

        if not post_ids:
            print("⚠️ Nenhum ID encontrado no discussions.txt.")
            return

        try:
            total_sample = int(input("Quantos posts deseja na amostra? "))
            yes_sample = int(input("Quantos posts devem ser 'Yes' (inclusos)? "))
            no_sample = total_sample - yes_sample
        except ValueError:
            print("❌ Entrada inválida! Insira apenas números inteiros.")
            return

        included_list = sorted(list(included_ids))
        available_no_list = sorted([pid for pid in post_ids if pid not in included_ids])

        if yes_sample > len(included_list):
            print("⚠️ O número de 'Yes' escolhidos é maior que os disponíveis. Ajustando automaticamente.")
            yes_sample = len(included_list)

        if no_sample > len(available_no_list):
            print("⚠️ O número de 'No' escolhidos é maior que os disponíveis. Ajustando automaticamente.")
            no_sample = len(available_no_list)

        sample_yes_ids = random.sample(included_list, yes_sample)
        sample_no_ids = random.sample(available_no_list, no_sample)

        sample_ids = sorted(sample_yes_ids + sample_no_ids)

        dataset_name = self.get_unique_dataset_name(prefix="(Amostra)")
        sample_data = self.fetch_posts_and_comments(sample_ids)

        dataset_path = os.path.join(self.datasets_dir, f"{dataset_name}.json")
        with open(dataset_path, "w", encoding="utf-8") as f:
            json.dump(sample_data, f, indent=4)

        print(f"✅ Dataset de amostra salvo com {len(sample_data)} posts em: {dataset_path}")
        self.create_human_review_file(sample_ids, dataset_name)

    def create_human_review_file(self, post_ids, dataset_name):
        included_ids = self.read_included_ids()
        results = [{"id": post_id, "inclusion": "Yes" if post_id in included_ids else "No"} for post_id in post_ids]

        results_path = os.path.join(self.datasets_dir, f"{dataset_name}_human_review.json")
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)

        print(f"✅ Arquivo de revisão humana salvo em: {results_path}")
