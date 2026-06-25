# 🌿 TenderGreen AI — Tender Sustainability Analyzer

**AI-Powered analysis of government tenders for SDG 11 & SDG 12 compliance**

Upload a government tender PDF → AI extracts environmental clauses, evaluates sustainability commitments, and identifies missing SDG requirements with a visual compliance scorecard.

## 🎯 SDG Focus

- **SDG 11** — Sustainable Cities and Communities
- **SDG 12** — Responsible Consumption and Production

## 🏗️ Architecture

```
Frontend (Next.js) → FastAPI Backend → PDF Processor → RAG Pipeline → Gemini LLM
                                        ↑                  ↑
                                    PyMuPDF/OCR      ChromaDB + HuggingFace
```

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 Smart PDF Extraction | Hybrid OCR + native text extraction |
| 🤖 RAG Analysis | Grounded analysis using actual tender text |
| 🎯 SDG Gap Detection | Identifies missing sustainability requirements |
| 📊 Visual Scorecard | Interactive radar charts for SDG coverage |
| 💬 Chat with Tender | Ask questions about your tender document |
| 📋 Recommendations | Actionable clause suggestions for gaps |

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ (conda env: `rl_env`)
- Node.js 18+
- Google Gemini API key (free from [Google AI Studio](https://aistudio.google.com/))

### 1. Backend Setup

```bash
cd backend

# Set your API key
# Edit .env and replace 'your_gemini_api_key_here' with your actual key
notepad .env

# Install dependencies (if not already done)
conda activate rl_env
pip install -r requirements.txt

# Start the server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies (if not already done)
npm install

# Start dev server
npm run dev
```

### 3. Open the App

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📂 Project Structure

```
internship_2/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Environment config
│   │   ├── models/schemas.py    # Pydantic models
│   │   ├── services/
│   │   │   ├── pdf_processor.py # PDF extraction engine
│   │   │   ├── rag_pipeline.py  # RAG + ChromaDB
│   │   │   └── sdg_analyzer.py  # Gemini LLM analysis
│   │   └── knowledge/           # SDG knowledge base JSONs
│   ├── sample_tenders/          # Sample tender PDFs
│   ├── .env                     # API keys (gitignored)
│   └── requirements.txt
├── frontend/
│   ├── src/app/
│   │   ├── page.tsx             # Landing page
│   │   ├── analyze/page.tsx     # Upload + Dashboard
│   │   └── globals.css          # Design system
│   └── src/lib/
│       ├── api.ts               # Backend API client
│       └── types.ts             # TypeScript interfaces
└── README.md
```

## 🧪 Sample Tenders

Two sample tenders are included for testing:
1. **Highway Construction** — MORTH NH-48 (moderate sustainability)
2. **Smart City ICCC** — Mumbai Smart City (better sustainability)

Generate them:
```bash
cd backend
conda activate rl_env
python generate_sample_tenders.py
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload tender PDF |
| GET | `/api/status/{id}` | Check processing status |
| GET | `/api/analysis/{id}` | Get full analysis results |
| POST | `/api/analysis/{id}/chat` | Chat with tender |
| GET | `/api/health` | Health check |

## 🔧 Tech Stack

- **Frontend**: Next.js 16, React 19, TypeScript, Recharts, Vanilla CSS
- **Backend**: FastAPI, Python 3.10
- **AI**: Google Gemini 2.0 Flash, LangChain, ChromaDB, HuggingFace sentence-transformers
- **PDF**: PyMuPDF, pdfplumber, Tesseract OCR (optional)
