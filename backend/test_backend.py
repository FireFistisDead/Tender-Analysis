"""Quick test script to verify all backend imports work."""
import sys
sys.path.insert(0, ".")

print("Testing imports...")

from app.config import UPLOAD_DIR, CHROMA_PERSIST_DIR, KNOWLEDGE_DIR
print(f"  Config OK: uploads={UPLOAD_DIR}, chroma={CHROMA_PERSIST_DIR}")

from app.models.schemas import AnalysisResult, UploadResponse
print("  Models OK")

from app.services.pdf_processor import PDFProcessor
print("  PDF Processor OK")

from app.services.rag_pipeline import RAGPipeline
print("  RAG Pipeline OK")

from app.services.sdg_analyzer import SDGAnalyzer
print("  SDG Analyzer OK")

# Test PDF processor with sample
import os
sample_dir = os.path.join("sample_tenders")
if os.path.exists(sample_dir):
    files = os.listdir(sample_dir)
    print(f"  Sample tenders found: {files}")
    
    proc = PDFProcessor()
    for f in files:
        path = os.path.join(sample_dir, f)
        doc = proc.process(path)
        print(f"    {f}: {doc.total_pages} pages, {len(doc.full_text)} chars extracted")

print("\nAll backend tests passed!")
