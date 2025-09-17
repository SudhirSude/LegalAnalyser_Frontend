from fastapi import APIRouter
import uuid
import os

from ..schemas import UploadResponse
from ..document_io import generate_signed_upload_url

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("", response_model=UploadResponse)
async def create_upload():
    session_id = str(uuid.uuid4())
    object_name = f"sessions/{session_id}/document.pdf"
    url = generate_signed_upload_url(object_name)
    return {"upload_url": url, "object_name": object_name}
