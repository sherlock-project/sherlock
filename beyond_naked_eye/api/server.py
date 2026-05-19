from fastapi import FastAPI

from beyond_naked_eye.analysis.assistant import summarize_findings
from beyond_naked_eye.engine import ScanEngine

app = FastAPI(title="Beyond The Naked Eye API")
engine = ScanEngine()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/scan/{scan_type}")
async def scan(scan_type: str, value: str):
    findings = await engine.scan(scan_type, value)
    return {"findings": [f.to_dict() for f in findings], "summary": summarize_findings(findings)}
