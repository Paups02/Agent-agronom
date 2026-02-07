"""Calculadora econòmica agronòmica.

Anàlisi de rendibilitat, ROI i estalvi per hectàrea basada en
dades reals del sector agrari mediterrani (MAPA, CaixaBank Research 2024-25).

Fonts:
- CaixaBank Research: Sector agroalimentari Espanya 2024-2025
- MAPA: Costos de producció per hectàrea
- FAO: Rendiments mitjans per cultiu
- Estudis CBA irrigació mediterrània (Wiley 2025)
"""

from agronom_agent.models.crop import CropProfile, GrowthStage
from agronom_agent.models.diagnosis import FertilizationPlan
from agronom_agent.data.crop_database import get_crop


# Rendiments mitjans i preus de mercat (€/kg) — Espanya 2024-2025
CROP_ECONOMICS: dict[str, dict] = {
    "tomàquet": {
        "yield_kg_ha": 80000, "price_eur_kg": 0.55,
        "phyto_cost_ha": 280, "labor_cost_ha": 3500,
        "seed_cost_ha": 450, "other_cost_ha": 600,
    },
    "pebrot": {
        "yield_kg_ha": 45000, "price_eur_kg": 0.70,
        "phyto_cost_ha": 250, "labor_cost_ha": 3200,
        "seed_cost_ha": 380, "other_cost_ha": 500,
    },
    "olivera": {
        "yield_kg_ha": 5000, "price_eur_kg": 3.50,
        "phyto_cost_ha": 180, "labor_cost_ha": 1200,
        "seed_cost_ha": 0, "other_cost_ha": 300,
    },
    "vinya": {
        "yield_kg_ha": 8000, "price_eur_kg": 0.45,
        "phyto_cost_ha": 350, "labor_cost_ha": 1800,
        "seed_cost_ha": 0, "other_cost_ha": 400,
    },
    "blat": {
        "yield_kg_ha": 4500, "price_eur_kg": 0.22,
        "phyto_cost_ha": 80, "labor_cost_ha": 250,
        "seed_cost_ha": 90, "other_cost_ha": 150,
    },
    "ordi": {
        "yield_kg_ha": 4000, "price_eur_kg": 0.20,
        "phyto_cost_ha": 70, "labor_cost_ha": 230,
        "seed_cost_ha": 80, "other_cost_ha": 140,
    },
    "blat_de_moro": {
        "yield_kg_ha": 12000, "price_eur_kg": 0.21,
        "phyto_cost_ha": 120, "labor_cost_ha": 350,
        "seed_cost_ha": 250, "other_cost_ha": 200,
    },
    "enciam": {
        "yield_kg_ha": 35000, "price_eur_kg": 0.40,
        "phyto_cost_ha": 200, "labor_cost_ha": 4000,
        "seed_cost_ha": 300, "other_cost_ha": 500,
    },
    "patata": {
        "yield_kg_ha": 35000, "price_eur_kg": 0.25,
        "phyto_cost_ha": 220, "labor_cost_ha": 1500,
        "seed_cost_ha": 800, "other_cost_ha": 400,
    },
    "taronger": {
        "yield_kg_ha": 25000, "price_eur_kg": 0.30,
        "phyto_cost_ha": 250, "labor_cost_ha": 2000,
        "seed_cost_ha": 0, "other_cost_ha": 400,
    },
    "ametller": {
        "yield_kg_ha": 2000, "price_eur_kg": 4.00,
        "phyto_cost_ha": 150, "labor_cost_ha": 800,
        "seed_cost_ha": 0, "other_cost_ha": 250,
    },
    "mongeta": {
        "yield_kg_ha": 15000, "price_eur_kg": 0.80,
        "phyto_cost_ha": 150, "labor_cost_ha": 2500,
        "seed_cost_ha": 200, "other_cost_ha": 350,
    },
    "arròs": {
        "yield_kg_ha": 7500, "price_eur_kg": 0.35,
        "phyto_cost_ha": 100, "labor_cost_ha": 400,
        "seed_cost_ha": 150, "other_cost_ha": 300,
    },
}

# Cost d'aigua per m³ segons tipus de reg (€/m³)
WATER_COSTS = {
    "degoteig": 0.12,
    "aspersió": 0.10,
    "inundació": 0.08,
    "pluja": 0.0,
}


class EconomicCalculator:
    """Calculadora de rendibilitat i ROI agronòmic."""

    def calculate(
        self,
        crop: CropProfile,
        fertilization_plan: FertilizationPlan,
        irrigation_plan: dict,
        soil_score: float,
    ) -> dict:
        """Calcula l'anàlisi econòmica completa."""
        econ = CROP_ECONOMICS.get(
            crop.name.lower(), self._default_economics()
        )

        # Ingressos
        yield_factor = self._yield_factor_from_score(soil_score)
        expected_yield = econ["yield_kg_ha"] * yield_factor
        gross_income = expected_yield * econ["price_eur_kg"]

        # Costos amb assessoria AgroNom
        fert_cost = fertilization_plan.estimated_cost_eur_ha
        water_m3 = irrigation_plan.get("monthly_total_m3_ha", 0) * 6  # 6 mesos de reg
        water_cost = water_m3 * WATER_COSTS.get(crop.irrigation_type, 0.10)
        phyto_cost = econ["phyto_cost_ha"] * 0.7  # 30% estalvi per prevenció
        total_cost_with = (
            fert_cost + water_cost + phyto_cost
            + econ["labor_cost_ha"] + econ["seed_cost_ha"] + econ["other_cost_ha"]
        )

        # Costos sense assessoria (genèric)
        fert_cost_generic = econ.get("yield_kg_ha", 5000) * 0.05  # ~5% del rendiment
        fert_cost_generic = min(max(fert_cost_generic, 200), 600)
        water_cost_generic = water_cost * 1.35  # 35% més d'aigua
        phyto_cost_generic = econ["phyto_cost_ha"]
        total_cost_without = (
            fert_cost_generic + water_cost_generic + phyto_cost_generic
            + econ["labor_cost_ha"] + econ["seed_cost_ha"] + econ["other_cost_ha"]
        )

        # Rendiments sense assessoria (15-25% menys per diagnòstic tardà)
        yield_without = econ["yield_kg_ha"] * 0.82
        income_without = yield_without * econ["price_eur_kg"]

        # Marge i ROI
        margin_with = gross_income - total_cost_with
        margin_without = income_without - total_cost_without
        extra_profit = margin_with - margin_without

        # Escalar a tota la finca
        total_savings = extra_profit * crop.area_hectares

        # ROI de l'assessoria
        advisory_cost = 0  # AgroNom és gratuït
        roi = ((extra_profit / max(total_cost_with, 1)) * 100)

        # Mètriques de sostenibilitat
        water_saved_m3 = (water_cost_generic - water_cost) / max(
            WATER_COSTS.get(crop.irrigation_type, 0.10), 0.01
        )
        fert_saved_kg = max(0, fert_cost_generic - fert_cost) / 1.0  # ~1€/kg aproximat

        return {
            "crop_name": crop.name,
            "area_hectares": crop.area_hectares,
            # Ingressos
            "expected_yield_kg_ha": round(expected_yield),
            "price_eur_kg": econ["price_eur_kg"],
            "gross_income_eur_ha": round(gross_income, 2),
            # Costos amb AgroNom
            "fert_cost_with": round(fert_cost, 2),
            "phyto_cost_with": round(phyto_cost, 2),
            "irrig_cost_with": round(water_cost, 2),
            "total_cost_with": round(total_cost_with, 2),
            # Costos sense assessoria
            "fert_cost_without": round(fert_cost_generic, 2),
            "phyto_cost_without": round(phyto_cost_generic, 2),
            "irrig_cost_without": round(water_cost_generic, 2),
            "total_cost_without": round(total_cost_without, 2),
            # Marges
            "margin_with_eur_ha": round(margin_with, 2),
            "margin_without_eur_ha": round(margin_without, 2),
            "extra_profit_eur_ha": round(extra_profit, 2),
            "total_savings_eur": round(total_savings, 2),
            "roi_percent": round(roi, 1),
            # Sostenibilitat
            "water_saved_m3_ha": round(water_saved_m3, 1),
            "fertilizer_saved_kg_ha": round(fert_saved_kg, 1),
            # Projecció anual
            "annual_income_eur": round(gross_income * crop.area_hectares, 2),
            "annual_cost_eur": round(total_cost_with * crop.area_hectares, 2),
            "annual_profit_eur": round(margin_with * crop.area_hectares, 2),
        }

    def _yield_factor_from_score(self, soil_score: float) -> float:
        """Estima factor de rendiment segons salut del sòl."""
        if soil_score >= 80:
            return 1.0
        elif soil_score >= 60:
            return 0.90
        elif soil_score >= 40:
            return 0.75
        elif soil_score >= 20:
            return 0.55
        else:
            return 0.35

    def _default_economics(self) -> dict:
        return {
            "yield_kg_ha": 10000, "price_eur_kg": 0.50,
            "phyto_cost_ha": 200, "labor_cost_ha": 1500,
            "seed_cost_ha": 200, "other_cost_ha": 300,
        }
