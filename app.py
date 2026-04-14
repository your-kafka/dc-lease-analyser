"""
DC Lease Analyser — FastAPI Backend
"""
import os
import sys
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(__file__))

from loaders.loader import load_document
from prompts.extraction_prompt import build_extraction_prompt
from extraction.claude_client import call_groq
from extraction.risk_advisor import get_risk_solutions
from output.report_formatter import format_report

app = FastAPI(title="DC Lease Analyser API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md"}


class AnalysisResponse(BaseModel):
    status: str
    file_name: str
    file_type: str
    extracted: dict
    risk_solutions: list
    report: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "DC Lease Analyser"}


@app.post("/analyse")
async def analyse_lease(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {list(ALLOWED_EXTENSIONS)}"
        )

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    try:
        text, file_type = load_document(tmp_path)
        text = " ".join(text.replace("\n", " ").split())

        prompt = build_extraction_prompt(text)
        extracted = call_groq(prompt)

        if not extracted or "status" in extracted:
            raise HTTPException(status_code=500, detail=f"Extraction failed: {extracted}")

        risk_flags = extracted.get("analysis", {}).get("risk_flags", [])
        risk_solutions = get_risk_solutions(risk_flags) if risk_flags else []

        report = format_report(extracted, file.filename, file_type, "Groq API", risk_solutions)

        return {
            "status": "success",
            "file_name": file.filename,
            "file_type": file_type,
            "extracted": extracted,
            "risk_solutions": risk_solutions,
            "report": report,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")