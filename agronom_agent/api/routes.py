"""API REST de l'agent agronòmic amb FastAPI."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agronom_agent.models.soil import SoilAnalysis
from agronom_agent.models.crop import CropProfile
from agronom_agent.models.climate import WeatherData
from agronom_agent.services.agent import AgronomAgent
from agronom_agent.data.crop_database import list_crops, get_crop


app = FastAPI(
    title="AgroNom Agent API",
    description=(
        "Agent IA agronòmic professional. Diagnòstic de sòl, "
        "fertilització intel·ligent, alertes fitosanitàries "
        "i planificació de reg personalitzada."
    ),
    version="1.0.0",
)

agent = AgronomAgent()


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


@app.get("/")
def root():
    """Informació de l'API."""
    return {
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
    }


@app.post("/diagnosis")
def full_diagnosis(request: FullDiagnosisRequest):
    """Diagnòstic complet: sòl + clima + plagues + fertilització + reg."""
    report = agent.full_diagnosis(
        soil=request.soil,
        crop=request.crop,
        weather=request.weather,
        farm_id=request.farm_id,
    )
    return report.model_dump()


@app.post("/soil")
def soil_diagnosis(soil: SoilAnalysis):
    """Diagnòstic ràpid de sòl."""
    diagnosis = agent.quick_soil_check(soil)
    return diagnosis.model_dump()


@app.post("/pests")
def pest_check(request: PestCheckRequest):
    """Consulta d'alertes fitosanitàries."""
    alerts = agent.quick_pest_check(request.crop, request.weather)
    return [alert.model_dump() for alert in alerts]


@app.post("/irrigation")
def irrigation_plan(request: IrrigationRequest):
    """Càlcul de necessitats de reg."""
    plan = agent.quick_irrigation(request.crop, request.weather)
    return plan.model_dump()


@app.get("/crops")
def available_crops():
    """Llista de cultius disponibles a la base de dades."""
    return {"crops": list_crops()}


@app.get("/crops/{name}")
def crop_info(name: str):
    """Informació detallada d'un cultiu."""
    crop = get_crop(name)
    if not crop:
        raise HTTPException(
            status_code=404,
            detail=f"Cultiu '{name}' no trobat. Useu /crops per veure disponibles.",
        )
    return crop.model_dump()
