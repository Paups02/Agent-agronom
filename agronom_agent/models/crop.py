"""Models de dades per a cultius i fenologia."""

from enum import Enum
from pydantic import BaseModel, Field


class CropCategory(str, Enum):
    """Categories principals de cultius."""
    CEREALS = "cereals"
    HORTALISSES = "hortalisses"
    FRUITA = "fruita"
    LLEGUMINOSES = "lleguminoses"
    OLIVOS = "olivera"
    VINYA = "vinya"
    CITRICS = "cítrics"
    TUBERCLES = "tubercles"


class GrowthStage(str, Enum):
    """Fases fenològiques generalitzades."""
    GERMINATION = "germinació"
    SEEDLING = "plàntula"
    VEGETATIVE = "creixement_vegetatiu"
    FLOWERING = "floració"
    FRUIT_SET = "quallat"
    RIPENING = "maduració"
    HARVEST = "collita"
    DORMANCY = "dormància"


class CropProfile(BaseModel):
    """Perfil complet d'un cultiu."""
    name: str = Field(..., description="Nom del cultiu")
    category: CropCategory
    variety: str = Field(default="", description="Varietat específica")
    growth_stage: GrowthStage = Field(
        default=GrowthStage.VEGETATIVE,
        description="Fase fenològica actual"
    )
    area_hectares: float = Field(
        ..., gt=0.0, description="Superfície en hectàrees"
    )
    planting_date: str = Field(
        default="", description="Data de sembra (YYYY-MM-DD)"
    )
    irrigation_type: str = Field(
        default="pluja", description="Tipus de reg: pluja, degoteig, aspersió, inundació"
    )
    previous_crop: str = Field(
        default="", description="Cultiu anterior (rotació)"
    )


class CropRequirements(BaseModel):
    """Requeriments nutricionals i hídrics d'un cultiu."""
    crop_name: str
    optimal_ph_min: float
    optimal_ph_max: float
    nitrogen_kg_ha: float
    phosphorus_kg_ha: float
    potassium_kg_ha: float
    water_mm_cycle: float
    optimal_temp_min: float
    optimal_temp_max: float
    sensitive_stages: list[str]
    common_pests: list[str]
    common_diseases: list[str]
