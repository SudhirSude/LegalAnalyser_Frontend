import os
from google.cloud import storage
from datetime import timedelta

GCS_BUCKET = os.getenv("GCS_BUCKET", None)
if not GCS_BUCKET:
    raise RuntimeError("GCS_BUCKET environment variable not set")

storage_client = storage.Client()


def generate_signed_upload_url(object_name: str, expires_minutes: int = 15):
    """
    Generate a V4 signed PUT URL for uploading the document to GCS.
    """
    bucket = storage_client.bucket(GCS_BUCKET)
    blob = bucket.blob(object_name)
    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expires_minutes),
        method="PUT",
        content_type="application/pdf",
    )
    return url


def delete_blob(object_name: str):
    bucket = storage_client.bucket(GCS_BUCKET)
    blob = bucket.blob(object_name)
    blob.delete(if_generation_match=None)
