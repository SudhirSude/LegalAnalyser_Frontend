import os
import time
import json
import logging
from typing import List, Dict, Any, Optional

# Vertex SDK per quickstart
import vertexai
from vertexai import rag
from vertexai.generative_models import GenerativeModel, Tool

from .utils import safe_parse_json, make_clause_provenance

logger = logging.getLogger(__name__)

PROJECT = os.getenv("GCP_PROJECT")
REGION = os.getenv("GCP_REGION", "us-central1")
# Choose a Gemini model available in your project/region (change if needed)
DEFAULT_MODEL = os.getenv("RAG_MODEL", "gemini-1.5-pro")  # or "gemini-2.0-flash-001"
EMBEDDING_PUBLISHER_MODEL = os.getenv("EMBEDDING_MODEL", "publishers/google/models/text-embedding-003")  # example


class VertexRAGClient:
    def __init__(self):
        if not PROJECT:
            raise RuntimeError("GCP_PROJECT env var not set")
        logger.info("Initializing Vertex AI for project=%s region=%s", PROJECT, REGION)
        vertexai.init(project=PROJECT, location=REGION)

    def create_session_rag_corpus(self, gcs_uri: str, session_id: str, display_name: Optional[str] = None) -> str:
        """
        Create a RAG corpus and import the file from GCS.
        Returns rag_corpus.name string.
        """
        display_name = display_name or f"corpus_{session_id}"
        logger.info("Creating rag corpus %s and importing %s", display_name, gcs_uri)

        # Configure embedding model for RAG (use the Vertex embedding endpoint)
        embedding_model_config = rag.RagEmbeddingModelConfig(
            vertex_prediction_endpoint=rag.VertexPredictionEndpoint(publisher_model=EMBEDDING_PUBLISHER_MODEL)
        )

        rag_corpus = rag.create_corpus(
            display_name=display_name,
            backend_config=rag.RagVectorDbConfig(rag_embedding_model_config=embedding_model_config),
        )

        # import the file from GCS
        rag.import_files(
            rag_corpus.name,
            [gcs_uri],
            transformation_config=rag.TransformationConfig(
                chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
            ),
            # optional throttle parameter
            max_embedding_requests_per_min=1000,
        )

        # the import is asynchronous; you can list files or poll
        # For simplicity, wait briefly for indexing (production: poll rag.list_files())
        logger.info("Waiting for corpus import/indexing (sleeping 6s)...")
        time.sleep(6)

        logger.info("Created rag_corpus: %s", rag_corpus.name)
        return rag_corpus.name

    def _make_rag_retrieval_tool(self, rag_corpus_name: str, top_k: int = 4) -> Tool:
        """
        Return a Tool that wraps retrieval from the rag corpus. The Tool can be provided to a GenerativeModel.
        """
        rag_retrieval_config = rag.RagRetrievalConfig(top_k=top_k)
        retrieval = rag.Retrieval(
            source=rag.VertexRagStore(
                rag_resources=[rag.RagResource(rag_corpus=rag_corpus_name)],
                rag_retrieval_config=rag_retrieval_config,
            )
        )
        rag_retrieval_tool = Tool.from_retrieval(retrieval=retrieval)
        return rag_retrieval_tool

    def summarize_document(self, rag_corpus_name: str) -> Dict[str, Any]:
        """
        Ask the model to produce a structured JSON summary with clause-level simplified texts.
        Returns a dict matching DocumentSummary schema.
        """
        logger.info("Summarizing rag corpus %s", rag_corpus_name)
        try:
            # Create retrieval tool
            tool = self._make_rag_retrieval_tool(rag_corpus_name, top_k=6)

            # instantiate model with tool
            rag_model = GenerativeModel(model_name=DEFAULT_MODEL, tools=[tool])

            # prompt instructing JSON output, clause extraction, risk scoring (ask LLM to return numeric risk 0-100)
            prompt = """
You are a helpful assistant that reads legal text (clauses) and returns structured JSON.
Given the context retrieved from the provided documents, produce a JSON object with keys:
- title: string or null
- summary: short high-level summary of the document (3-5 sentences)
- overall_risk_score: a number 0-100 representing overall document risk (higher = riskier)
- clauses: an array of objects with keys:
  - original: original clause text (string)
  - simplified: simple, plain-language explanation (1-2 sentences)
  - llm_score: a numeric risk estimate 0-100
  - provenance: array of provenance objects with keys page (if available), start_offset (if available), text (snippet)
Return ONLY valid JSON. Do not include backticks or explanation. 
"""

            # generate content (with the retrieval tool so model can access doc chunks)
            response = rag_model.generate_content(prompt)
            text = response.text or ""
            parsed = safe_parse_json(text)
            if not parsed:
                # fallback: ask retrieval_query to get raw retrieval result + attempt light summary
                logger.warning("Failed to parse JSON from model. Falling back to retrieval_query.")
                retrieval = rag.retrieval_query(
                    rag_resources=[rag.RagResource(rag_corpus=rag_corpus_name)],
                    text="Please provide a short summary of the document and list key clauses.",
                    rag_retrieval_config=rag.RagRetrievalConfig(top_k=4),
                )
                # Construct minimal structured fallback
                summary_text = getattr(retrieval, "text", "") or "Summary unavailable"
                clauses = []
                parsed_fallback = {
                    "title": None,
                    "summary": summary_text,
                    "overall_risk_score": 50.0,
                    "rag_corpus_name": rag_corpus_name,
                    "clauses": clauses,
                }
                return parsed_fallback

            # Convert model-provided clauses to our schema
            clauses_out = []
            for c in parsed.get("clauses", []):
                llm_score = float(c.get("llm_score", 50)) if c.get("llm_score") is not None else 50.0
                provs = c.get("provenance", [])
                clauses_out.append(
                    {
                        "original": c.get("original", ""),
                        "simplified": c.get("simplified", ""),
                        "risk": "high" if llm_score >= 66 else "medium" if llm_score >= 33 else "low",
                        "score": llm_score,
                        "provenance": provs,
                    }
                )

            out = {
                "title": parsed.get("title"),
                "summary": parsed.get("summary", ""),
                "overall_risk_score": float(parsed.get("overall_risk_score", 50.0)),
                "rag_corpus_name": rag_corpus_name,
                "clauses": clauses_out,
            }
            return out

        except Exception as e:
            logger.exception("summarize_document failed")
            return {
                "title": None,
                "summary": "Failed to summarize document",
                "overall_risk_score": 50.0,
                "rag_corpus_name": rag_corpus_name,
                "clauses": [],
            }

    def query_rag(self, rag_corpus_name: str, question: str, top_k: int = 4) -> Dict[str, Any]:
        """
        Answer a question grounded on documents in the rag corpus.
        Returns: {'answer': str, 'evidence': [ {text, page, start_offset} ] }
        """
        logger.info("Running query against %s: %s", rag_corpus_name, question)
        try:
            # 1) direct retrieval (this returns retrieval results)
            retrieval_result = rag.retrieval_query(
                rag_resources=[rag.RagResource(rag_corpus=rag_corpus_name)],
                text=question,
                rag_retrieval_config=rag.RagRetrievalConfig(top_k=top_k),
            )

            # gather evidence from retrieval_result
            evidence = []
            # retrieval_result may have a .responses or .items; we attempt to extract text
            if hasattr(retrieval_result, "items"):
                for it in retrieval_result.items:
                    # each item might have a 'content' attribute or similar
                    try:
                        evidence.append({"text": getattr(it, "text", str(it)), "metadata": getattr(it, "metadata", None)})
                    except Exception:
                        evidence.append({"text": str(it)})
            else:
                # fallback: include raw repr
                evidence.append({"text": str(retrieval_result)})

            # 2) use the retrieval tool + model to generate an answer using the retrieved context
            tool = self._make_rag_retrieval_tool(rag_corpus_name, top_k=top_k)
            rag_model = GenerativeModel(model_name=DEFAULT_MODEL, tools=[tool])

            prompt = f"Using only the retrieved document context, answer the question concisely and cite any provenance (page or snippet). Question: {question}\n\nReturn JSON: {{'answer': string, 'provenance': [{{'text':string}}]}}"
            gen_resp = rag_model.generate_content(prompt)
            gen_text = gen_resp.text or ""
            parsed = safe_parse_json(gen_text)
            if parsed:
                answer = parsed.get("answer", gen_text)
                provs = parsed.get("provenance", evidence)
            else:
                answer = gen_text or str(retrieval_result)
                provs = evidence

            return {"answer": answer, "evidence": provs}
        except Exception as e:
            logger.exception("query_rag failed")
            return {"answer": "Failed to answer question due to an internal error.", "evidence": []}
