from fastapi import APIRouter, HTTPException
import uuid
import os
from typing import Dict

from ..schemas import ProcessRequest, DocumentSummary
from ..rag_client import VertexRAGClient

router = APIRouter(prefix="/process", tags=["process"])
rag = VertexRAGClient()


@router.post("", response_model=DocumentSummary)
async def process_doc(req: ProcessRequest):
    if not req.object_name:
        raise HTTPException(status_code=400, detail="object_name required")
    session_id = req.session_id or "sess-" + str(uuid.uuid4())
    gcs_uri = f"gs://{os.getenv('GCS_BUCKET')}/{req.object_name}"
    rag_corpus = rag.create_session_rag_corpus(gcs_uri, session_id)
    structured = rag.summarize_document(rag_corpus)
    return structured
