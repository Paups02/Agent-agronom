"""Tests de l'agent agronòmic central (integració)."""

import pytest
from agronom_agent.models.soil import SoilAnalysis, SoilTexture
from agronom_agent.models.crop import CropProfile, CropCategory, GrowthStage
from agronom_agent.models.climate import WeatherData
from agronom_agent.services.agent import AgronomAgent


@pytest.fixture
def agent():
    return AgronomAgent()


@pytest.fixture
def demo_scenario():
    soil = SoilAnalysis(
        ph=7.2, organic_matter=1.5, nitrogen_ppm=18.0,
        phosphorus_ppm=12.0, potassium_ppm=160.0,
        texture=SoilTexture.SANDY_LOAM, electrical_conductivity=0.8,
    )
    crop = CropProfile(
        name="tomàquet",
        category=CropCategory.HORTALISSES,
        variety="Montserrat",
        growth_stage=GrowthStage.FLOWERING,
        area_hectares=2.5,
        irrigation_type="degoteig",
        previous_crop="mongeta",
    )
    weather = WeatherData(
        temperature_c=24.0, temp_min_c=16.0, temp_max_c=32.0,
        humidity_percent=72.0, precipitation_mm=0.0, eto_mm=5.5,
    )
    return soil, crop, weather


class TestAgronomAgent:
    def test_full_diagnosis_returns_report(self, agent, demo_scenario):
        soil, crop, weather = demo_scenario
        report = agent.full_diagnosis(soil, crop, weather)
        assert report.farm_id == "FARM-001"
        assert report.crop_name == "tomàquet"
        assert 0 <= report.soil_score <= 100
        assert len(report.priority_actions) > 0

    def test_report_has_fertilization_plan(self, agent, demo_scenario):
        soil, crop, weather = demo_scenario
        report = agent.full_diagnosis(soil, crop, weather)
        assert report.fertilization_plan is not None
        assert report.fertilization_plan.nitrogen_kg_ha >= 0

    def test_report_has_irrigation_plan(self, agent, demo_scenario):
        soil, crop, weather = demo_scenario
        report = agent.full_diagnosis(soil, crop, weather)
        assert report.irrigation_plan is not None
        assert report.irrigation_plan["daily_water_need_mm"] > 0

    def test_report_climate_risks(self, agent, demo_scenario):
        soil, crop, weather = demo_scenario
        report = agent.full_diagnosis(soil, crop, weather)
        assert len(report.climate_risks) > 0

    def test_quick_soil_check(self, agent, demo_scenario):
        soil, _, _ = demo_scenario
        diagnosis = agent.quick_soil_check(soil)
        assert diagnosis.score > 0
        assert diagnosis.ph_status != ""

    def test_quick_pest_check(self, agent, demo_scenario):
        _, crop, weather = demo_scenario
        alerts = agent.quick_pest_check(crop, weather)
        assert isinstance(alerts, list)

    def test_quick_irrigation(self, agent, demo_scenario):
        _, crop, weather = demo_scenario
        plan = agent.quick_irrigation(crop, weather)
        assert plan.daily_water_need_mm > 0

    def test_priority_actions_ordered(self, agent, demo_scenario):
        soil, crop, weather = demo_scenario
        report = agent.full_diagnosis(soil, crop, weather)
        # Urgent actions should come first
        urgent_indices = [
            i for i, a in enumerate(report.priority_actions)
            if "[URGENT]" in a
        ]
        non_urgent_indices = [
            i for i, a in enumerate(report.priority_actions)
            if "[URGENT]" not in a
        ]
        if urgent_indices and non_urgent_indices:
            assert max(urgent_indices) < min(non_urgent_indices)

    def test_different_crops_different_results(self, agent, demo_scenario):
        soil, _, weather = demo_scenario
        tomato = CropProfile(
            name="tomàquet", category=CropCategory.HORTALISSES,
            growth_stage=GrowthStage.FLOWERING, area_hectares=1.0,
        )
        wheat = CropProfile(
            name="blat", category=CropCategory.CEREALS,
            growth_stage=GrowthStage.FLOWERING, area_hectares=1.0,
        )
        report_tomato = agent.full_diagnosis(soil, tomato, weather)
        report_wheat = agent.full_diagnosis(soil, wheat, weather)
        # Tomato and wheat should have different fertilization plans
        assert (
            report_tomato.fertilization_plan.potassium_kg_ha
            != report_wheat.fertilization_plan.potassium_kg_ha
        )
