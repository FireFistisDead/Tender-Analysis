"""
FastAPI application entry point.
Handles PDF upload, analysis, and chat endpoints.
"""

import uuid
import asyncio
import logging
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import UPLOAD_DIR, MAX_FILE_SIZE_MB, SUPPORTED_EXTENSIONS
from app.models.schemas import (
    UploadResponse, StatusResponse, AnalysisResult,
    ChatRequest, ChatResponse, ProcessingStatus
)
from app.services.pdf_processor import PDFProcessor
from app.services.rag_pipeline import RAGPipeline
from app.services.sdg_analyzer import SDGAnalyzer, ANALYSIS_QUERIES

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# --- App ---
app = FastAPI(
    title="Tender Sustainability Analyzer",
    description="AI-powered analysis of government tenders for SDG 11 & 12 compliance",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Singletons ---
pdf_processor = PDFProcessor()
rag_pipeline = RAGPipeline()
sdg_analyzer = SDGAnalyzer()

# --- In-memory state ---
analysis_store: Dict[str, AnalysisResult] = {}
status_store: Dict[str, StatusResponse] = {}


@app.on_event("startup")
async def startup_event():
    """Initialize SDG knowledge base on startup."""
    logger.info("Starting Tender Sustainability Analyzer...")
    try:
        rag_pipeline.initialize_sdg_knowledge()
        logger.info("SDG knowledge base ready")
    except Exception as e:
        logger.error(f"Failed to initialize SDG knowledge: {e}")


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "Tender Sustainability Analyzer"}


@app.post("/api/upload", response_model=UploadResponse)
async def upload_tender(file: UploadFile = File(...)):
    """Upload a tender PDF for analysis."""
    # Validate file
    if not file.filename:
        raise HTTPException(400, "No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: {ext}. Only PDF files are supported.")

    # Read and check size
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(400, f"File too large: {size_mb:.1f}MB (max {MAX_FILE_SIZE_MB}MB)")

    # Save file
    upload_id = str(uuid.uuid4())[:8]
    save_path = UPLOAD_DIR / f"{upload_id}_{file.filename}"
    with open(save_path, "wb") as f:
        f.write(content)

    # Set initial status
    status_store[upload_id] = StatusResponse(
        upload_id=upload_id,
        status=ProcessingStatus.PROCESSING,
        progress=10,
        message="PDF uploaded, starting processing..."
    )

    # Start async processing
    asyncio.create_task(process_tender(upload_id, str(save_path), file.filename))

    return UploadResponse(
        upload_id=upload_id,
        filename=file.filename,
        message="Upload successful. Processing started.",
        status=ProcessingStatus.PROCESSING
    )


async def process_tender(upload_id: str, file_path: str, filename: str):
    """Background task to process and analyze a tender."""
    try:
        # Step 1: Extract text from PDF
        status_store[upload_id].progress = 20
        status_store[upload_id].message = "Extracting text from PDF..."
        processed = await asyncio.to_thread(pdf_processor.process, file_path)

        # Step 2: Index in ChromaDB
        status_store[upload_id].progress = 40
        status_store[upload_id].message = "Building document index..."
        await asyncio.to_thread(
            rag_pipeline.index_tender,
            upload_id, processed.full_text, filename
        )

        # Step 3: Retrieve relevant context
        status_store[upload_id].progress = 60
        status_store[upload_id].message = "Retrieving relevant sections..."
        tender_context = await asyncio.to_thread(
            rag_pipeline.retrieve_tender_context,
            upload_id, ANALYSIS_QUERIES
        )
        sdg_context = await asyncio.to_thread(
            rag_pipeline.retrieve_sdg_context,
            ANALYSIS_QUERIES
        )

        # Step 4: LLM Analysis
        status_store[upload_id].progress = 80
        status_store[upload_id].message = "AI analyzing sustainability compliance..."
        result = await asyncio.to_thread(
            sdg_analyzer.analyze,
            upload_id, filename, processed.total_pages,
            tender_context, sdg_context
        )

        # Store result
        analysis_store[upload_id] = result
        status_store[upload_id] = StatusResponse(
            upload_id=upload_id,
            status=ProcessingStatus.COMPLETE,
            progress=100,
            message="Analysis complete!"
        )
        logger.info(f"Analysis complete for {upload_id}: score={result.overall_sustainability_score}")

    except Exception as e:
        logger.error(f"Processing failed for {upload_id}: {e}")
        status_store[upload_id] = StatusResponse(
            upload_id=upload_id,
            status=ProcessingStatus.ERROR,
            progress=0,
            message=f"Processing failed: {str(e)}"
        )


@app.get("/api/status/{upload_id}", response_model=StatusResponse)
async def get_status(upload_id: str):
    """Check processing status."""
    if upload_id not in status_store:
        raise HTTPException(404, "Upload not found")
    return status_store[upload_id]


@app.get("/api/analysis/{upload_id}", response_model=AnalysisResult)
async def get_analysis(upload_id: str):
    """Get full analysis results."""
    if upload_id not in analysis_store:
        if upload_id in status_store:
            status = status_store[upload_id]
            if status.status == ProcessingStatus.PROCESSING:
                raise HTTPException(202, "Analysis still in progress")
            elif status.status == ProcessingStatus.ERROR:
                raise HTTPException(500, status.message)
        raise HTTPException(404, "Analysis not found")
    return analysis_store[upload_id]


@app.post("/api/analysis/{upload_id}/chat", response_model=ChatResponse)
async def chat_with_tender(upload_id: str, request: ChatRequest):
    """Chat with an analyzed tender document."""
    if upload_id not in analysis_store:
        raise HTTPException(404, "Analysis not found. Upload and analyze a tender first.")

    context_docs = await asyncio.to_thread(
        rag_pipeline.chat_with_tender,
        upload_id, request.question
    )

    if not context_docs:
        return ChatResponse(
            answer="I couldn't find relevant information in the tender document.",
            source_pages=[],
            confidence=0.0
        )

    result = await asyncio.to_thread(
        sdg_analyzer.chat,
        request.question, context_docs
    )

    return ChatResponse(**result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
