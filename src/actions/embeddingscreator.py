import os
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm
import psycopg as pg
from config import DISCUSSIONS_FILE, LLM_MODELS

load_dotenv()
load_dotenv(dotenv_path=".env", override=True)

class EmbeddingsCreator:
    def __init__(self, db_manager):
        self.db = db_manager
        self.client = OpenAI(api_key=os.getenv("OPENAI_TOKEN"))
        self.model = "text-embedding-3-small"
        self.batch_size = 100

    def read_discussion_ids(self):
        if not os.path.exists(DISCUSSIONS_FILE):
            print("❌ Arquivo discussions.txt não encontrado.")
            return []
        with open(DISCUSSIONS_FILE, "r", encoding="utf-8") as f:
            return [int(line.strip().split("/")[-1]) for line in f if line.strip()]

    def create_vector_fields(self):
        print("🧱 Verificando campos vetoriais...")
        try:
            with self.db.conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
                cur.execute("""
                    ALTER TABLE posts 
                    ADD COLUMN IF NOT EXISTS title_vector vector(1536),
                    ADD COLUMN IF NOT EXISTS body_vector vector(1536);
                """)
            self.db.conn.commit()
            print("✅ Campos vetoriais criados ou já existentes.")
        except (Exception, pg.Error) as error:
            print(f"❌ Erro ao adicionar campos vetoriais: {error}")
            self.db.conn.rollback()

    def create_vector_indexes(self):
        print("🔍 Criando índices vetoriais...")
        try:
            with self.db.conn.cursor() as cur:
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS title_embedding_idx 
                    ON posts USING hnsw (title_vector vector_cosine_ops);
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS body_embedding_idx 
                    ON posts USING hnsw (body_vector vector_cosine_ops);
                """)
            self.db.conn.commit()
            print("✅ Índices vetoriais criados.")
        except (Exception, pg.Error) as error:
            print(f"❌ Erro ao criar índices vetoriais: {error}")
            self.db.conn.rollback()

    def reset_vectors(self):
        
        discussion_ids = self.read_discussion_ids()

        if not discussion_ids:
            print("⚠️ Nenhum ID encontrado.")
            return

        try:
            with self.db.conn.cursor() as cur:
                cur.execute("""
                    UPDATE posts
                    SET title_vector = NULL, body_vector = NULL
                    WHERE id = ANY(%s)
                """, (discussion_ids,))
            self.db.conn.commit()
            
        except Exception as e:
            print(f"❌ Erro ao limpar embeddings: {e}")
            self.db.conn.rollback()

    def generate_embeddings_from_text(self, text):
        if not text:
            return None
        try:
            response = self.client.embeddings.create(input=[text], model=self.model)
            return response.data[0].embedding
        except Exception as e:
            print(f"⚠️ Erro ao gerar embedding: {e}")
            return None

    def generate_embeddings(self):
        discussion_ids = self.read_discussion_ids()
        if not discussion_ids:
            print("⚠️ Nenhum ID encontrado.")
            return

        try:
            with self.db.conn.cursor() as cur:
                for post_id in tqdm(discussion_ids, desc="Gerando embeddings"):
                    cur.execute("SELECT title, body FROM posts WHERE id = %s", (post_id,))
                    row = cur.fetchone()

                    if not row:
                        tqdm.write(f"⚠️ Post {post_id} não encontrado.")
                        continue

                    title, body = row
                    title_emb = self.generate_embeddings_from_text(title)
                    body_emb = self.generate_embeddings_from_text(body)

                    cur.execute("""
                        UPDATE posts
                        SET title_vector = %s, body_vector = %s
                        WHERE id = %s
                    """, (title_emb, body_emb, post_id))

                    self.db.conn.commit()
                    #tqdm.write(f"✅ ID {post_id} atualizado")

        except Exception as e:
            print(f"❌ Erro ao gerar embeddings: {e}")
            self.db.conn.rollback()
