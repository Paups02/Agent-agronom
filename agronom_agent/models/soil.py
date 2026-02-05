"""Models de dades per a l'anàlisi de sòl."""

from enum import Enum
from pydantic import BaseModel, Field


class SoilTexture(str, Enum):
    """Textures de sòl segons triangle textural USDA."""
    SANDY = "arenós"
    LOAMY_SAND = "arenós-franc"
    SANDY_LOAM = "franc-arenós"
    LOAM = "franc"
    SILT_LOAM = "franc-llimós"
    SILT = "llimós"
    SANDY_CLAY_LOAM = "franc-argilo-arenós"
    CLAY_LOAM = "franc-argilós"
    SILTY_CLAY_LOAM = "franc-argilo-llimós"
    SANDY_CLAY = "argilo-arenós"
    SILTY_CLAY = "argilo-llimós"
    CLAY = "argilós"


class SoilAnalysis(BaseModel):
    """Anàlisi completa de sòl amb paràmetres agronòmics."""
    ph: float = Field(..., ge=3.0, le=10.0, description="pH del sòl (3.0-10.0)")
    organic_matter: float = Field(
        ..., ge=0.0, le=15.0,
        description="Matèria orgànica en percentatge"
    )
    nitrogen_ppm: float = Field(
        ..., ge=0.0, description="Nitrogen disponible (ppm)"
    )
    phosphorus_ppm: float = Field(
        ..., ge=0.0, description="Fòsfor disponible Olsen (ppm)"
    )
    potassium_ppm: float = Field(
        ..., ge=0.0, description="Potassi disponible (ppm)"
    )
    texture: SoilTexture = Field(..., description="Textura del sòl")
    electrical_conductivity: float = Field(
        default=0.0, ge=0.0,
        description="Conductivitat elèctrica (dS/m)"
    )
    calcium_ppm: float = Field(default=0.0, ge=0.0, description="Calci (ppm)")
    magnesium_ppm: float = Field(default=0.0, ge=0.0, description="Magnesi (ppm)")
    depth_cm: float = Field(
        default=30.0, ge=0.0,
        description="Profunditat de mostreig (cm)"
    )


class SoilDiagnosis(BaseModel):
    """Resultat del diagnòstic de sòl."""
    ph_status: str
    ph_recommendation: str
    organic_matter_status: str
    organic_matter_recommendation: str
    nitrogen_status: str
    phosphorus_status: str
    potassium_status: str
    salinity_risk: str
    overall_fertility: str
    limiting_factors: list[str]
    score: float = Field(..., ge=0.0, le=100.0, description="Puntuació de salut (0-100)")
