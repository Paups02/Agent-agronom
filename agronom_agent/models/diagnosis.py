"""Models per a diagnòstic fitosanitari i alertes."""

from enum import Enum
from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    """Nivells de severitat."""
    INFO = "informatiu"
    LOW = "baix"
    MEDIUM = "mitjà"
    HIGH = "alt"
    CRITICAL = "crític"


class PestType(str, Enum):
    """Tipus d'agents nocius."""
    INSECT = "insecte"
    FUNGUS = "fong"
    BACTERIA = "bacteri"
    VIRUS = "virus"
    NEMATODE = "nematode"
    WEED = "mala_herba"
    ABIOTIC = "abiòtic"


class PhytosanitaryAlert(BaseModel):
    """Alerta fitosanitària."""
    pest_name: str = Field(..., description="Nom de la plaga/malaltia")
    pest_type: PestType
    severity: SeverityLevel
    affected_crop: str
    symptoms: list[str]
    conditions_favoring: str
    preventive_measures: list[str]
    curative_treatments: list[str]
    organic_alternatives: list[str]
    action_deadline_days: int = Field(
        default=7,
        description="Dies màxims per actuar"
    )


class FertilizationPlan(BaseModel):
    """Pla de fertilització personalitzat."""
    crop_name: str
    growth_stage: str
    nitrogen_kg_ha: float
    phosphorus_kg_ha: float
    potassium_kg_ha: float
    application_method: str
    timing: str
    recommended_products: list[str]
    organic_alternatives: list[str]
    estimated_cost_eur_ha: float
    notes: list[str] = Field(default_factory=list)


class AgentReport(BaseModel):
    """Informe complet de l'agent agronòmic."""
    farm_id: str
    crop_name: str
    soil_score: float
    climate_risks: list[str]
    active_alerts: list[PhytosanitaryAlert]
    fertilization_plan: FertilizationPlan | None = None
    irrigation_plan: dict | None = None
    priority_actions: list[str]
    estimated_savings_eur: float = 0.0
