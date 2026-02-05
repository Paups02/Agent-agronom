"""Agent agronòmic central — Orquestrador principal.

Coordina tots els serveis (sòl, clima, fitosanitari, fertilització)
per generar informes integrals i recomanacions prioritzades.
"""

from agronom_agent.models.soil import SoilAnalysis
from agronom_agent.models.crop import CropProfile
from agronom_agent.models.climate import WeatherData
from agronom_agent.models.diagnosis import AgentReport, PhytosanitaryAlert
from agronom_agent.services.soil_analyzer import SoilAnalyzer
from agronom_agent.services.climate_analyzer import ClimateAnalyzer
from agronom_agent.services.pest_advisor import PestAdvisor
from agronom_agent.services.fertilization_planner import FertilizationPlanner


class AgronomAgent:
    """Agent agronòmic IA que integra totes les funcionalitats."""

    def __init__(self):
        self.soil_analyzer = SoilAnalyzer()
        self.climate_analyzer = ClimateAnalyzer()
        self.pest_advisor = PestAdvisor()
        self.fertilization_planner = FertilizationPlanner()

    def full_diagnosis(
        self,
        soil: SoilAnalysis,
        crop: CropProfile,
        weather: WeatherData,
        farm_id: str = "FARM-001",
    ) -> AgentReport:
        """Genera un informe complet amb totes les recomanacions."""
        # 1. Diagnòstic de sòl
        soil_diagnosis = self.soil_analyzer.diagnose(soil)

        # 2. Anàlisi climàtica i riscos
        climate_risk = self.climate_analyzer.assess_risks(weather, crop)

        # 3. Alertes fitosanitàries
        pest_alerts = self.pest_advisor.evaluate_risks(crop, weather)

        # 4. Pla de fertilització
        fert_plan = self.fertilization_planner.create_plan(
            soil, soil_diagnosis, crop
        )

        # 5. Pla de reg
        irrigation = self.climate_analyzer.calculate_irrigation(weather, crop)

        # 6. Prioritzar accions
        priority_actions = self._prioritize_actions(
            soil_diagnosis, climate_risk, pest_alerts, fert_plan, irrigation
        )

        # 7. Estimar estalvi
        savings = self._estimate_savings(soil_diagnosis, crop, fert_plan)

        return AgentReport(
            farm_id=farm_id,
            crop_name=crop.name,
            soil_score=soil_diagnosis.score,
            climate_risks=climate_risk.recommendations,
            active_alerts=pest_alerts,
            fertilization_plan=fert_plan,
            irrigation_plan=irrigation.model_dump(),
            priority_actions=priority_actions,
            estimated_savings_eur=savings,
        )

    def quick_soil_check(self, soil: SoilAnalysis):
        """Diagnòstic ràpid només de sòl."""
        return self.soil_analyzer.diagnose(soil)

    def quick_pest_check(self, crop: CropProfile, weather: WeatherData):
        """Consulta ràpida d'alertes fitosanitàries."""
        return self.pest_advisor.evaluate_risks(crop, weather)

    def quick_irrigation(self, crop: CropProfile, weather: WeatherData):
        """Càlcul ràpid de necessitats de reg."""
        return self.climate_analyzer.calculate_irrigation(weather, crop)

    def _prioritize_actions(
        self, soil_diag, climate_risk, alerts, fert_plan, irrigation
    ) -> list[str]:
        """Genera llista d'accions prioritzades."""
        actions: list[str] = []

        # Alertes crítiques primer
        for alert in alerts:
            if alert.severity.value in ("crític", "alt"):
                actions.append(
                    f"[URGENT] {alert.pest_name}: {alert.curative_treatments[0]} "
                    f"(actuar en {alert.action_deadline_days} dies)"
                )

        # Riscos climàtics
        if climate_risk.frost_risk in ("alt", "crític"):
            actions.append("[URGENT] Protecció contra gelades imminent")
        if climate_risk.drought_risk in ("alt", "crític"):
            actions.append("[IMPORTANT] Assegurar reg — risc de sequera")

        # Fertilització
        if fert_plan.nitrogen_kg_ha > 0:
            actions.append(
                f"[PLANIFICAT] Aplicar fertilització: "
                f"{fert_plan.nitrogen_kg_ha} N, "
                f"{fert_plan.phosphorus_kg_ha} P, "
                f"{fert_plan.potassium_kg_ha} K kg/ha"
            )

        # Reg
        if irrigation.gross_dose_mm > 0:
            actions.append(
                f"[DIARI] Reg: {irrigation.gross_dose_mm} mm "
                f"cada {irrigation.irrigation_frequency_days} dies"
            )

        # Factors limitants del sòl
        for factor in soil_diag.limiting_factors:
            actions.append(f"[CORRECCIÓ] {factor}")

        if not actions:
            actions.append("Cap acció urgent. Tot en ordre.")

        return actions

    def _estimate_savings(self, soil_diag, crop, fert_plan) -> float:
        """Estima l'estalvi econòmic de seguir les recomanacions."""
        savings = 0.0

        # Estalvi per optimització de fertilització vs aplicació genèrica
        generic_cost = 350.0  # Cost mitjà sense assessoria (EUR/ha)
        savings += max(0, generic_cost - fert_plan.estimated_cost_eur_ha)

        # Estalvi per prevenció de plagues (evitar pèrdues de collita)
        if soil_diag.score < 60:
            savings += crop.area_hectares * 50  # Correcció evita pèrdues

        return round(savings, 2)
