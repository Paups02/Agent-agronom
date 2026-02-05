"""Tests del servei d'anàlisi de sòl."""

import pytest
from agronom_agent.models.soil import SoilAnalysis, SoilTexture
from agronom_agent.services.soil_analyzer import SoilAnalyzer


@pytest.fixture
def analyzer():
    return SoilAnalyzer()


@pytest.fixture
def good_soil():
    return SoilAnalysis(
        ph=6.8,
        organic_matter=2.8,
        nitrogen_ppm=35.0,
        phosphorus_ppm=18.0,
        potassium_ppm=220.0,
        texture=SoilTexture.LOAM,
        electrical_conductivity=0.5,
    )


@pytest.fixture
def poor_soil():
    return SoilAnalysis(
        ph=8.5,
        organic_matter=0.8,
        nitrogen_ppm=8.0,
        phosphorus_ppm=4.0,
        potassium_ppm=60.0,
        texture=SoilTexture.SANDY,
        electrical_conductivity=3.5,
    )


class TestSoilAnalyzer:
    def test_good_soil_high_score(self, analyzer, good_soil):
        diagnosis = analyzer.diagnose(good_soil)
        assert diagnosis.score >= 70
        assert diagnosis.ph_status == "neutre"
        assert diagnosis.organic_matter_status == "alt"

    def test_poor_soil_low_score(self, analyzer, poor_soil):
        diagnosis = analyzer.diagnose(poor_soil)
        assert diagnosis.score < 50
        assert len(diagnosis.limiting_factors) >= 3

    def test_acidic_soil_detection(self, analyzer):
        soil = SoilAnalysis(
            ph=4.5, organic_matter=2.0, nitrogen_ppm=25.0,
            phosphorus_ppm=15.0, potassium_ppm=180.0,
            texture=SoilTexture.CLAY, electrical_conductivity=0.3,
        )
        diagnosis = analyzer.diagnose(soil)
        assert diagnosis.ph_status == "molt_àcid"
        assert "CaCO3" in diagnosis.ph_recommendation

    def test_alkaline_soil_detection(self, analyzer):
        soil = SoilAnalysis(
            ph=8.8, organic_matter=2.0, nitrogen_ppm=25.0,
            phosphorus_ppm=15.0, potassium_ppm=180.0,
            texture=SoilTexture.CLAY_LOAM, electrical_conductivity=0.3,
        )
        diagnosis = analyzer.diagnose(soil)
        assert diagnosis.ph_status == "molt_alcalí"
        assert "sofre" in diagnosis.ph_recommendation.lower()

    def test_saline_soil_warning(self, analyzer):
        soil = SoilAnalysis(
            ph=7.0, organic_matter=2.0, nitrogen_ppm=25.0,
            phosphorus_ppm=15.0, potassium_ppm=180.0,
            texture=SoilTexture.LOAM, electrical_conductivity=5.0,
        )
        diagnosis = analyzer.diagnose(soil)
        assert "tolerants" in diagnosis.salinity_risk.lower()

    def test_score_range(self, analyzer, good_soil, poor_soil):
        good_diag = analyzer.diagnose(good_soil)
        poor_diag = analyzer.diagnose(poor_soil)
        assert 0 <= good_diag.score <= 100
        assert 0 <= poor_diag.score <= 100
        assert good_diag.score > poor_diag.score

    def test_low_organic_matter_flagged(self, analyzer):
        soil = SoilAnalysis(
            ph=7.0, organic_matter=0.5, nitrogen_ppm=25.0,
            phosphorus_ppm=15.0, potassium_ppm=180.0,
            texture=SoilTexture.LOAM, electrical_conductivity=0.3,
        )
        diagnosis = analyzer.diagnose(soil)
        assert diagnosis.organic_matter_status == "molt_baix"
        assert any("orgànica" in f.lower() for f in diagnosis.limiting_factors)
