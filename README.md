# Quiz Generator

AI-powered quiz generator that creates questions from PDF and PPTX documents using RAG (Retrieval Augmented Generation).

## Features

- 📄 Upload PDF and PowerPoint files
- 🤖 AI-generated quiz questions
- 🔍 Vector search with Qdrant
- 📊 Automatic scoring and explanations

## Architecture

- **Backend**: FastAPI + Qdrant vector database
- **Frontend**: Streamlit
- **AI**: Azure OpenAI GPT + Sentence Transformers

## Prerequisites

- Python 3.12+
- Docker (for Qdrant vector database)
- Azure OpenAI API access with credentials

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <repo-name>
```

### 2. Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your Azure OpenAI credentials:
```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_API_VERSION=2025-04-01-preview
AZURE_OPENAI_CHAT_MODEL=o4-mini
AZURE_OPENAI_EMBED_MODEL=text-embedding-3-small
```

### 5. Start Qdrant vector database

```bash
docker run -d -p 6333:6333 -p 6334:6334 --name qdrant qdrant/qdrant:latest
```

### 6. Start the backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Start the frontend (in a new terminal)

```bash
source .venv/bin/activate
cd frontend
streamlit run app.py --server.port 8501
```

## Access the Application

- **Frontend (Streamlit)**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

## API Endpoints

- `POST /ingest` - Upload and process documents
- `POST /quiz` - Generate quiz questions
- `POST /score` - Score quiz answers
- `GET /health` - Health check

## Usage

1. Open the frontend at http://localhost:8501
2. Upload a PDF or PPTX file
3. Enter a topic for the quiz
4. Generate and answer quiz questions
5. Submit to see your score and explanations

## Stopping the Application

To stop the backend and frontend, press `Ctrl+C` in their respective terminals.

To stop Qdrant:
```bash
docker stop qdrant
```

To remove Qdrant (including data):
```bash
docker rm -f qdrant
```

## Project Structure

```
.
├── backend/
│   ├── generation/      # Quiz generation logic
│   ├── ingestion/       # Document parsing and chunking
│   ├── retrieval/       # Vector search
│   ├── clients.py       # Azure OpenAI and Qdrant clients
│   ├── config.py        # Configuration settings
│   ├── main.py          # FastAPI application
│   └── models.py        # Pydantic models
├── frontend/
│   └── app.py           # Streamlit UI
├── .env.example         # Environment variables template
├── requirements.txt     # Python dependencies
└── README.md
```

## License

MIT
