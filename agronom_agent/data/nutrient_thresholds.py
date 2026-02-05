"""Llindars de nutrients per a interpretació d'anàlisis de sòl.

Basats en criteris del MAPA, IRTA i estàndards internacionals FAO.
Unitats: ppm (mg/kg) per a N, P (Olsen), K.
"""


# pH: interpretació agronòmica
PH_RANGES = {
    "molt_àcid": (0.0, 5.0),
    "àcid": (5.0, 5.8),
    "lleugerament_àcid": (5.8, 6.5),
    "neutre": (6.5, 7.3),
    "lleugerament_alcalí": (7.3, 8.0),
    "alcalí": (8.0, 8.5),
    "molt_alcalí": (8.5, 14.0),
}

PH_RECOMMENDATIONS = {
    "molt_àcid": "Encalar amb CaCO3 (2-4 t/ha). Atenció: toxicitat per alumini probable.",
    "àcid": "Encalar amb dolomita (1-2 t/ha). Revisar disponibilitat de Ca i Mg.",
    "lleugerament_àcid": "pH acceptable per a la majoria de cultius. Monitoritzar.",
    "neutre": "pH òptim. Cap correcció necessària.",
    "lleugerament_alcalí": "Acceptat. Vigilar disponibilitat de Fe, Mn, Zn.",
    "alcalí": "Aplicar sofre elemental o sulfat de ferro. Risc de clorosi fèrrica.",
    "molt_alcalí": "Risc alt de clorosi. Aplicar sofre + matèria orgànica àcida. Considerar cultius tolerants.",
}

# Matèria orgànica (%)
ORGANIC_MATTER_RANGES = {
    "molt_baix": (0.0, 1.0),
    "baix": (1.0, 1.8),
    "mitjà": (1.8, 2.5),
    "alt": (2.5, 3.5),
    "molt_alt": (3.5, 100.0),
}

ORGANIC_MATTER_RECOMMENDATIONS = {
    "molt_baix": "Crític. Aplicar compost (15-20 t/ha) + coberta vegetal. Prioritat alta.",
    "baix": "Aplicar compost (10-15 t/ha) i/o adob verd. Incorporar residus de collita.",
    "mitjà": "Acceptable. Mantenir amb aportacions anuals de 5-8 t/ha compost.",
    "alt": "Bon nivell. Mantenir pràctiques actuals.",
    "molt_alt": "Excel·lent. Possible risc d'excés de N per mineralització.",
}

# Nitrogen disponible (ppm) - Nitrogen mineral (NO3- + NH4+)
NITROGEN_RANGES = {
    "molt_baix": (0.0, 10.0),
    "baix": (10.0, 20.0),
    "mitjà": (20.0, 40.0),
    "alt": (40.0, 60.0),
    "molt_alt": (60.0, 9999.0),
}

# Fòsfor Olsen (ppm)
PHOSPHORUS_RANGES = {
    "molt_baix": (0.0, 5.0),
    "baix": (5.0, 10.0),
    "mitjà": (10.0, 20.0),
    "alt": (20.0, 40.0),
    "molt_alt": (40.0, 9999.0),
}

# Potassi disponible (ppm)
POTASSIUM_RANGES = {
    "molt_baix": (0.0, 80.0),
    "baix": (80.0, 150.0),
    "mitjà": (150.0, 250.0),
    "alt": (250.0, 400.0),
    "molt_alt": (400.0, 9999.0),
}

# Conductivitat elèctrica (dS/m) - Salinitat
SALINITY_RANGES = {
    "no_salí": (0.0, 2.0),
    "lleugerament_salí": (2.0, 4.0),
    "moderadament_salí": (4.0, 8.0),
    "fortament_salí": (8.0, 16.0),
    "molt_salí": (16.0, 9999.0),
}

SALINITY_IMPACT = {
    "no_salí": "Cap restricció. Tots els cultius possibles.",
    "lleugerament_salí": "Rendiment reduït en cultius sensibles (mongeta, enciam, maduixa).",
    "moderadament_salí": "Només cultius tolerants (ordi, remolatxa, cotó). Pèrdua 25-50%.",
    "fortament_salí": "Només cultius molt tolerants. Pèrdua >50%.",
    "molt_salí": "Cultiu no viable. Requereix recuperació del sòl.",
}


def classify_value(value: float, ranges: dict[str, tuple[float, float]]) -> str:
    """Classifica un valor numèric dins dels rangs definits."""
    for level, (low, high) in ranges.items():
        if low <= value < high:
            return level
    return list(ranges.keys())[-1]
