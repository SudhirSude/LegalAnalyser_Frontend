from pydantic import BaseModel
from typing import Optional, List, Dict


class UploadResponse(BaseModel):
    upload_url: str
    object_name: str


class ProcessRequest(BaseModel):
    object_name: str
    session_id: Optional[str] = None


class Clause(BaseModel):
    original: str
    simplified: str
    risk: str
    score: float
    provenance: List[Dict]


class DocumentSummary(BaseModel):
    title: Optional[str] = None
    summary: str
    overall_risk_score: float
    rag_corpus_name: Optional[str] = None
    clauses: List[Clause]
