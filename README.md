# AgroNom Agent

Agent IA agronòmic professional que democratitza l'assessoria agrícola per a petits i mitjans agricultors.

## El Problema

El 70% dels agricultors de petita i mitjana escala prenen decisions de fertilització, reg i tractament fitosanitari basant-se en intuïció o consells genèrics. Això provoca:

- **Sobrefertilització** — 30-40% dels nutrients es perden, contaminant aqüífers
- **Pèrdues de collita** del 15-25% per diagnòstics tardans de plagues
- **Consum excessiu d'aigua** — fins a un 40% més del necessari
- **Cost d'assessoria** inaccessible (60-150€/ha/any)

## La Solució

AgroNom Agent ofereix assessoria agronòmica professional automatitzada:

| Funcionalitat | Descripció |
|---|---|
| **Diagnòstic de sòl** | Interpretació d'analítiques amb puntuació 0-100 i recomanacions |
| **Fertilització intel·ligent** | Plans personalitzats segons sòl + cultiu + fase fenològica |
| **Alertes fitosanitàries** | Detecció de riscos de plagues/malalties segons clima actual |
| **Planificació de reg** | Càlcul FAO-56 de necessitats hídriques reals |
| **Informe integral** | Accions prioritzades amb estimació d'estalvi econòmic |

## Cultius Suportats

Blat, ordi, blat de moro, arròs, tomàquet, pebrot, enciam, patata, olivera, vinya, taronger, ametller, mongeta — amb dades agronòmiques reals (MAPA, IRTA, FAO).

## Instal·lació

```bash
pip install -e ".[dev]"
```

## Ús

### CLI Interactiva

```bash
# Diagnòstic complet interactiu
python -m agronom_agent.cli diagnostic

# Demostració amb dades d'exemple
python -m agronom_agent.cli demo

# Diagnòstic ràpid de sòl
python -m agronom_agent.cli soil

# Llistar cultius disponibles
python -m agronom_agent.cli crops
```

### API REST

```bash
# Iniciar servidor
uvicorn agronom_agent.api.routes:app --reload

# Endpoints:
# POST /diagnosis  — Diagnòstic complet
# POST /soil       — Diagnòstic de sòl
# POST /pests      — Alertes fitosanitàries
# POST /irrigation — Planificació de reg
# GET  /crops      — Cultius disponibles
# GET  /crops/{nom} — Info d'un cultiu
```

Exemple de petició:

```bash
curl -X POST http://localhost:8000/diagnosis \
  -H "Content-Type: application/json" \
  -d '{
    "soil": {
      "ph": 7.2,
      "organic_matter": 1.5,
      "nitrogen_ppm": 18,
      "phosphorus_ppm": 12,
      "potassium_ppm": 160,
      "texture": "franc-arenós",
      "electrical_conductivity": 0.8
    },
    "crop": {
      "name": "tomàquet",
      "category": "hortalisses",
      "growth_stage": "floració",
      "area_hectares": 2.5,
      "irrigation_type": "degoteig"
    },
    "weather": {
      "temperature_c": 24,
      "temp_min_c": 16,
      "temp_max_c": 32,
      "humidity_percent": 72,
      "precipitation_mm": 0,
      "eto_mm": 5.5
    }
  }'
```

### Ús com a Llibreria

```python
from agronom_agent.models.soil import SoilAnalysis, SoilTexture
from agronom_agent.models.crop import CropProfile, CropCategory, GrowthStage
from agronom_agent.models.climate import WeatherData
from agronom_agent.services.agent import AgronomAgent

agent = AgronomAgent()

soil = SoilAnalysis(
    ph=7.2, organic_matter=1.5, nitrogen_ppm=18.0,
    phosphorus_ppm=12.0, potassium_ppm=160.0,
    texture=SoilTexture.SANDY_LOAM, electrical_conductivity=0.8,
)

crop = CropProfile(
    name="tomàquet", category=CropCategory.HORTALISSES,
    growth_stage=GrowthStage.FLOWERING, area_hectares=2.5,
    irrigation_type="degoteig",
)

weather = WeatherData(
    temperature_c=24.0, temp_min_c=16.0, temp_max_c=32.0,
    humidity_percent=72.0, precipitation_mm=0.0, eto_mm=5.5,
)

report = agent.full_diagnosis(soil, crop, weather)
print(f"Salut del sòl: {report.soil_score}/100")
print(f"Alertes actives: {len(report.active_alerts)}")
for action in report.priority_actions:
    print(f"  → {action}")
```

## Tests

```bash
pytest tests/ -v
```

## Arquitectura

```
agronom_agent/
├── models/          # Models Pydantic (sòl, cultiu, clima, diagnòstic)
├── data/            # Base de coneixement (cultius, nutrients, plagues)
├── services/        # Lògica de negoci
│   ├── soil_analyzer.py         # Diagnòstic de sòl
│   ├── climate_analyzer.py      # Anàlisi climàtica i reg (FAO-56)
│   ├── pest_advisor.py          # Assessoria fitosanitària
│   ├── fertilization_planner.py # Planificació de fertilització
│   └── agent.py                 # Orquestrador central
├── api/             # API REST (FastAPI)
└── cli.py           # Interfície CLI (Typer + Rich)
```

## Llicència

MIT
