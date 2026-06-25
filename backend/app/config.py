"""
Configuration module for the Tender Sustainability Analyzer.
Loads environment variables and provides app-wide settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads")))
CHROMA_PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "chroma_db")))
KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge"
SAMPLE_TENDERS_DIR = BASE_DIR / "sample_tenders"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_TENDERS_DIR.mkdir(parents=True, exist_ok=True)

# --- AI Model Settings ---
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# --- Processing Settings ---
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_FILE_SIZE_MB = 50
SUPPORTED_EXTENSIONS = {".pdf"}

# --- RAG Settings ---
TOP_K_RESULTS = 5
COLLECTION_NAME = "tender_documents"
SDG_COLLECTION_NAME = "sdg_knowledge"
