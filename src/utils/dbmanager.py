import psycopg
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", override=True)

class DBManager:

    def __init__(self):
        self.db_name = os.getenv("POSTGRES_DB")
        self.db_user = os.getenv("POSTGRES_USER")
        self.db_host = os.getenv("POSTGRES_HOST")
        self.db_port = os.getenv("POSTGRES_PORT")
        self.db_password = os.getenv("POSTGRES_PASSWORD")

        self.connect()

    def connect(self):
        try:
            self.conn = psycopg.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                dbname=self.db_name
            )
            self.cursor = self.conn.cursor()
           
        except psycopg.OperationalError as e:
            print(f"❌ Erro ao conectar ao banco '{self.db_name}': {e}")
            print("⚠️ Certifique-se de que o banco de dados já foi criado antes de executar a aplicação.")
            exit(1)  

    def insert_data(self, table_name, columns, data_rows):
        if not data_rows:
            print(f"⚠️ Nenhum dado para inserir na tabela {table_name}.")
            return

        try:
            placeholders = ", ".join(["%s"] * len(columns))  
            columns_str = ", ".join(columns)  

            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders});"

            self.cursor.executemany(query, data_rows)  
            

        except psycopg.Error as e:
            print(f"❌ Erro ao inserir dados na tabela {table_name}: {e}")

    def drop_all_tables(self):
       
        try:
            self.cursor.execute("""
                DROP TABLE IF EXISTS Comments CASCADE;
                DROP TABLE IF EXISTS Posts CASCADE;
                DROP TABLE IF EXISTS Users CASCADE;
            """)
            self.conn.commit()
            
        except psycopg.Error as e:
            print(f"❌ Erro ao apagar as tabelas: {e}")
            exit(1)

    def create_tables(self):
        schemas_dir = os.path.join(os.path.dirname(__file__), "schemas")

        if not os.path.exists(schemas_dir):
            print("❌ Diretório schemas/ não encontrado!")
            exit(1)

        sql_files = [f for f in os.listdir(schemas_dir) if f.endswith(".sql")]

        if not sql_files:
            print("❌ Nenhum arquivo SQL encontrado na pasta schemas/")
            exit(1)

        
        self.drop_all_tables()

        for sql_file in sql_files:
            self.execute_sql_file(os.path.join(schemas_dir, sql_file))

        print("✅ Todas as tabelas foram criadas com sucesso!")

    def execute_sql_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                sql_content = file.read()

            self.cursor.execute(sql_content)
            self.conn.commit()
            print(f"📜 Executado: {file_path}")

        except psycopg.Error as e:
            print(f"❌ Erro ao executar {file_path}: {e}")
            exit(1)

    def commit(self):
        if self.conn:
            self.conn.commit()

    def close(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()
           
