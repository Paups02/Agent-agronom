"""Models de dades climàtiques i meteorològiques."""

from pydantic import BaseModel, Field


class WeatherData(BaseModel):
    """Dades meteorològiques actuals o previstes."""
    temperature_c: float = Field(..., description="Temperatura mitjana (°C)")
    temp_min_c: float = Field(default=0.0, description="Temperatura mínima (°C)")
    temp_max_c: float = Field(default=0.0, description="Temperatura màxima (°C)")
    humidity_percent: float = Field(
        ..., ge=0.0, le=100.0, description="Humitat relativa (%)"
    )
    precipitation_mm: float = Field(
        default=0.0, ge=0.0, description="Precipitació (mm)"
    )
    wind_speed_kmh: float = Field(
        default=0.0, ge=0.0, description="Velocitat del vent (km/h)"
    )
    solar_radiation: float = Field(
        default=0.0, ge=0.0, description="Radiació solar (MJ/m²/dia)"
    )
    eto_mm: float = Field(
        default=0.0, ge=0.0,
        description="Evapotranspiració de referència (mm/dia)"
    )


class ClimateRisk(BaseModel):
    """Avaluació de riscos climàtics."""
    frost_risk: str = Field(default="baix", description="Risc de gelada")
    heat_stress_risk: str = Field(default="baix", description="Risc d'estrès tèrmic")
    drought_risk: str = Field(default="baix", description="Risc de sequera")
    disease_pressure: str = Field(
        default="baix",
        description="Pressió de malalties (basada en humitat/temperatura)"
    )
    recommendations: list[str] = Field(default_factory=list)


class IrrigationPlan(BaseModel):
    """Pla de reg recomanat."""
    crop_name: str
    growth_stage: str
    daily_water_need_mm: float
    irrigation_frequency_days: int
    dose_per_irrigation_mm: float
    efficiency_factor: float
    gross_dose_mm: float
    monthly_total_m3_ha: float
    notes: list[str] = Field(default_factory=list)
