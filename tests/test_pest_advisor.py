"""Tests del servei d'assessoria fitosanitària."""

import pytest
from agronom_agent.models.climate import WeatherData
from agronom_agent.models.crop import CropProfile, CropCategory, GrowthStage
from agronom_agent.services.pest_advisor import PestAdvisor


@pytest.fixture
def advisor():
    return PestAdvisor()


@pytest.fixture
def tomato_flowering():
    return CropProfile(
        name="tomàquet",
        category=CropCategory.HORTALISSES,
        growth_stage=GrowthStage.FLOWERING,
        area_hectares=1.0,
        irrigation_type="degoteig",
    )


class TestPestAdvisor:
    def test_mildew_alert_humid_conditions(self, advisor, tomato_flowering):
        weather = WeatherData(
            temperature_c=20.0, temp_min_c=15.0, temp_max_c=25.0,
            humidity_percent=85.0, precipitation_mm=12.0, eto_mm=2.0,
        )
        alerts = advisor.evaluate_risks(tomato_flowering, weather)
        pest_names = [a.pest_name for a in alerts]
        assert any("Míldiu" in name for name in pest_names)

    def test_no_alerts_dry_cold(self, advisor, tomato_flowering):
        weather = WeatherData(
            temperature_c=5.0, temp_min_c=0.0, temp_max_c=10.0,
            humidity_percent=30.0, precipitation_mm=0.0, eto_mm=1.0,
        )
        alerts = advisor.evaluate_risks(tomato_flowering, weather)
        # En condicions fredes i seques, pocs fongs s'activen
        fungal = [a for a in alerts if a.pest_type.value == "fong"]
        assert len(fungal) == 0

    def test_severity_increases_flowering(self, advisor):
        crop = CropProfile(
            name="tomàquet",
            category=CropCategory.HORTALISSES,
            growth_stage=GrowthStage.FLOWERING,
            area_hectares=1.0,
        )
        weather = WeatherData(
            temperature_c=22.0, temp_min_c=18.0, temp_max_c=26.0,
            humidity_percent=75.0, precipitation_mm=15.0, eto_mm=3.0,
        )
        alerts = advisor.evaluate_risks(crop, weather)
        # En floració, la severitat hauria d'augmentar
        for alert in alerts:
            assert alert.severity.value in ("alt", "crític", "mitjà")

    def test_alerts_sorted_by_severity(self, advisor, tomato_flowering):
        weather = WeatherData(
            temperature_c=22.0, temp_min_c=17.0, temp_max_c=27.0,
            humidity_percent=80.0, precipitation_mm=10.0, eto_mm=3.0,
        )
        alerts = advisor.evaluate_risks(tomato_flowering, weather)
        if len(alerts) >= 2:
            severity_order = {"crític": 0, "alt": 1, "mitjà": 2, "baix": 3, "informatiu": 4}
            for i in range(len(alerts) - 1):
                s1 = severity_order.get(alerts[i].severity.value, 5)
                s2 = severity_order.get(alerts[i + 1].severity.value, 5)
                assert s1 <= s2

    def test_olive_fly_alert(self, advisor):
        olive = CropProfile(
            name="olivera",
            category=CropCategory.OLIVOS,
            growth_stage=GrowthStage.RIPENING,
            area_hectares=5.0,
        )
        weather = WeatherData(
            temperature_c=24.0, temp_min_c=18.0, temp_max_c=30.0,
            humidity_percent=55.0, precipitation_mm=0.0, eto_mm=4.0,
        )
        alerts = advisor.evaluate_risks(olive, weather)
        pest_names = [a.pest_name for a in alerts]
        assert any("mosca" in name.lower() for name in pest_names)

    def test_alerts_have_treatments(self, advisor, tomato_flowering):
        weather = WeatherData(
            temperature_c=22.0, temp_min_c=17.0, temp_max_c=27.0,
            humidity_percent=80.0, precipitation_mm=10.0, eto_mm=3.0,
        )
        alerts = advisor.evaluate_risks(tomato_flowering, weather)
        for alert in alerts:
            assert len(alert.preventive_measures) > 0
            assert len(alert.curative_treatments) > 0
            assert len(alert.organic_alternatives) > 0
