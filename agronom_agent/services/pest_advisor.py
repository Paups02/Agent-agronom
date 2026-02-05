"""Servei d'assessoria fitosanitària intel·ligent.

Genera alertes de plagues i malalties basades en condicions
climàtiques actuals, cultiu i fase fenològica.
"""

from agronom_agent.models.climate import WeatherData
from agronom_agent.models.crop import CropProfile
from agronom_agent.models.diagnosis import (
    PhytosanitaryAlert,
    SeverityLevel,
)
from agronom_agent.data.pest_database import (
    get_alerts_for_crop,
    check_climate_trigger,
)


class PestAdvisor:
    """Assessor fitosanitari basat en regles climàtiques."""

    def evaluate_risks(
        self, crop: CropProfile, weather: WeatherData
    ) -> list[PhytosanitaryAlert]:
        """Avalua riscos fitosanitaris actius per a un cultiu."""
        potential_threats = get_alerts_for_crop(crop.name)
        active_alerts: list[PhytosanitaryAlert] = []

        for rule in potential_threats:
            is_triggered = check_climate_trigger(
                rule,
                temperature=weather.temperature_c,
                humidity=weather.humidity_percent,
                precipitation=weather.precipitation_mm,
            )
            if is_triggered:
                # Ajustar severitat segons fase fenològica
                severity = self._adjust_severity(rule, crop)

                alert = PhytosanitaryAlert(
                    pest_name=rule["name"],
                    pest_type=rule["type"],
                    severity=severity,
                    affected_crop=crop.name,
                    symptoms=rule["symptoms"],
                    conditions_favoring=self._describe_conditions(rule, weather),
                    preventive_measures=rule["preventive"],
                    curative_treatments=rule["curative"],
                    organic_alternatives=rule["organic"],
                    action_deadline_days=rule["action_days"],
                )
                active_alerts.append(alert)

        # Ordenar per severitat (crític primer)
        severity_order = {
            SeverityLevel.CRITICAL: 0,
            SeverityLevel.HIGH: 1,
            SeverityLevel.MEDIUM: 2,
            SeverityLevel.LOW: 3,
            SeverityLevel.INFO: 4,
        }
        active_alerts.sort(key=lambda a: severity_order.get(a.severity, 5))

        return active_alerts

    def _adjust_severity(self, rule: dict, crop: CropProfile) -> SeverityLevel:
        """Ajusta la severitat segons la fase fenològica."""
        base_severity = rule["severity"]
        stage = crop.growth_stage.value

        # Fases crítiques augmenten la severitat
        critical_stages = {"floració", "quallat", "maduració"}
        if stage in critical_stages and base_severity == SeverityLevel.MEDIUM:
            return SeverityLevel.HIGH
        if stage in critical_stages and base_severity == SeverityLevel.HIGH:
            return SeverityLevel.CRITICAL

        return base_severity

    def _describe_conditions(self, rule: dict, weather: WeatherData) -> str:
        """Descriu per què les condicions actuals afavoreixen la plaga."""
        cond = rule["conditions"]
        parts: list[str] = []

        parts.append(
            f"Temperatura actual {weather.temperature_c}°C "
            f"(rang favorable: {cond['temp_min']}-{cond['temp_max']}°C)"
        )
        parts.append(
            f"Humitat {weather.humidity_percent}% "
            f"(llindar: ≥{cond['humidity_min']}%)"
        )
        if cond["rain_trigger_mm"] > 0:
            parts.append(
                f"Precipitació {weather.precipitation_mm}mm "
                f"(activació: ≥{cond['rain_trigger_mm']}mm)"
            )

        return ". ".join(parts) + "."
