"""Servei d'anàlisi i diagnòstic de sòl.

Interpreta anàlisis de sòl i genera recomanacions professionals
basades en llindars agronòmics estàndard.
"""

from agronom_agent.models.soil import SoilAnalysis, SoilDiagnosis
from agronom_agent.data.nutrient_thresholds import (
    PH_RANGES,
    PH_RECOMMENDATIONS,
    ORGANIC_MATTER_RANGES,
    ORGANIC_MATTER_RECOMMENDATIONS,
    NITROGEN_RANGES,
    PHOSPHORUS_RANGES,
    POTASSIUM_RANGES,
    SALINITY_RANGES,
    SALINITY_IMPACT,
    classify_value,
)


class SoilAnalyzer:
    """Analitza mostres de sòl i genera diagnòstics professionals."""

    def diagnose(self, analysis: SoilAnalysis) -> SoilDiagnosis:
        """Genera un diagnòstic complet del sòl."""
        ph_status = classify_value(analysis.ph, PH_RANGES)
        om_status = classify_value(analysis.organic_matter, ORGANIC_MATTER_RANGES)
        n_status = classify_value(analysis.nitrogen_ppm, NITROGEN_RANGES)
        p_status = classify_value(analysis.phosphorus_ppm, PHOSPHORUS_RANGES)
        k_status = classify_value(analysis.potassium_ppm, POTASSIUM_RANGES)
        salinity = classify_value(
            analysis.electrical_conductivity, SALINITY_RANGES
        )

        limiting_factors = self._identify_limiting_factors(
            ph_status, om_status, n_status, p_status, k_status, salinity
        )

        score = self._calculate_score(
            analysis, ph_status, om_status, n_status, p_status, k_status, salinity
        )

        fertility = self._classify_fertility(score)

        return SoilDiagnosis(
            ph_status=ph_status,
            ph_recommendation=PH_RECOMMENDATIONS[ph_status],
            organic_matter_status=om_status,
            organic_matter_recommendation=ORGANIC_MATTER_RECOMMENDATIONS[om_status],
            nitrogen_status=n_status,
            phosphorus_status=p_status,
            potassium_status=k_status,
            salinity_risk=SALINITY_IMPACT[salinity],
            overall_fertility=fertility,
            limiting_factors=limiting_factors,
            score=score,
        )

    def _identify_limiting_factors(
        self,
        ph: str,
        om: str,
        n: str,
        p: str,
        k: str,
        salinity: str,
    ) -> list[str]:
        """Identifica els factors limitants del sòl."""
        factors = []
        if ph in ("molt_àcid", "àcid", "alcalí", "molt_alcalí"):
            factors.append(f"pH {ph}: limita la disponibilitat de nutrients")
        if om in ("molt_baix", "baix"):
            factors.append(
                f"Matèria orgànica {om}: estructura deficient, baixa CIC"
            )
        if n in ("molt_baix", "baix"):
            factors.append(f"Nitrogen {n}: limitarà creixement vegetatiu")
        if p in ("molt_baix", "baix"):
            factors.append(f"Fòsfor {p}: afectarà arrelament i floració")
        if k in ("molt_baix", "baix"):
            factors.append(
                f"Potassi {k}: risc de baixa qualitat de fruit i resistència"
            )
        if salinity not in ("no_salí",):
            factors.append(f"Salinitat ({salinity}): reduirà rendiment")
        return factors

    def _calculate_score(
        self,
        analysis: SoilAnalysis,
        ph: str,
        om: str,
        n: str,
        p: str,
        k: str,
        salinity: str,
    ) -> float:
        """Calcula una puntuació de salut del sòl (0-100)."""
        score = 100.0

        # pH: penalitzar extrems
        ph_penalties = {
            "molt_àcid": 30, "àcid": 15, "lleugerament_àcid": 5,
            "neutre": 0, "lleugerament_alcalí": 5, "alcalí": 15,
            "molt_alcalí": 30,
        }
        score -= ph_penalties.get(ph, 0)

        # Matèria orgànica
        om_penalties = {
            "molt_baix": 25, "baix": 15, "mitjà": 5, "alt": 0, "molt_alt": 0,
        }
        score -= om_penalties.get(om, 0)

        # Nutrients (N, P, K) — pes 10 pts cada un
        nutrient_penalties = {"molt_baix": 10, "baix": 7, "mitjà": 2, "alt": 0, "molt_alt": 0}
        score -= nutrient_penalties.get(n, 0)
        score -= nutrient_penalties.get(p, 0)
        score -= nutrient_penalties.get(k, 0)

        # Salinitat
        salinity_penalties = {
            "no_salí": 0, "lleugerament_salí": 10,
            "moderadament_salí": 25, "fortament_salí": 40,
            "molt_salí": 50,
        }
        score -= salinity_penalties.get(salinity, 0)

        return max(0.0, min(100.0, round(score, 1)))

    def _classify_fertility(self, score: float) -> str:
        """Classifica la fertilitat global."""
        if score >= 80:
            return "Alta — Sòl en excel·lents condicions"
        elif score >= 60:
            return "Mitjana-Alta — Bon potencial amb millores puntuals"
        elif score >= 40:
            return "Mitjana — Requereix correccions significatives"
        elif score >= 20:
            return "Baixa — Necessita intervenció urgent"
        else:
            return "Molt baixa — Sòl degradat, cal regeneració completa"
