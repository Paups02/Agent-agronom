"""Tests de l'API REST."""

import pytest
from fastapi.testclient import TestClient
from agronom_agent.api.routes import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def diagnosis_payload():
    return {
        "soil": {
            "ph": 7.0,
            "organic_matter": 2.0,
            "nitrogen_ppm": 25.0,
            "phosphorus_ppm": 15.0,
            "potassium_ppm": 180.0,
            "texture": "franc",
            "electrical_conductivity": 0.5,
        },
        "crop": {
            "name": "tomàquet",
            "category": "hortalisses",
            "growth_stage": "floració",
            "area_hectares": 2.0,
            "irrigation_type": "degoteig",
        },
        "weather": {
            "temperature_c": 22.0,
            "temp_min_c": 15.0,
            "temp_max_c": 30.0,
            "humidity_percent": 70.0,
            "precipitation_mm": 0.0,
            "eto_mm": 5.0,
        },
    }


class TestAPI:
    def test_root_serves_html(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "AgroNom" in response.text

    def test_api_info(self, client):
        response = client.get("/api")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "AgroNom Agent"

    def test_full_diagnosis(self, client, diagnosis_payload):
        response = client.post("/diagnosis", json=diagnosis_payload)
        assert response.status_code == 200
        data = response.json()
        assert "soil_score" in data
        assert "priority_actions" in data
        assert "fertilization_plan" in data

    def test_soil_diagnosis(self, client, diagnosis_payload):
        response = client.post("/soil", json=diagnosis_payload["soil"])
        assert response.status_code == 200
        data = response.json()
        assert "ph_status" in data
        assert "score" in data

    def test_pest_check(self, client, diagnosis_payload):
        payload = {
            "crop": diagnosis_payload["crop"],
            "weather": diagnosis_payload["weather"],
        }
        response = client.post("/pests", json=payload)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_irrigation_plan(self, client, diagnosis_payload):
        payload = {
            "crop": diagnosis_payload["crop"],
            "weather": diagnosis_payload["weather"],
        }
        response = client.post("/irrigation", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "daily_water_need_mm" in data

    def test_list_crops(self, client):
        response = client.get("/crops")
        assert response.status_code == 200
        data = response.json()
        assert "crops" in data
        assert len(data["crops"]) > 0

    def test_crop_info(self, client):
        response = client.get("/crops/tomàquet")
        assert response.status_code == 200
        data = response.json()
        assert "crop_name" in data
        assert data["optimal_ph_min"] > 0

    def test_crop_not_found(self, client):
        response = client.get("/crops/inexistent")
        assert response.status_code == 404

    def test_invalid_soil_ph(self, client):
        payload = {
            "ph": 15.0,  # Invalid
            "organic_matter": 2.0,
            "nitrogen_ppm": 25.0,
            "phosphorus_ppm": 15.0,
            "potassium_ppm": 180.0,
            "texture": "franc",
        }
        response = client.post("/soil", json=payload)
        assert response.status_code == 422  # Validation error

    def test_full_report_with_charts(self, client, diagnosis_payload):
        response = client.post("/report", json=diagnosis_payload)
        assert response.status_code == 200
        data = response.json()
        assert "soil_score" in data
        assert "charts" in data
        assert "economics" in data
        assert "soil_radar" in data["charts"]
        assert "npk_chart" in data["charts"]
        assert "economic_chart" in data["charts"]

    def test_report_economics_fields(self, client, diagnosis_payload):
        response = client.post("/report", json=diagnosis_payload)
        data = response.json()
        econ = data["economics"]
        assert "crop_name" in econ
        assert "roi_percent" in econ
        assert "total_savings_eur" in econ
        assert "margin_with_eur_ha" in econ
        assert econ["expected_yield_kg_ha"] > 0

    def test_chat_offline(self, client):
        response = client.post("/chat", json={
            "question": "Com puc millorar el pH del meu sòl?",
            "context": "",
            "api_key": "",
        })
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert len(data["answer"]) > 10
