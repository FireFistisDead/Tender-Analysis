"""
PDF Processing Engine.
Hybrid extraction: PyMuPDF (native text) → Tesseract OCR (fallback for scanned PDFs).
"""

import fitz  # PyMuPDF
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class PageContent:
    """Content extracted from a single PDF page."""
    page_number: int
    text: str
    is_ocr: bool = False
    confidence: float = 1.0


@dataclass
class ProcessedDocument:
    """Full processed PDF document."""
    filename: str
    total_pages: int
    pages: List[PageContent] = field(default_factory=list)
    full_text: str = ""
    metadata: dict = field(default_factory=dict)

    def get_text_with_page_markers(self) -> str:
        """Return full text with [PAGE X] markers for traceability."""
        parts = []
        for page in self.pages:
            parts.append(f"\n[PAGE {page.page_number}]\n{page.text}")
        return "\n".join(parts)


class PDFProcessor:
    """
    Hybrid PDF processing engine.
    1. Attempts native text extraction via PyMuPDF (fast, high quality)
    2. Falls back to OCR via Tesseract for scanned/image-based pages
    """

    MIN_TEXT_LENGTH = 50  # Minimum chars to consider a page as having extractable text

    def __init__(self):
        self._ocr_available = self._check_ocr()

    def _check_ocr(self) -> bool:
        """Check if Tesseract OCR is available."""
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR is available")
            return True
        except Exception:
            logger.warning("Tesseract OCR is not available. Scanned PDFs will have limited text extraction.")
            return False

    def process(self, file_path: str) -> ProcessedDocument:
        """
        Process a PDF file and extract text from all pages.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            ProcessedDocument with extracted text and metadata
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        logger.info(f"Processing PDF: {path.name}")

        doc = fitz.open(file_path)
        processed = ProcessedDocument(
            filename=path.name,
            total_pages=len(doc),
            metadata={
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "creator": doc.metadata.get("creator", ""),
            }
        )

        for page_num in range(len(doc)):
            page = doc[page_num]
            page_content = self._extract_page(page, page_num + 1)
            processed.pages.append(page_content)

        doc.close()

        # Build full text
        processed.full_text = processed.get_text_with_page_markers()

        logger.info(
            f"Processed {processed.total_pages} pages from {path.name}. "
            f"Total text length: {len(processed.full_text)} chars"
        )

        return processed

    def _extract_page(self, page: fitz.Page, page_number: int) -> PageContent:
        """
        Extract text from a single page.
        Try native extraction first, fall back to OCR if text is sparse.
        """
        # Try native text extraction
        text = page.get_text("text").strip()

        if len(text) >= self.MIN_TEXT_LENGTH:
            return PageContent(
                page_number=page_number,
                text=text,
                is_ocr=False,
                confidence=1.0
            )

        # Text is too short — might be a scanned page
        if self._ocr_available:
            return self._ocr_page(page, page_number)

        # No OCR available, return whatever we got
        return PageContent(
            page_number=page_number,
            text=text if text else "[No extractable text found on this page]",
            is_ocr=False,
            confidence=0.1
        )

    def _ocr_page(self, page: fitz.Page, page_number: int) -> PageContent:
        """
        Perform OCR on a page by rendering it as an image.
        """
        try:
            import pytesseract
            from PIL import Image
            import io

            # Render page as high-res image (300 DPI)
            mat = fitz.Matrix(300 / 72, 300 / 72)
            pix = page.get_pixmap(matrix=mat)
            img_bytes = pix.tobytes("png")

            # OCR with Tesseract
            image = Image.open(io.BytesIO(img_bytes))
            ocr_data = pytesseract.image_to_data(image, lang="eng", output_type=pytesseract.Output.DICT)

            # Calculate average confidence
            confidences = [int(c) for c in ocr_data["conf"] if int(c) > 0]
            avg_confidence = sum(confidences) / len(confidences) / 100 if confidences else 0.0

            text = pytesseract.image_to_string(image, lang="eng").strip()

            logger.info(f"  Page {page_number}: OCR extracted {len(text)} chars (confidence: {avg_confidence:.2f})")

            return PageContent(
                page_number=page_number,
                text=text if text else "[OCR could not extract text from this page]",
                is_ocr=True,
                confidence=avg_confidence
            )

        except Exception as e:
            logger.error(f"  Page {page_number}: OCR failed - {e}")
            return PageContent(
                page_number=page_number,
                text="[OCR extraction failed for this page]",
                is_ocr=True,
                confidence=0.0
            )
