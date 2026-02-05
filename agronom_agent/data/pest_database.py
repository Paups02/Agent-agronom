"""Base de dades de plagues i malalties amb condicions d'aparició.

Permet generar alertes fitosanitàries basades en clima i fase fenològica.
"""

from agronom_agent.models.diagnosis import PestType, SeverityLevel

# Estructura: condicions climàtiques que afavoreixen cada plaga/malaltia
PEST_CLIMATE_RULES: list[dict] = [
    # FONGS
    {
        "name": "Míldiu (Phytophthora / Plasmopara)",
        "type": PestType.FUNGUS,
        "crops": ["tomàquet", "patata", "vinya", "enciam"],
        "conditions": {
            "humidity_min": 70,
            "temp_min": 15,
            "temp_max": 25,
            "rain_trigger_mm": 10,
        },
        "symptoms": [
            "Taques olioses al feix de la fulla",
            "Pelussa blanquinosa al revers",
            "Necrosi ràpida del teixit",
        ],
        "preventive": [
            "Evitar reg per aspersió",
            "Augmentar ventilació (poda, marc de plantació)",
            "Aplicació preventiva de coure (2-3 g/L)",
        ],
        "curative": [
            "Mancozeb 80% (2 g/L)",
            "Fosetil-Al (2.5 g/L)",
            "Metalaxil + Mancozeb",
        ],
        "organic": [
            "Brou bordelès (sulfat de coure + calç)",
            "Bacillus subtilis",
            "Extracte de cua de cavall",
        ],
        "severity": SeverityLevel.HIGH,
        "action_days": 3,
    },
    {
        "name": "Oïdi (Erysiphe / Uncinula)",
        "type": PestType.FUNGUS,
        "crops": ["vinya", "tomàquet", "pebrot", "blat", "ordi", "enciam"],
        "conditions": {
            "humidity_min": 40,
            "temp_min": 20,
            "temp_max": 32,
            "rain_trigger_mm": 0,
        },
        "symptoms": [
            "Pols blanc a la superfície de les fulles",
            "Deformació de brots joves",
            "Dessecació de teixit afectat",
        ],
        "preventive": [
            "Evitar excés de nitrogen",
            "Mantenir bona ventilació",
            "Aplicar sofre preventiu",
        ],
        "curative": [
            "Sofre mullable (3-5 g/L)",
            "Tebuconazol (0.5 g/L)",
            "Azoxistrobina",
        ],
        "organic": [
            "Sofre mullable (dosi baixa)",
            "Bicarbonat de potassi (5 g/L)",
            "Llet desnatada diluïda 1:10",
        ],
        "severity": SeverityLevel.MEDIUM,
        "action_days": 5,
    },
    {
        "name": "Botritis (Botrytis cinerea)",
        "type": PestType.FUNGUS,
        "crops": ["vinya", "tomàquet", "enciam", "pebrot", "mongeta"],
        "conditions": {
            "humidity_min": 80,
            "temp_min": 10,
            "temp_max": 22,
            "rain_trigger_mm": 5,
        },
        "symptoms": [
            "Podridura gris amb esporulació",
            "Afecta fruits, flors i teixits ferits",
            "Aroma a vinagre en fruits",
        ],
        "preventive": [
            "Reduir humitat ambiental",
            "Evitar ferides als fruits",
            "No regar per aspersió durant floració",
        ],
        "curative": [
            "Iprodiona (1 g/L)",
            "Ciprodinil + Fludioxonil",
            "Pirimetanil",
        ],
        "organic": [
            "Trichoderma harzianum",
            "Bacillus subtilis",
            "Bicarbonat de potassi",
        ],
        "severity": SeverityLevel.HIGH,
        "action_days": 3,
    },
    # INSECTES
    {
        "name": "Pugó (Aphis spp. / Myzus persicae)",
        "type": PestType.INSECT,
        "crops": [
            "tomàquet", "pebrot", "enciam", "patata", "blat",
            "ordi", "mongeta", "vinya",
        ],
        "conditions": {
            "humidity_min": 30,
            "temp_min": 15,
            "temp_max": 30,
            "rain_trigger_mm": 0,
        },
        "symptoms": [
            "Colònies a l'envés de fulles i brots tendres",
            "Melassa i negrilla",
            "Fulles enrotllades i deformades",
            "Vector de virus (CMV, PVY, TSWV)",
        ],
        "preventive": [
            "Afavorir fauna auxiliar (marietes, crisopes)",
            "No abusar del nitrogen",
            "Trampes cromàtiques grogues",
        ],
        "curative": [
            "Imidacloprid (0.5 mL/L)",
            "Pimetrozina",
            "Flonicamid",
        ],
        "organic": [
            "Sabó potàssic (10-20 mL/L)",
            "Oli de neem (3-5 mL/L)",
            "Extracte de piretrina natural",
        ],
        "severity": SeverityLevel.MEDIUM,
        "action_days": 5,
    },
    {
        "name": "Tuta absoluta (minador del tomàquet)",
        "type": PestType.INSECT,
        "crops": ["tomàquet"],
        "conditions": {
            "humidity_min": 30,
            "temp_min": 18,
            "temp_max": 35,
            "rain_trigger_mm": 0,
        },
        "symptoms": [
            "Mines serpenteig a les fulles",
            "Galeries als fruits",
            "Perforacions als àpexs de tiges",
        ],
        "preventive": [
            "Trampes de feromones (detecció)",
            "Malles antiinsectes",
            "Eliminar restes vegetals",
        ],
        "curative": [
            "Spinosad",
            "Clorantraniliprol",
            "Emamectina benzoat",
        ],
        "organic": [
            "Bacillus thuringiensis var. kurstaki",
            "Nesidiocoris tenuis (depredador)",
            "Trampes de feromones massives",
        ],
        "severity": SeverityLevel.HIGH,
        "action_days": 3,
    },
    {
        "name": "Aranya roja (Tetranychus urticae)",
        "type": PestType.INSECT,
        "crops": [
            "tomàquet", "pebrot", "mongeta", "vinya",
            "taronger", "blat_de_moro",
        ],
        "conditions": {
            "humidity_min": 0,
            "temp_min": 25,
            "temp_max": 40,
            "rain_trigger_mm": 0,
        },
        "symptoms": [
            "Puntejat cloròtic a les fulles",
            "Teranyines fines a l'envés",
            "Fulles bronzejades i seques",
        ],
        "preventive": [
            "Mantenir humitat ambiental",
            "Evitar estrès hídric",
            "Afavorir Phytoseiulus persimilis",
        ],
        "curative": [
            "Abamectina (0.5 mL/L)",
            "Espirodiclofen",
            "Hexitiazox (ovicida)",
        ],
        "organic": [
            "Phytoseiulus persimilis (àcar depredador)",
            "Sabó potàssic + oli de neem",
            "Sofre mullable (efecte repel·lent)",
        ],
        "severity": SeverityLevel.MEDIUM,
        "action_days": 5,
    },
    {
        "name": "Mosca de l'oliva (Bactrocera oleae)",
        "type": PestType.INSECT,
        "crops": ["olivera"],
        "conditions": {
            "humidity_min": 40,
            "temp_min": 18,
            "temp_max": 30,
            "rain_trigger_mm": 0,
        },
        "symptoms": [
            "Picades a l'oliva (punts d'oviposició)",
            "Galeries larvàries al fruit",
            "Caiguda prematura de fruits",
            "Augment d'acidesa de l'oli",
        ],
        "preventive": [
            "Trampes McPhail amb proteïna hidrolitzada",
            "Trampes cromàtiques grogues",
            "Collita primerenca si pressió alta",
        ],
        "curative": [
            "Dimetoat (tractament cebo)",
            "Spinosad (tractament cebo)",
            "Lambda-cihalotrina",
        ],
        "organic": [
            "Argila de caolí (barrera física)",
            "Spinosad cebo (autoritzat eco)",
            "Trampes massives",
        ],
        "severity": SeverityLevel.HIGH,
        "action_days": 5,
    },
]


def get_alerts_for_crop(crop_name: str) -> list[dict]:
    """Retorna totes les amenaces potencials per a un cultiu."""
    key = crop_name.lower().strip()
    return [
        rule for rule in PEST_CLIMATE_RULES
        if key in rule["crops"]
    ]


def check_climate_trigger(
    rule: dict,
    temperature: float,
    humidity: float,
    precipitation: float,
) -> bool:
    """Comprova si les condicions climàtiques activen una alerta."""
    cond = rule["conditions"]
    temp_match = cond["temp_min"] <= temperature <= cond["temp_max"]
    humidity_match = humidity >= cond["humidity_min"]
    rain_match = (
        precipitation >= cond["rain_trigger_mm"]
        if cond["rain_trigger_mm"] > 0
        else True
    )
    return temp_match and humidity_match and rain_match
