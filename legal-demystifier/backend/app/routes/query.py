from fastapi import APIRouter, HTTPException
from typing import Dict
from ..rag_client import VertexRAGClient

router = APIRouter(prefix="/query", tags=["query"])
rag = VertexRAGClient()


@router.post("")
async def query_doc(req: Dict):
    question = req.get("question")
    rag_corpus = req.get("rag_corpus")
    if not question or not rag_corpus:
        raise HTTPException(status_code=400, detail="Missing rag_corpus or question")
    resp = rag.query_rag(rag_corpus, question)
    return resp
