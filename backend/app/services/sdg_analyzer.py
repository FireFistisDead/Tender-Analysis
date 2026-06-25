"""
SDG Analyzer - Uses Google Gemini LLM to analyze tender documents
for sustainability compliance against SDG 11 and SDG 12.
"""

import json
import logging
from typing import List, Optional

from langchain.schema import Document

from app.config import OLLAMA_BASE_URL, MODEL_NAME
from app.models.schemas import (
    AnalysisResult, EnvironmentalClause, SustainabilityCommitment,
    MissingRequirement, RiskFlag, ClauseStrength, Severity, ProcessingStatus
)

logger = logging.getLogger(__name__)

# Analysis queries for RAG retrieval
ANALYSIS_QUERIES = [
    "environmental protection clauses and requirements",
    "sustainability commitments and green procurement criteria",
    "waste management and resource efficiency requirements",
    "energy efficiency and carbon emissions standards",
    "urban planning and infrastructure sustainability",
    "compliance certifications ISO 14001 GRIHA BEE rating",
    "air quality monitoring and pollution control",
    "recycling reuse circular economy requirements",
    "water conservation and management",
    "hazardous waste chemical management disposal",
]


class SDGAnalyzer:
    """Analyzes tender documents for SDG 11 & 12 compliance using Gemini LLM."""

    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from langchain_community.chat_models import ChatOllama
            self._model = ChatOllama(
                model=MODEL_NAME,
                base_url=OLLAMA_BASE_URL,
                temperature=0.1
            )
        return self._model

    def analyze(
        self,
        upload_id: str,
        filename: str,
        total_pages: int,
        tender_context: List[Document],
        sdg_context: List[Document]
    ) -> AnalysisResult:
        """Run full SDG sustainability analysis on a tender."""
        logger.info(f"Analyzing tender {upload_id} with {len(tender_context)} chunks")

        tender_text = "\n\n---\n\n".join(
            [doc.page_content for doc in tender_context]
        )
        sdg_text = "\n\n---\n\n".join(
            [doc.page_content for doc in sdg_context]
        )

        prompt = self._build_analysis_prompt(tender_text, sdg_text)

        try:
            response = self.model.invoke(prompt)
            result_data = self._parse_response(response.content)
            result = self._build_result(upload_id, filename, total_pages, result_data)
            return result
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return AnalysisResult(
                upload_id=upload_id,
                filename=filename,
                total_pages=total_pages,
                status=ProcessingStatus.ERROR,
                executive_summary=f"Analysis failed: {str(e)}"
            )

    def chat(self, question: str, context_docs: List[Document]) -> dict:
        """Answer a question about a tender using retrieved context."""
        context = "\n\n".join([doc.page_content for doc in context_docs])
        pages = list(set(
            doc.metadata.get("page", 0) for doc in context_docs if doc.metadata.get("page", 0) > 0
        ))

        prompt = (
            "You are an expert procurement analyst. Answer the question "
            "based ONLY on the tender document context below.\n\n"
            f"TENDER CONTEXT:\n{context}\n\n"
            f"QUESTION: {question}\n\n"
            "Provide a clear, specific answer. If the information is not "
            "found in the context, say so explicitly."
        )

        try:
            response = self.model.invoke(prompt)
            return {
                "answer": response.content,
                "source_pages": sorted(pages),
                "confidence": 0.85
            }
        except Exception as e:
            return {
                "answer": f"Error generating answer: {str(e)}",
                "source_pages": [],
                "confidence": 0.0
            }

    def _build_analysis_prompt(self, tender_text: str, sdg_text: str) -> str:
        return f"""You are an expert sustainability analyst specializing in government procurement and SDG compliance. Analyze the following tender document against SDG 11 (Sustainable Cities and Communities) and SDG 12 (Responsible Consumption and Production).

## SDG REFERENCE KNOWLEDGE:
{sdg_text}

## TENDER DOCUMENT EXTRACTS:
{tender_text}

## ANALYSIS INSTRUCTIONS:
Perform a thorough analysis and return a JSON object with this EXACT structure:

{{
  "overall_sustainability_score": <0-100 integer>,
  "sdg11_score": <0-100 integer>,
  "sdg12_score": <0-100 integer>,
  "executive_summary": "<2-3 paragraph summary of sustainability posture>",
  "environmental_clauses": [
    {{
      "clause_text": "<exact or paraphrased clause>",
      "page": <page number or 0>,
      "category": "<Waste Management|Energy Efficiency|Air Quality|Water Management|Material Sourcing|Emissions|Biodiversity|Other>",
      "strength": "<strong|moderate|vague>",
      "sdg_alignment": ["<target IDs like 11.6, 12.5>"]
    }}
  ],
  "sustainability_commitments": [
    {{
      "commitment": "<commitment text>",
      "page": <page number or 0>,
      "specificity": "<strong|moderate|vague>",
      "recommendation": "<how to strengthen>"
    }}
  ],
  "missing_requirements": [
    {{
      "sdg_target": "<e.g., 11.6>",
      "target_name": "<target name>",
      "description": "<what the target requires>",
      "gap": "<what's missing>",
      "severity": "<high|medium|low>",
      "recommendation": "<specific clause text to add>"
    }}
  ],
  "risk_flags": [
    {{
      "risk": "<description>",
      "severity": "<high|medium|low>",
      "page": <page or null>,
      "mitigation": "<how to address>"
    }}
  ],
  "recommendations": [
    "<actionable recommendation strings>"
  ]
}}

IMPORTANT:
- Score 0-30 = Poor sustainability, 31-60 = Moderate, 61-80 = Good, 81-100 = Excellent
- Be specific about page numbers when possible
- Include ALL relevant SDG targets from 11.1-11.c and 12.1-12.c
- Flag missing requirements with HIGH severity if they are legally mandated
- Return ONLY valid JSON, no markdown code blocks"""

    def _parse_response(self, content: str) -> dict:
        """Parse LLM response, handling markdown code blocks and reasoning tags."""
        import re
        text = content.strip()
        
        # Strip out <think>...</think> tags generated by DeepSeek-R1 models
        text = re.sub(r'<think>[\s\S]*?</think>', '', text).strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = lines[1:]  # Remove opening ```json
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON in the response
            import re
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            logger.error(f"Failed to parse LLM response as JSON")
            return {}

    def _build_result(self, upload_id: str, filename: str,
                      total_pages: int, data: dict) -> AnalysisResult:
        """Build AnalysisResult from parsed LLM output."""
        clauses = []
        for c in data.get("environmental_clauses", []):
            try:
                clauses.append(EnvironmentalClause(
                    clause_text=c.get("clause_text", ""),
                    page=c.get("page", 0),
                    category=c.get("category", "Other"),
                    strength=ClauseStrength(c.get("strength", "vague")),
                    sdg_alignment=c.get("sdg_alignment", [])
                ))
            except Exception:
                pass

        commitments = []
        for s in data.get("sustainability_commitments", []):
            try:
                commitments.append(SustainabilityCommitment(
                    commitment=s.get("commitment", ""),
                    page=s.get("page", 0),
                    specificity=ClauseStrength(s.get("specificity", "vague")),
                    recommendation=s.get("recommendation", "")
                ))
            except Exception:
                pass

        missing = []
        for m in data.get("missing_requirements", []):
            try:
                missing.append(MissingRequirement(
                    sdg_target=m.get("sdg_target", ""),
                    target_name=m.get("target_name", ""),
                    description=m.get("description", ""),
                    gap=m.get("gap", ""),
                    severity=Severity(m.get("severity", "medium")),
                    recommendation=m.get("recommendation", "")
                ))
            except Exception:
                pass

        risks = []
        for r in data.get("risk_flags", []):
            try:
                risks.append(RiskFlag(
                    risk=r.get("risk", ""),
                    severity=Severity(r.get("severity", "medium")),
                    page=r.get("page"),
                    mitigation=r.get("mitigation", "")
                ))
            except Exception:
                pass

        return AnalysisResult(
            upload_id=upload_id,
            filename=filename,
            total_pages=total_pages,
            overall_sustainability_score=data.get("overall_sustainability_score", 0),
            sdg11_score=data.get("sdg11_score", 0),
            sdg12_score=data.get("sdg12_score", 0),
            environmental_clauses=clauses,
            sustainability_commitments=commitments,
            missing_requirements=missing,
            risk_flags=risks,
            recommendations=data.get("recommendations", []),
            executive_summary=data.get("executive_summary", ""),
            status=ProcessingStatus.COMPLETE
        )
