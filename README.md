# LLM4Grey
## An LLM-based System for Grey Literature Screening

## ✅ Requirements

- [Docker](https://www.docker.com/) (tested with Docker Engine 24+)
- [Docker Compose](https://docs.docker.com/compose/) (v2+)
- [Python 3.13.2](https://www.python.org/downloads/release/python-3132/)


## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/seu-usuario/LLM4Grey.git
cd LLM4Grey
```

### 2. Create and activate virtual environment

```bash
python3.13 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate.bat    # Windows
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
A sample environment file is provided. Rename `.env-example` to `.env`, then, open the .env file and fill in your configuration

OPENAI_TOKEN=
GEMINI_TOKEN=
CLAUDE_TOKEN=
LHAMA_TOKEN=
DEEPSEEK_TOKEN=
GROK_TOKEN=
POSTGRES_DB=
POSTGRES_HOST=localhost
POSTGRES_PORT=5555
POSTGRES_USER=
POSTGRES_PASSWORD=

### 5. Start the database with Docker
```bash
sudo docker compose up -d
```

- PostgreSQL with pgvector extension


### 6. Run the CLI interface
```bash
python src/main.py
```
