import os
import glob
import lxml.etree as ET
from bs4 import BeautifulSoup

class XMLReader:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(__file__))
        self.xml_dir = os.path.join(self.project_root, "raw_data", "dump")

    def get_files(self):
        return glob.glob(os.path.join(self.xml_dir, "*.xml"))

    def clean_text(self, text):
        if not text:
            return ""
        return BeautifulSoup(text, "html.parser").get_text().replace("\n", " ").strip()

    def parse_xml(self, file_path, columns):
        """
            file_path (str): Caminho do arquivo XML.
            columns (list): Lista das colunas a serem extraídas.
        """
        data = []
        try:
            context = ET.iterparse(file_path, events=("start",), encoding="utf-8")

            for _, elem in context:
                if elem.tag == "row":
                    row_data = {}
                    for col in columns:
                        value = elem.get(col)
                        if col in ["Body", "Title"]: 
                            row_data[col] = self.clean_text(value)
                        else:
                            row_data[col] = value
                    data.append(row_data)
                    elem.clear()

        except Exception as e:
            print(f"❌ Erro ao processar {file_path}: {e}")

        return data
