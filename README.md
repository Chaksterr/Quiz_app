# AI Quiz Generator

Generate interactive quizzes from PDF and PowerPoint documents using AI and RAG (Retrieval Augmented Generation).

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

## ⚡ Installation (3 commandes)

```bash
# 1. Installer uv (une seule fois)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Cloner et installer
git clone <your-repo-url>
cd quiz-generator
uv sync  # Installe tout automatiquement !

# 3. Configurer
cp .env.example .env
# Éditer .env avec vos credentials Azure OpenAI
```

**C'est tout !** `uv sync` crée le venv et installe toutes les dépendances en quelques secondes.

## 🚀 Démarrage

```bash
# Terminal 1 - Qdrant
docker run -d -p 6333:6333 --name qdrant qdrant/qdrant:latest

# Terminal 2 - Backend
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3 - Frontend
uv run streamlit run frontend/app.py --server.port 8501
```

**Accès:** http://localhost:8501 🎉

## ✨ Features

- 📄 **Document Support**: Upload PDF and PowerPoint files
- 🤖 **AI-Powered**: Generates questions using Azure OpenAI GPT
- 🔍 **Smart Search**: Vector search with Qdrant for relevant content
- 📊 **Instant Scoring**: Automatic grading with detailed explanations
- 📍 **Source References**: Each answer includes page/slide numbers
- 🔄 **Retake Quiz**: Practice with the same questions to improve
- 🎓 **AI Analysis**: Get personalized learning recommendations
- 🎯 **Adaptive**: Create 3-100 questions per quiz

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Frontend   │─────▶│   Backend    │─────▶│   Qdrant    │
│ (Streamlit) │      │  (FastAPI)   │      │  (Vectors)  │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │ Azure OpenAI │
                     │ GPT + Embed  │
                     └──────────────┘
```

**Components:**
- **Frontend**: Streamlit web interface
- **Backend**: FastAPI REST API
- **Vector DB**: Qdrant for semantic search
- **AI**: Azure OpenAI for embeddings and generation

## 🚀 Quick Start

> **Prérequis:** [uv](https://docs.astral.sh/uv/) (gestionnaire de paquets Python ultra-rapide)

Si `uv` n'est pas installé :
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# ou
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows
```

### Installation complète

### Installation complète

```bash
git clone <your-repo-url>
cd quiz-generator
uv sync  # Crée le venv + installe les dépendances
cp .env.example .env  # Configurer vos credentials Azure
```

### Lancement des services

### Lancement des services

```bash
# Qdrant (base de données vectorielle)
docker run -d -p 6333:6333 --name qdrant qdrant/qdrant:latest

# Backend (dans un terminal)
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (dans un autre terminal)
uv run streamlit run frontend/app.py --server.port 8501
```

### Accès

### Accès

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000/docs
- **Qdrant**: http://localhost:6333/dashboard

## 📖 Usage

1. **Upload Document**
   - Open http://localhost:8501
   - Upload a PDF or PPTX file
   - Enter a topic for the quiz
   - Select number of questions (3-100)

2. **Take Quiz**
   - Answer multiple-choice questions
   - Track progress in real-time
   - Submit when complete

3. **View Results**
   - See your score with emoji feedback
   - Review explanations for each question
   - Check source references (page/slide numbers)

4. **Improve**
   - **Retake Quiz**: Practice with same questions
   - **AI Analysis**: Get personalized study plan
   - **New Quiz**: Generate different questions

## 🎯 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/ingest` | POST | Upload and process document |
| `/quiz` | POST | Generate quiz questions |
| `/score` | POST | Score quiz answers |
| `/summarize` | POST | Get AI performance analysis |

## 📁 Project Structure

```
.
├── backend/
│   ├── generation/          # Quiz and summary generation
│   │   ├── llm.py          # Azure OpenAI chat wrapper
│   │   └── quiz.py         # Quiz generation logic
│   ├── ingestion/          # Document processing
│   │   ├── parser.py       # PDF/PPTX extraction
│   │   ├── chunker.py      # Semantic text chunking
│   │   └── store.py        # Vector storage
│   ├── retrieval/          # Search functionality
│   │   └── search.py       # Vector similarity search
│   ├── clients.py          # Azure & Qdrant clients
│   ├── config.py           # Configuration settings
│   ├── main.py             # FastAPI application
│   ├── models.py           # Pydantic models
│   └── requirements.txt    # Backend dependencies
├── frontend/
│   ├── .streamlit/         # Streamlit configuration
│   ├── app.py              # Streamlit UI
│   └── requirements.txt    # Frontend dependencies
├── .env.example            # Environment template
├── requirements.txt        # Root dependencies
└── README.md
```

## 📦 Using uv Package Manager

### Common Commands

```bash
# Install/sync dependencies
uv sync

# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Remove a dependency
uv remove package-name

# Run a command in the virtual environment
uv run python script.py
uv run uvicorn backend.main:app --reload

# Update dependencies
uv lock --upgrade

# Show installed packages
uv pip list
```

### Why uv?

- ⚡ **10-100x faster** than pip
- 🔒 **Deterministic** dependency resolution with `uv.lock`
- 🎯 **Single tool** for venv, pip, and pip-tools
- 📦 **Modern** pyproject.toml support
- 🔄 **Compatible** with existing Python projects

> **Important**: The `uv.lock` file is committed to git to ensure everyone installs the exact same dependency versions. When you clone the repo, just run `uv sync` and you're ready to go!

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | Required |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | Required |
| `AZURE_OPENAI_API_VERSION` | API version | 2025-04-01-preview |
| `AZURE_OPENAI_CHAT_MODEL` | Chat model name | o4-mini |
| `AZURE_OPENAI_EMBED_MODEL` | Embedding model | text-embedding-3-small |
| `QDRANT_HOST` | Qdrant host | localhost |
| `QDRANT_PORT` | Qdrant port | 6333 |
| `COLLECTION_NAME` | Vector collection name | quiz_docs |

## 🛠️ Advanced Features

### Document Processing

- **PDF Support**: Text extraction, table detection, page mapping
- **PPTX Support**: Slide text, tables, presenter notes
- **Error Handling**: Graceful handling of corrupted files
- **Validation**: Content verification before processing

### Quiz Generation

- **Semantic Chunking**: Intelligent text segmentation
- **Vector Search**: Find most relevant content
- **AI Generation**: Context-aware question creation
- **Page References**: Track source location for each question

### Scoring & Analysis

- **Instant Feedback**: Immediate scoring with explanations
- **Performance Tracking**: Score percentage with emoji indicators
- **AI Analysis**: Personalized learning recommendations
- **Study Plans**: Customized improvement strategies

## 🐛 Troubleshooting

### Qdrant Connection Issues
```bash
# Check if Qdrant is running
docker ps | grep qdrant

# Restart Qdrant
docker restart qdrant
```

### Backend Errors
```bash
# Check backend logs
cd backend
uvicorn main:app --reload --log-level debug
```

### Frontend Issues
```bash
# Clear Streamlit cache
streamlit cache clear

# Restart frontend
cd frontend
streamlit run app.py --server.port 8501
```

## 🧪 Testing

```bash
# Test backend health
curl http://localhost:8000/health

# Test Qdrant
curl http://localhost:6333/collections

# View API documentation
open http://localhost:8000/docs
```

## 📊 Performance

- **Document Processing**: ~2-5 seconds for typical documents
- **Quiz Generation**: ~5-15 seconds for 5 questions
- **Scoring**: Instant (<1 second)
- **AI Analysis**: ~10-20 seconds

## 🔒 Security Notes

- API keys stored in `.env` (not committed to git)
- CORS enabled for local development
- Input validation on all endpoints
- Error messages sanitized

## 🚦 Stopping Services

```bash
# Stop backend: Ctrl+C in backend terminal
# Stop frontend: Ctrl+C in frontend terminal

# Stop Qdrant
docker stop qdrant

# Remove Qdrant (including data)
docker rm -f qdrant
```

## 📝 License

MIT

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 📧 Support

For issues or questions, please open a GitHub issue.
