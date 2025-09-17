from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import upload, process, query

app = FastAPI(title="Legal Demystifier Backend", version="0.1.0")

# NOTE: restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "Legal Demystifier backend running"}

# include routers
app.include_router(upload.router)
app.include_router(process.router)
app.include_router(query.router)
