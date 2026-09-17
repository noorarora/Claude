from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.classifier import PhishingClassifier
from app.database import initialise_database, recent_analyses, save_analysis
from app.schemas import AnalysisRequest, AnalysisResponse, HistoryItem, Signal

BASE_DIR = Path(__file__).resolve().parent
classifier = PhishingClassifier()


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialise_database()
    yield


app = FastAPI(
    title="PhishGuard AI",
    description="Explainable phishing-risk triage for suspicious messages.",
    version="0.1.0",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


def verdict_for(score: int) -> tuple[str, str]:
    if score >= 70:
        return (
            "High risk",
            "Do not click links or reply. Verify the request through an official channel.",
        )
    if score >= 40:
        return "Suspicious", "Treat this message cautiously and verify the sender independently."
    return "Low risk", "No strong phishing indicators were found, but remain cautious with links."


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "phishguard-ai"}


@app.post("/api/analyse", response_model=AnalysisResponse, status_code=201)
def analyse_message(request: AnalysisRequest) -> AnalysisResponse:
    risk_score, confidence, detected = classifier.analyse(request.text)
    verdict, recommendation = verdict_for(risk_score)
    record = save_analysis(request.text, risk_score, confidence, verdict)
    return AnalysisResponse(
        id=record["id"],
        risk_score=risk_score,
        verdict=verdict,
        confidence=round(confidence, 4),
        signals=[
            Signal(label=item.label, detail=item.detail, severity=item.severity)
            for item in detected
        ],
        recommendation=recommendation,
        created_at=record["created_at"],
    )


@app.get("/api/history", response_model=list[HistoryItem])
def history(limit: int = Query(default=10, ge=1, le=50)) -> list[HistoryItem]:
    return [
        HistoryItem(
            id=row["id"],
            preview=row["text"][:100],
            risk_score=row["risk_score"],
            verdict=row["verdict"],
            created_at=row["created_at"],
        )
        for row in recent_analyses(limit)
    ]
