import os
from dotenv import load_dotenv

load_dotenv()
load_dotenv(dotenv_path=".env", override=True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROMPT_DIR = os.path.join(BASE_DIR, "prompts")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(BASE_DIR, "raw_data", "dump")
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")

DISCUSSIONS_FILE = os.path.join(BASE_DIR, "raw_data", "discussions.txt")
INCLUDED_FILE = os.path.join(BASE_DIR, "raw_data", "included.txt")

os.makedirs(DATASETS_DIR, exist_ok=True)

FILE_MAPPINGS = {
    "Posts.xml": ("Posts", [
        "Id", "PostTypeId", "AcceptedAnswerId", "ParentId", "CreationDate", "Score",
        "ViewCount", "Body", "OwnerUserId", "LastEditorUserId", "LastEditorDisplayName",
        "LastEditDate", "LastActivityDate", "Title", "Tags", "AnswerCount", "CommentCount",
        "FavoriteCount", "ClosedDate", "CommunityOwnedDate"
    ]),
    "Comments.xml": ("Comments", [
        "Id", "PostId", "Score", "Text", "CreationDate", "UserId"
    ]),
    "Users.xml": ("Users", [
        "Id", "Reputation", "CreationDate", "DisplayName", "LastAccessDate",
        "WebsiteUrl", "Location", "AboutMe", "Views", "UpVotes", "DownVotes",
        "ProfileImageUrl", "Age", "AccountId"
    ]),
}

# Número máximo de requisições antes de uma pausa (para modelos com `rate_limit=True`)
RATE_LIMIT_THRESHOLD = 5  

LLM_MODELS = {
    "GPT-4o": {
        "file": "gpt_4o",
        "api_key": os.getenv("OPENAI_TOKEN"),
        "rate_limit": False
    },
    "Gemini 2.0 Flash": {
        "file": "gemini_2_0",
        "api_key": os.getenv("GEMINI_TOKEN"),
        "rate_limit": True
    },
    "Claude 3.5 Sonnet": {
        "file": "claude_3_5",
        "api_key": os.getenv("CLAUDE_TOKEN"),
        "rate_limit": False
    },
    "Grok 2": {
        "file": "grok_2",
        "api_key": os.getenv("GROK_TOKEN"),
        "rate_limit": False
    },
    "Deepseek R1": {
        "file": "deepseek_r1",
        "api_key": os.getenv("DEEPSEEK_TOKEN"),
        "rate_limit": False
    },
    "Llama 3.1 405b": {
        "file": "llama_3_1",
        "api_key": os.getenv("LHAMA_TOKEN"),
        "rate_limit": False
    },
}

for model_name, details in LLM_MODELS.items():
    if not details["api_key"]:
        #print(f"Aviso: Token de API para {model_name} ({details['file']}.py) não foi encontrado no arquivo .env!")
        pass



if os.path.exists(PROMPT_DIR):
    PROMPT_TECHNIQUES = [folder for folder in os.listdir(PROMPT_DIR) if os.path.isdir(os.path.join(PROMPT_DIR, folder))]
else:
    PROMPT_TECHNIQUES = []
