"""Servei de planificació de fertilització intel·ligent.

Calcula plans de fertilització personalitzats basats en l'anàlisi
de sòl, els requeriments del cultiu i la fase fenològica.
"""

from agronom_agent.models.soil import SoilAnalysis, SoilDiagnosis
from agronom_agent.models.crop import CropProfile, GrowthStage
from agronom_agent.models.diagnosis import FertilizationPlan
from agronom_agent.data.crop_database import get_crop
from agronom_agent.data.nutrient_thresholds import (
    NITROGEN_RANGES,
    PHOSPHORUS_RANGES,
    POTASSIUM_RANGES,
    classify_value,
)


# Factors de correcció per disponibilitat segons pH
PH_CORRECTION_FACTORS = {
    # (N_factor, P_factor, K_factor) — >1.0 = cal més perquè hi ha menys disponibilitat
    "molt_àcid": (1.0, 1.5, 1.1),
    "àcid": (1.0, 1.3, 1.05),
    "lleugerament_àcid": (1.0, 1.1, 1.0),
    "neutre": (1.0, 1.0, 1.0),
    "lleugerament_alcalí": (1.0, 1.2, 1.0),
    "alcalí": (1.05, 1.4, 1.0),
    "molt_alcalí": (1.1, 1.6, 1.05),
}

# Distribució de N per fase fenològica (proporció del total)
N_STAGE_DISTRIBUTION = {
    GrowthStage.GERMINATION: 0.0,
    GrowthStage.SEEDLING: 0.10,
    GrowthStage.VEGETATIVE: 0.40,
    GrowthStage.FLOWERING: 0.30,
    GrowthStage.FRUIT_SET: 0.15,
    GrowthStage.RIPENING: 0.05,
    GrowthStage.HARVEST: 0.0,
    GrowthStage.DORMANCY: 0.0,
}

# Preus aproximats per kg de nutrient (EUR)
NUTRIENT_COSTS = {
    "N": 1.2,  # EUR/kg N
    "P2O5": 1.0,  # EUR/kg P2O5
    "K2O": 0.8,  # EUR/kg K2O
}


class FertilizationPlanner:
    """Planifica la fertilització basada en sòl i cultiu."""

    def create_plan(
        self,
        soil: SoilAnalysis,
        soil_diagnosis: SoilDiagnosis,
        crop: CropProfile,
    ) -> FertilizationPlan:
        """Crea un pla de fertilització personalitzat."""
        crop_data = get_crop(crop.name)
        if not crop_data:
            return self._default_plan(crop)

        # Calcular necessitats base del cultiu
        n_need = crop_data.nitrogen_kg_ha
        p_need = crop_data.phosphorus_kg_ha
        k_need = crop_data.potassium_kg_ha

        # Ajustar segons nivell actual del sòl
        n_need = self._adjust_for_soil_level(
            n_need, soil.nitrogen_ppm, NITROGEN_RANGES
        )
        p_need = self._adjust_for_soil_level(
            p_need, soil.phosphorus_ppm, PHOSPHORUS_RANGES
        )
        k_need = self._adjust_for_soil_level(
            k_need, soil.potassium_ppm, POTASSIUM_RANGES
        )

        # Correcció per pH (disponibilitat)
        ph_status = soil_diagnosis.ph_status
        n_factor, p_factor, k_factor = PH_CORRECTION_FACTORS.get(
            ph_status, (1.0, 1.0, 1.0)
        )
        n_need *= n_factor
        p_need *= p_factor
        k_need *= k_factor

        # Distribuir N segons fase fenològica actual
        n_stage_factor = N_STAGE_DISTRIBUTION.get(crop.growth_stage, 0.25)
        n_this_application = n_need * n_stage_factor

        # Determinar mètode i productes
        method, timing = self._recommend_method(crop)
        products = self._recommend_products(n_this_application, p_need, k_need)
        organic = self._recommend_organic(crop, soil_diagnosis)

        # Estimació de cost
        cost = self._estimate_cost(n_need, p_need, k_need)

        notes = self._generate_notes(soil_diagnosis, crop, crop_data)

        return FertilizationPlan(
            crop_name=crop.name,
            growth_stage=crop.growth_stage.value,
            nitrogen_kg_ha=round(n_this_application, 1),
            phosphorus_kg_ha=round(p_need, 1),
            potassium_kg_ha=round(k_need, 1),
            application_method=method,
            timing=timing,
            recommended_products=products,
            organic_alternatives=organic,
            estimated_cost_eur_ha=round(cost, 2),
            notes=notes,
        )

    def _adjust_for_soil_level(
        self,
        base_need: float,
        soil_value: float,
        ranges: dict[str, tuple[float, float]],
    ) -> float:
        """Ajusta la necessitat segons el nivell actual del sòl."""
        level = classify_value(soil_value, ranges)
        adjustments = {
            "molt_baix": 1.3,   # Cal 30% més
            "baix": 1.15,       # Cal 15% més
            "mitjà": 1.0,       # Normal
            "alt": 0.7,         # Reduir 30%
            "molt_alt": 0.3,    # Reduir 70%
        }
        return base_need * adjustments.get(level, 1.0)

    def _recommend_method(self, crop: CropProfile) -> tuple[str, str]:
        """Recomana mètode d'aplicació i moment."""
        if crop.irrigation_type == "degoteig":
            return "Fertirrigació", "Aplicar en cada reg, fraccionar dosi setmanal"
        elif crop.growth_stage in (GrowthStage.GERMINATION, GrowthStage.SEEDLING):
            return "Fons (pre-sembra)", "Incorporar al sòl abans de sembrar"
        elif crop.growth_stage == GrowthStage.VEGETATIVE:
            return "Cobertera", "Aplicar en superfície i incorporar amb reg/pluja"
        else:
            return "Foliar + Cobertera", "Combinar aplicació foliar amb cobertera"

    def _recommend_products(
        self, n: float, p: float, k: float
    ) -> list[str]:
        """Recomana productes comercials."""
        products: list[str] = []
        if n > 50:
            products.append(f"Nitrat amònic 33.5% ({round(n / 0.335)}  kg/ha)")
        elif n > 0:
            products.append(f"Urea 46% ({round(n / 0.46)} kg/ha)")

        if p > 20:
            products.append(
                f"Superfosfat triple 46% ({round(p * 2.29 / 0.46)} kg/ha de P2O5)"
            )

        if k > 40:
            products.append(
                f"Sulfat de potassi 50% ({round(k * 1.2 / 0.50)} kg/ha de K2O)"
            )

        if not products:
            products.append("No cal aportació addicional en aquesta fase")
        return products

    def _recommend_organic(
        self, crop: CropProfile, diagnosis: SoilDiagnosis
    ) -> list[str]:
        """Recomana alternatives ecològiques."""
        organic: list[str] = []
        if diagnosis.organic_matter_status in ("molt_baix", "baix"):
            organic.append("Compost madur (10-15 t/ha)")
        organic.append("Fems compostats de bestiar local")
        organic.append("Adob verd (veça, fajol, trèvol)")
        if crop.growth_stage == GrowthStage.VEGETATIVE:
            organic.append("Purí d'ortiga fermentat (N foliar)")
        return organic

    def _estimate_cost(self, n: float, p: float, k: float) -> float:
        """Estima el cost de fertilització per hectàrea."""
        cost_n = n * NUTRIENT_COSTS["N"]
        cost_p = p * 2.29 * NUTRIENT_COSTS["P2O5"]  # P → P2O5
        cost_k = k * 1.2 * NUTRIENT_COSTS["K2O"]    # K → K2O
        return cost_n + cost_p + cost_k

    def _generate_notes(
        self, diagnosis: SoilDiagnosis, crop: CropProfile, crop_data
    ) -> list[str]:
        """Genera notes addicionals rellevants."""
        notes: list[str] = []
        if diagnosis.ph_status in ("alcalí", "molt_alcalí"):
            notes.append(
                "pH alcalí: considerar acidificar la solució nutritiva o "
                "aplicar quelats de ferro (EDDHA) per prevenir clorosi."
            )
        if diagnosis.organic_matter_status in ("molt_baix", "baix"):
            notes.append(
                "Prioritzar aportació de matèria orgànica per millorar "
                "estructura, retenció d'aigua i activitat biològica."
            )
        if crop.previous_crop and crop.previous_crop.lower() in (
            "mongeta", "pèsol", "fava", "soja", "llenties"
        ):
            notes.append(
                f"Cultiu anterior lleguminosa ({crop.previous_crop}): "
                "reduir N un 20-30% per fixació biològica residual."
            )
        return notes

    def _default_plan(self, crop: CropProfile) -> FertilizationPlan:
        """Pla genèric quan el cultiu no està a la base de dades."""
        return FertilizationPlan(
            crop_name=crop.name,
            growth_stage=crop.growth_stage.value,
            nitrogen_kg_ha=100,
            phosphorus_kg_ha=50,
            potassium_kg_ha=80,
            application_method="Cobertera",
            timing="Fraccionar en 2-3 aplicacions",
            recommended_products=["Complex NPK 15-15-15 (500 kg/ha)"],
            organic_alternatives=["Compost madur (10-15 t/ha)"],
            estimated_cost_eur_ha=250.0,
            notes=[
                "Pla genèric. Per a recomanacions precises, afegiu el cultiu "
                "a la base de dades o proporcioneu una anàlisi de sòl."
            ],
        )
