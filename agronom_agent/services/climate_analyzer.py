"""Servei d'anàlisi climàtica i càlcul de riscos.

Avalua condicions meteorològiques i genera alertes de risc
per a la gestió agrícola.
"""

from agronom_agent.models.climate import ClimateRisk, WeatherData, IrrigationPlan
from agronom_agent.models.crop import CropProfile, GrowthStage
from agronom_agent.data.crop_database import get_crop


# Coeficients de cultiu (Kc) per fase fenològica — FAO-56
KC_TABLE: dict[GrowthStage, float] = {
    GrowthStage.GERMINATION: 0.3,
    GrowthStage.SEEDLING: 0.4,
    GrowthStage.VEGETATIVE: 0.7,
    GrowthStage.FLOWERING: 1.05,
    GrowthStage.FRUIT_SET: 1.1,
    GrowthStage.RIPENING: 0.8,
    GrowthStage.HARVEST: 0.5,
    GrowthStage.DORMANCY: 0.2,
}

# Eficiència de reg per tipus
IRRIGATION_EFFICIENCY: dict[str, float] = {
    "degoteig": 0.90,
    "aspersió": 0.75,
    "inundació": 0.55,
    "pluja": 1.0,  # No hi ha sistema de reg
}


class ClimateAnalyzer:
    """Analitza condicions climàtiques i calcula necessitats hídriques."""

    def assess_risks(
        self, weather: WeatherData, crop: CropProfile
    ) -> ClimateRisk:
        """Avalua riscos climàtics per al cultiu."""
        crop_data = get_crop(crop.name)
        recommendations: list[str] = []

        # Risc de gelada
        frost_risk = "baix"
        if weather.temp_min_c <= 0:
            frost_risk = "crític"
            recommendations.append(
                f"GELADA IMMINENT ({weather.temp_min_c}°C). "
                "Protegir amb manta tèrmica, reg antigelada o calefacció."
            )
        elif weather.temp_min_c <= 3:
            frost_risk = "alt"
            recommendations.append(
                f"Risc de gelada ({weather.temp_min_c}°C). "
                "Preparar mesures de protecció."
            )
        elif weather.temp_min_c <= 5:
            frost_risk = "mitjà"

        # Estrès tèrmic
        heat_risk = "baix"
        if crop_data and weather.temp_max_c > crop_data.optimal_temp_max + 5:
            heat_risk = "crític"
            recommendations.append(
                f"Estrès tèrmic sever ({weather.temp_max_c}°C > "
                f"{crop_data.optimal_temp_max}°C òptim). "
                "Augmentar reg, aplicar ombrejat si és possible."
            )
        elif crop_data and weather.temp_max_c > crop_data.optimal_temp_max:
            heat_risk = "alt"
            recommendations.append(
                f"Temperatura per sobre de l'òptim ({weather.temp_max_c}°C). "
                "Considerar reg refrescant."
            )

        # Risc de sequera
        drought_risk = "baix"
        if weather.eto_mm > 6 and weather.precipitation_mm < 2:
            drought_risk = "alt"
            recommendations.append(
                "Demanda evaporativa alta amb precipitació nul·la. "
                "Assegurar reg adequat."
            )
        elif weather.eto_mm > 4 and weather.precipitation_mm < 5:
            drought_risk = "mitjà"

        # Pressió de malalties (humitat + temperatura)
        disease_pressure = "baix"
        if weather.humidity_percent > 80 and 15 <= weather.temperature_c <= 25:
            disease_pressure = "alt"
            recommendations.append(
                "Condicions favorables per a fongs (humitat alta + temp. suau). "
                "Vigilar míldiu, botritis, oïdi."
            )
        elif weather.humidity_percent > 65 and 18 <= weather.temperature_c <= 28:
            disease_pressure = "mitjà"

        if not recommendations:
            recommendations.append(
                "Condicions climàtiques favorables. Cap risc immediat."
            )

        return ClimateRisk(
            frost_risk=frost_risk,
            heat_stress_risk=heat_risk,
            drought_risk=drought_risk,
            disease_pressure=disease_pressure,
            recommendations=recommendations,
        )

    def calculate_irrigation(
        self, weather: WeatherData, crop: CropProfile
    ) -> IrrigationPlan:
        """Calcula necessitats de reg segons FAO-56 Penman-Monteith."""
        kc = KC_TABLE.get(crop.growth_stage, 0.7)
        eto = weather.eto_mm if weather.eto_mm > 0 else self._estimate_eto(weather)

        # ETc = ETo × Kc
        etc_mm = eto * kc

        # Descomptar precipitació efectiva (75% de la precipitació)
        effective_rain = weather.precipitation_mm * 0.75
        net_need = max(0.0, etc_mm - effective_rain)

        # Eficiència del sistema de reg
        efficiency = IRRIGATION_EFFICIENCY.get(crop.irrigation_type, 0.75)
        gross_need = net_need / efficiency if efficiency > 0 else net_need

        # Freqüència i dosi
        freq_days, dose = self._calculate_frequency(
            gross_need, crop.irrigation_type
        )

        monthly_m3 = (gross_need * 30 * 10) if gross_need > 0 else 0  # mm → m³/ha

        notes: list[str] = []
        if crop.irrigation_type == "pluja":
            notes.append(
                "Cultiu de secà. Les necessitats indiquen l'aigua que falta "
                "respecte l'òptim. Considerar reg de suport si és viable."
            )
        if crop.growth_stage in (GrowthStage.FLOWERING, GrowthStage.FRUIT_SET):
            notes.append(
                "Fase crítica. No permetre estrès hídric — reduiria "
                "quallat i mida del fruit significativament."
            )

        return IrrigationPlan(
            crop_name=crop.name,
            growth_stage=crop.growth_stage.value,
            daily_water_need_mm=round(etc_mm, 2),
            irrigation_frequency_days=freq_days,
            dose_per_irrigation_mm=round(dose, 2),
            efficiency_factor=efficiency,
            gross_dose_mm=round(gross_need, 2),
            monthly_total_m3_ha=round(monthly_m3, 1),
            notes=notes,
        )

    def _estimate_eto(self, weather: WeatherData) -> float:
        """Estimació simplificada d'ETo amb Hargreaves."""
        ra = 15.0  # Radiació extraterrestre aproximada (MJ/m²/dia)
        temp_range = max(1.0, weather.temp_max_c - weather.temp_min_c)
        eto = 0.0023 * ra * (weather.temperature_c + 17.8) * (temp_range ** 0.5)
        return max(0.0, round(eto, 2))

    def _calculate_frequency(
        self, daily_gross: float, irrigation_type: str
    ) -> tuple[int, float]:
        """Calcula freqüència i dosi de reg."""
        if daily_gross <= 0:
            return 1, 0.0
        if irrigation_type == "degoteig":
            freq = 1  # Diàriament
            dose = daily_gross
        elif irrigation_type == "aspersió":
            freq = 3
            dose = daily_gross * freq
        else:
            freq = 7
            dose = daily_gross * freq
        return freq, dose
