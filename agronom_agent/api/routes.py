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
from agronom_agent.data.crop_database import list_crops, get_crop


STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(
    title="AgroNom Agent API",
    description=(
        "Agent IA agronòmic professional. Diagnòstic de sòl, "
        "fertilització intel·ligent, alertes fitosanitàries "
        "i planificació de reg personalitzada."
    ),
    version="1.0.0",
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
    """Petició de diagnòstic complet."""
    soil: SoilAnalysis
    crop: CropProfile
    weather: WeatherData
    farm_id: str = "FARM-001"


class PestCheckRequest(BaseModel):
    """Petició de consulta fitosanitària."""
    crop: CropProfile
    weather: WeatherData


class IrrigationRequest(BaseModel):
    """Petició de càlcul de reg."""
    crop: CropProfile
    weather: WeatherData


@app.get("/", include_in_schema=False)
def homepage():
    """Serveix la interfície web SaaS."""
    return FileResponse(str(STATIC_DIR / "index.html"), media_type="text/html")


@app.get("/api")
def api_info():
    """Informació de l'API."""
    return utf8_json({
        "name": "AgroNom Agent",
        "version": "1.0.0",
        "description": "Agent IA agronòmic professional",
        "endpoints": [
            "/diagnosis — Diagnòstic complet (sòl + cultiu + clima)",
            "/soil — Diagnòstic ràpid de sòl",
            "/pests — Alertes fitosanitàries",
            "/irrigation — Planificació de reg",
            "/crops — Llista de cultius disponibles",
            "/crops/{name} — Informació d'un cultiu",
        ],
    })


@app.post("/diagnosis")
def full_diagnosis(request: FullDiagnosisRequest):
    """Diagnòstic complet: sòl + clima + plagues + fertilització + reg."""
    report = agent.full_diagnosis(
        soil=request.soil,
        crop=request.crop,
        weather=request.weather,
        farm_id=request.farm_id,
    )
    return utf8_json(report.model_dump())


@app.post("/soil")
def soil_diagnosis(soil: SoilAnalysis):
    """Diagnòstic ràpid de sòl."""
    diagnosis = agent.quick_soil_check(soil)
    return utf8_json(diagnosis.model_dump())


@app.post("/pests")
def pest_check(request: PestCheckRequest):
    """Consulta d'alertes fitosanitàries."""
    alerts = agent.quick_pest_check(request.crop, request.weather)
    return utf8_json([alert.model_dump() for alert in alerts])


@app.post("/irrigation")
def irrigation_plan(request: IrrigationRequest):
    """Càlcul de necessitats de reg."""
    plan = agent.quick_irrigation(request.crop, request.weather)
    return utf8_json(plan.model_dump())


@app.get("/crops")
def available_crops():
    """Llista de cultius disponibles a la base de dades."""
    return utf8_json({"crops": list_crops()})


@app.get("/crops/{name}")
def crop_info(name: str):
    """Informació detallada d'un cultiu."""
    crop = get_crop(name)
    if not crop:
        raise HTTPException(
            status_code=404,
            detail=f"Cultiu '{name}' no trobat. Useu /crops per veure disponibles.",
        )
    return utf8_json(crop.model_dump())
