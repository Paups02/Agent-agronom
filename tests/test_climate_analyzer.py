"""Tests del servei d'anàlisi climàtica."""

import pytest
from agronom_agent.models.climate import WeatherData
from agronom_agent.models.crop import CropProfile, CropCategory, GrowthStage
from agronom_agent.services.climate_analyzer import ClimateAnalyzer


@pytest.fixture
def analyzer():
    return ClimateAnalyzer()


@pytest.fixture
def tomato_crop():
    return CropProfile(
        name="tomàquet",
        category=CropCategory.HORTALISSES,
        growth_stage=GrowthStage.FLOWERING,
        area_hectares=2.0,
        irrigation_type="degoteig",
    )


@pytest.fixture
def mild_weather():
    return WeatherData(
        temperature_c=22.0,
        temp_min_c=15.0,
        temp_max_c=28.0,
        humidity_percent=60.0,
        precipitation_mm=0.0,
        eto_mm=5.0,
    )


class TestClimateAnalyzer:
    def test_frost_risk_detection(self, analyzer, tomato_crop):
        weather = WeatherData(
            temperature_c=3.0, temp_min_c=-2.0, temp_max_c=8.0,
            humidity_percent=80.0, precipitation_mm=0.0, eto_mm=1.0,
        )
        risk = analyzer.assess_risks(weather, tomato_crop)
        assert risk.frost_risk == "crític"

    def test_heat_stress_detection(self, analyzer, tomato_crop):
        weather = WeatherData(
            temperature_c=38.0, temp_min_c=25.0, temp_max_c=42.0,
            humidity_percent=30.0, precipitation_mm=0.0, eto_mm=8.0,
        )
        risk = analyzer.assess_risks(weather, tomato_crop)
        assert risk.heat_stress_risk in ("alt", "crític")

    def test_disease_pressure_high_humidity(self, analyzer, tomato_crop):
        weather = WeatherData(
            temperature_c=20.0, temp_min_c=16.0, temp_max_c=24.0,
            humidity_percent=90.0, precipitation_mm=15.0, eto_mm=2.0,
        )
        risk = analyzer.assess_risks(weather, tomato_crop)
        assert risk.disease_pressure == "alt"

    def test_no_risk_mild_conditions(self, analyzer, tomato_crop, mild_weather):
        risk = analyzer.assess_risks(mild_weather, tomato_crop)
        assert risk.frost_risk == "baix"
        assert risk.heat_stress_risk == "baix"

    def test_irrigation_calculation(self, analyzer, tomato_crop, mild_weather):
        plan = analyzer.calculate_irrigation(mild_weather, tomato_crop)
        assert plan.daily_water_need_mm > 0
        assert plan.efficiency_factor == 0.90  # Degoteig
        assert plan.irrigation_frequency_days == 1  # Degoteig = diari

    def test_irrigation_rainfed(self, analyzer, mild_weather):
        crop = CropProfile(
            name="blat",
            category=CropCategory.CEREALS,
            growth_stage=GrowthStage.VEGETATIVE,
            area_hectares=10.0,
            irrigation_type="pluja",
        )
        plan = analyzer.calculate_irrigation(mild_weather, crop)
        assert any("secà" in n.lower() for n in plan.notes)

    def test_critical_stage_note(self, analyzer, tomato_crop, mild_weather):
        plan = analyzer.calculate_irrigation(mild_weather, tomato_crop)
        assert any("crítica" in n.lower() for n in plan.notes)

    def test_eto_estimation(self, analyzer, tomato_crop):
        weather = WeatherData(
            temperature_c=25.0, temp_min_c=18.0, temp_max_c=32.0,
            humidity_percent=50.0, precipitation_mm=0.0, eto_mm=0.0,
        )
        plan = analyzer.calculate_irrigation(weather, tomato_crop)
        assert plan.daily_water_need_mm > 0  # Estima ETo automàticament
