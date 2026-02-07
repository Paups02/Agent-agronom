"""API REST de l'agent agronòmic amb FastAPI."""

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agronom_agent.models.soil import SoilAnalysis
from agronom_agent.models.crop import CropProfile
from agronom_agent.models.climate import WeatherData
from agronom_agent.services.agent import AgronomAgent
from agronom_agent.services.gemini_advisor import ask_gemini
from agronom_agent.data.crop_database import list_crops, get_crop


STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(
    title="AgroNom Agent API",
    description=(
        "Agent IA agronòmic professional. Diagnòstic de sòl, "
        "fertilització intel·ligent, alertes fitosanitàries, "
        "planificació de reg, gràfics i assessor IA."
    ),
    version="2.0.0",
)

# Servir fitxers estàtics (CSS, JS)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

agent = AgronomAgent()


def utf8_json(data) -> Response:
    """Retorna JSON amb UTF-8 correcte (caràcters catalans visibles)."""
    return Response(
        content=json.dumps(data, ensure_ascii=False, indent=2),
        media_type="application/json; charset=utf-8",
    )


class FullDiagnosisRequest(BaseModel):
    soil: SoilAnalysis
    crop: CropProfile
    weather: WeatherData
    farm_id: str = "FARM-001"


class PestCheckRequest(BaseModel):
    crop: CropProfile
    weather: WeatherData


class IrrigationRequest(BaseModel):
    crop: CropProfile
    weather: WeatherData


class ChatRequest(BaseModel):
    question: str
    context: str = ""
    api_key: str = ""


# ─── FRONTEND ───

@app.get("/", include_in_schema=False)
def homepage():
    return FileResponse(str(STATIC_DIR / "index.html"), media_type="text/html")


# ─── API INFO ───

@app.get("/api")
def api_info():
    return utf8_json({
        "name": "AgroNom Agent",
        "version": "2.0.0",
        "description": "Agent IA agronòmic professional amb gràfics, economia i assessor IA",
        "endpoints": [
            "/report — Informe complet amb gràfics i economia (POST)",
            "/diagnosis — Diagnòstic complet (POST)",
            "/soil — Diagnòstic ràpid de sòl (POST)",
            "/pests — Alertes fitosanitàries (POST)",
            "/irrigation — Planificació de reg (POST)",
            "/chat — Assessor IA agronòmic (POST)",
            "/crops — Llista de cultius (GET)",
            "/crops/{name} — Info d'un cultiu (GET)",
        ],
    })


# ─── REPORT COMPLET AMB GRÀFICS ───

@app.post("/report")
def full_report(request: FullDiagnosisRequest):
    """Informe complet amb gràfics matplotlib i anàlisi econòmica."""
    result = agent.full_report_with_charts(
        soil=request.soil,
        crop=request.crop,
        weather=request.weather,
        farm_id=request.farm_id,
    )
    return utf8_json(result)


# ─── DIAGNÒSTIC (sense gràfics) ───

@app.post("/diagnosis")
def full_diagnosis(request: FullDiagnosisRequest):
    report = agent.full_diagnosis(
        soil=request.soil,
        crop=request.crop,
        weather=request.weather,
        farm_id=request.farm_id,
    )
    return utf8_json(report.model_dump())


@app.post("/soil")
def soil_diagnosis(soil: SoilAnalysis):
    diagnosis = agent.quick_soil_check(soil)
    return utf8_json(diagnosis.model_dump())


@app.post("/pests")
def pest_check(request: PestCheckRequest):
    alerts = agent.quick_pest_check(request.crop, request.weather)
    return utf8_json([alert.model_dump() for alert in alerts])


@app.post("/irrigation")
def irrigation_plan(request: IrrigationRequest):
    plan = agent.quick_irrigation(request.crop, request.weather)
    return utf8_json(plan.model_dump())


# ─── ASSESSOR IA (GEMINI) ───

@app.post("/chat")
def chat_advisor(request: ChatRequest):
    """Assessor agronòmic IA amb Gemini o respostes locals."""
    response = ask_gemini(
        question=request.question,
        context=request.context,
        api_key=request.api_key or None,
    )
    return utf8_json({"question": request.question, "answer": response})


# ─── CULTIUS ───

@app.get("/crops")
def available_crops():
    return utf8_json({"crops": list_crops()})


@app.get("/crops/{name}")
def crop_info(name: str):
    crop = get_crop(name)
    if not crop:
        raise HTTPException(
            status_code=404,
            detail=f"Cultiu '{name}' no trobat. Useu /crops per veure disponibles.",
        )
    return utf8_json(crop.model_dump())
