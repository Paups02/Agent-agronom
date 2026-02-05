"""Tests del servei de planificació de fertilització."""

import pytest
from agronom_agent.models.soil import SoilAnalysis, SoilTexture
from agronom_agent.models.crop import CropProfile, CropCategory, GrowthStage
from agronom_agent.services.soil_analyzer import SoilAnalyzer
from agronom_agent.services.fertilization_planner import FertilizationPlanner


@pytest.fixture
def planner():
    return FertilizationPlanner()


@pytest.fixture
def soil_analyzer():
    return SoilAnalyzer()


@pytest.fixture
def medium_soil():
    return SoilAnalysis(
        ph=7.0, organic_matter=2.0, nitrogen_ppm=25.0,
        phosphorus_ppm=12.0, potassium_ppm=180.0,
        texture=SoilTexture.LOAM, electrical_conductivity=0.5,
    )


@pytest.fixture
def tomato_crop():
    return CropProfile(
        name="tomàquet",
        category=CropCategory.HORTALISSES,
        growth_stage=GrowthStage.VEGETATIVE,
        area_hectares=2.0,
        irrigation_type="degoteig",
    )


class TestFertilizationPlanner:
    def test_plan_has_nutrients(self, planner, soil_analyzer, medium_soil, tomato_crop):
        diagnosis = soil_analyzer.diagnose(medium_soil)
        plan = planner.create_plan(medium_soil, diagnosis, tomato_crop)
        assert plan.nitrogen_kg_ha >= 0
        assert plan.phosphorus_kg_ha >= 0
        assert plan.potassium_kg_ha >= 0

    def test_fertigation_for_drip(self, planner, soil_analyzer, medium_soil, tomato_crop):
        diagnosis = soil_analyzer.diagnose(medium_soil)
        plan = planner.create_plan(medium_soil, diagnosis, tomato_crop)
        assert "fertirrigació" in plan.application_method.lower()

    def test_less_n_after_legume(self, planner, soil_analyzer, medium_soil):
        crop_after_legume = CropProfile(
            name="tomàquet",
            category=CropCategory.HORTALISSES,
            growth_stage=GrowthStage.VEGETATIVE,
            area_hectares=2.0,
            irrigation_type="degoteig",
            previous_crop="mongeta",
        )
        diagnosis = soil_analyzer.diagnose(medium_soil)
        plan = planner.create_plan(medium_soil, diagnosis, crop_after_legume)
        # Should have a note about reducing N
        assert any("lleguminosa" in n.lower() for n in plan.notes)

    def test_rich_soil_less_fertilizer(self, planner, soil_analyzer, tomato_crop):
        rich_soil = SoilAnalysis(
            ph=6.8, organic_matter=3.0, nitrogen_ppm=55.0,
            phosphorus_ppm=35.0, potassium_ppm=350.0,
            texture=SoilTexture.LOAM, electrical_conductivity=0.3,
        )
        poor_soil = SoilAnalysis(
            ph=6.8, organic_matter=1.0, nitrogen_ppm=8.0,
            phosphorus_ppm=4.0, potassium_ppm=70.0,
            texture=SoilTexture.SANDY, electrical_conductivity=0.3,
        )

        rich_diag = soil_analyzer.diagnose(rich_soil)
        poor_diag = soil_analyzer.diagnose(poor_soil)

        rich_plan = planner.create_plan(rich_soil, rich_diag, tomato_crop)
        poor_plan = planner.create_plan(poor_soil, poor_diag, tomato_crop)

        # Sòl pobre necessita més fertilitzant
        total_rich = rich_plan.phosphorus_kg_ha + rich_plan.potassium_kg_ha
        total_poor = poor_plan.phosphorus_kg_ha + poor_plan.potassium_kg_ha
        assert total_poor > total_rich

    def test_cost_estimation(self, planner, soil_analyzer, medium_soil, tomato_crop):
        diagnosis = soil_analyzer.diagnose(medium_soil)
        plan = planner.create_plan(medium_soil, diagnosis, tomato_crop)
        assert plan.estimated_cost_eur_ha > 0

    def test_has_organic_alternatives(self, planner, soil_analyzer, medium_soil, tomato_crop):
        diagnosis = soil_analyzer.diagnose(medium_soil)
        plan = planner.create_plan(medium_soil, diagnosis, tomato_crop)
        assert len(plan.organic_alternatives) > 0

    def test_unknown_crop_default_plan(self, planner, soil_analyzer, medium_soil):
        unknown_crop = CropProfile(
            name="quinoa_exòtica",
            category=CropCategory.CEREALS,
            growth_stage=GrowthStage.VEGETATIVE,
            area_hectares=1.0,
        )
        diagnosis = soil_analyzer.diagnose(medium_soil)
        plan = planner.create_plan(medium_soil, diagnosis, unknown_crop)
        assert plan.nitrogen_kg_ha > 0  # Retorna pla genèric
