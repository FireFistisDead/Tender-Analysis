"""
Pydantic schemas for request/response models.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"


class Severity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ClauseStrength(str, Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    VAGUE = "vague"
    ABSENT = "absent"


# --- Response Models ---

class EnvironmentalClause(BaseModel):
    clause_text: str = Field(..., description="The extracted clause text")
    page: int = Field(..., description="Page number where clause was found")
    category: str = Field(..., description="Category (e.g., Waste Management, Energy Efficiency)")
    strength: ClauseStrength = Field(..., description="How specific/enforceable the clause is")
    sdg_alignment: List[str] = Field(default_factory=list, description="SDG targets this aligns with")


class SustainabilityCommitment(BaseModel):
    commitment: str = Field(..., description="The commitment text")
    page: int = Field(default=0, description="Page number")
    specificity: ClauseStrength = Field(..., description="How specific the commitment is")
    recommendation: str = Field(default="", description="Improvement recommendation")


class MissingRequirement(BaseModel):
    sdg_target: str = Field(..., description="SDG target ID (e.g., 11.6)")
    target_name: str = Field(default="", description="Short name of the target")
    description: str = Field(..., description="What the target requires")
    gap: str = Field(..., description="What's missing from the tender")
    severity: Severity = Field(..., description="How critical this gap is")
    recommendation: str = Field(default="", description="Suggested clause to add")


class RiskFlag(BaseModel):
    risk: str = Field(..., description="Description of the risk")
    severity: Severity = Field(..., description="Risk severity")
    page: Optional[int] = Field(default=None, description="Related page")
    mitigation: str = Field(default="", description="How to mitigate")


class AnalysisResult(BaseModel):
    upload_id: str
    filename: str
    total_pages: int = 0
    overall_sustainability_score: int = Field(0, ge=0, le=100)
    sdg11_score: int = Field(0, ge=0, le=100)
    sdg12_score: int = Field(0, ge=0, le=100)
    environmental_clauses: List[EnvironmentalClause] = Field(default_factory=list)
    sustainability_commitments: List[SustainabilityCommitment] = Field(default_factory=list)
    missing_requirements: List[MissingRequirement] = Field(default_factory=list)
    risk_flags: List[RiskFlag] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    executive_summary: str = ""
    status: ProcessingStatus = ProcessingStatus.PENDING


class UploadResponse(BaseModel):
    upload_id: str
    filename: str
    message: str
    status: ProcessingStatus


class StatusResponse(BaseModel):
    upload_id: str
    status: ProcessingStatus
    progress: int = Field(0, ge=0, le=100)
    message: str = ""


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Question about the tender")


class ChatResponse(BaseModel):
    answer: str
    source_pages: List[int] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
