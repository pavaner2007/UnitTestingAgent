# AutoQA Agent

AutoQA Agent is a production-ready AI-powered repository analysis system. It accepts a GitHub repository URL, clones the repository, detects the technology stack, discovers API endpoints, and generates a structured JSON report.

This version focuses on:

- Repository analysis
- Tech stack detection
- API endpoint discovery
- JSON report generation

It intentionally does **not** include UI testing, security testing, performance testing, or multi-agent orchestration yet.

## Tech Stack

- Backend: FastAPI, Python
- Frontend: React, Vite, TailwindCSS
- Database: PostgreSQL
- AI Layer: LangChain-ready pluggable LLM architecture
- Version Control: GitHub

## Folder Structure

```text
AutoQA_Agent/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
├── database/
│   └── init.sql
├── reports/
├── repositories/
└── README.md
```

## Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux
uvicorn app.main:app --reload
```

Backend will run at:

```text
http://localhost:8000
```

API docs:

```text
http://localhost:8000/docs
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will run at:

```text
http://localhost:5173
```

## PostgreSQL Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE autoqa_agent;
```

Then run:

```bash
psql -U postgres -d autoqa_agent -f database/init.sql
```

Set this in `backend/.env`:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/autoqa_agent
```

## API Endpoints

### Health Check

```http
GET /health
```

Response:

```json
{
  "status": "healthy",
  "service": "AutoQA Agent"
}
```

### Analyze Repository

```http
POST /analyze-repository
Content-Type: application/json

{
  "github_url": "https://github.com/user/repository"
}
```

Response:

```json
{
  "analysis_id": "uuid",
  "status": "completed",
  "report": {}
}
```

### Get Analysis

```http
GET /analysis/{id}
```

## Example Report

```json
{
  "repository_name": "sample-api",
  "repository_url": "https://github.com/user/sample-api",
  "metadata": {
    "default_branch": "main",
    "local_path": "repositories/sample-api"
  },
  "technology_stack": {
    "frontend": ["React"],
    "backend": ["FastAPI"],
    "languages": ["Python", "JavaScript"],
    "databases": ["PostgreSQL"]
  },
  "project_structure_summary": {
    "directories": 12,
    "files": 40,
    "top_level_items": ["backend", "frontend", "README.md"]
  },
  "number_of_files": 40,
  "number_of_apis_discovered": 3,
  "api_inventory": []
}
```

## LLM Provider Architecture

The backend contains a pluggable LLM provider interface under:

```text
backend/app/services/llm_service.py
```

Current mode uses a safe no-op provider because the repository analysis is deterministic. Later you can plug in:

- DeepSeek
- Qwen
- Gemini
- OpenAI

without changing the API layer.

## Notes

- Make sure Git is installed on your machine.
- Repositories are cloned into the root `repositories/` folder by default.
- Reports are stored as JSON files in the root `reports/` folder and also persisted in PostgreSQL.
