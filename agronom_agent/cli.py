"""Interfície CLI interactiva de l'agent agronòmic.

Proporciona una experiència d'usuari rica amb menús interactius,
taules formatades i colors per a la terminal.
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from agronom_agent.models.soil import SoilAnalysis, SoilTexture
from agronom_agent.models.crop import CropProfile, CropCategory, GrowthStage
from agronom_agent.models.climate import WeatherData
from agronom_agent.services.agent import AgronomAgent
from agronom_agent.data.crop_database import list_crops, get_crop

app = typer.Typer(
    name="agronom",
    help="AgroNom Agent — Agent IA agronòmic professional",
)
console = Console()
agent = AgronomAgent()


@app.command()
def diagnostic():
    """Diagnòstic complet interactiu: sòl + cultiu + clima."""
    console.print(
        Panel(
            "[bold green]AgroNom Agent[/bold green]\n"
            "Agent IA Agronòmic Professional\n"
            "Diagnòstic integral de la teva finca",
            box=box.DOUBLE,
        )
    )

    # Recollir dades de sòl
    console.print("\n[bold cyan]1. DADES DEL SÒL[/bold cyan]")
    console.print("Introdueix les dades de l'anàlisi de sòl:\n")

    ph = typer.prompt("pH del sòl", type=float, default=7.0)
    om = typer.prompt("Matèria orgànica (%)", type=float, default=2.0)
    n = typer.prompt("Nitrogen disponible (ppm)", type=float, default=25.0)
    p = typer.prompt("Fòsfor Olsen (ppm)", type=float, default=15.0)
    k = typer.prompt("Potassi (ppm)", type=float, default=180.0)
    ec = typer.prompt("Conductivitat elèctrica (dS/m)", type=float, default=0.5)

    console.print("\nTextures disponibles: " + ", ".join(t.value for t in SoilTexture))
    texture_str = typer.prompt("Textura del sòl", default="franc")
    texture = _parse_texture(texture_str)

    soil = SoilAnalysis(
        ph=ph,
        organic_matter=om,
        nitrogen_ppm=n,
        phosphorus_ppm=p,
        potassium_ppm=k,
        texture=texture,
        electrical_conductivity=ec,
    )

    # Recollir dades de cultiu
    console.print("\n[bold cyan]2. DADES DEL CULTIU[/bold cyan]")
    console.print("Cultius disponibles: " + ", ".join(list_crops()))

    crop_name = typer.prompt("Nom del cultiu", default="tomàquet")
    area = typer.prompt("Superfície (ha)", type=float, default=1.0)

    console.print("Fases: " + ", ".join(s.value for s in GrowthStage))
    stage_str = typer.prompt("Fase fenològica", default="creixement_vegetatiu")
    stage = _parse_growth_stage(stage_str)

    irrigation = typer.prompt(
        "Tipus de reg (pluja/degoteig/aspersió/inundació)",
        default="degoteig",
    )
    previous = typer.prompt("Cultiu anterior (Enter si no saps)", default="")

    crop = CropProfile(
        name=crop_name,
        category=_infer_category(crop_name),
        growth_stage=stage,
        area_hectares=area,
        irrigation_type=irrigation,
        previous_crop=previous,
    )

    # Recollir dades climàtiques
    console.print("\n[bold cyan]3. DADES CLIMÀTIQUES[/bold cyan]")
    temp = typer.prompt("Temperatura mitjana (°C)", type=float, default=22.0)
    temp_min = typer.prompt("Temperatura mínima (°C)", type=float, default=15.0)
    temp_max = typer.prompt("Temperatura màxima (°C)", type=float, default=30.0)
    humidity = typer.prompt("Humitat relativa (%)", type=float, default=65.0)
    rain = typer.prompt("Precipitació prevista (mm)", type=float, default=0.0)
    eto = typer.prompt("ETo (mm/dia, 0 si no saps)", type=float, default=0.0)

    weather = WeatherData(
        temperature_c=temp,
        temp_min_c=temp_min,
        temp_max_c=temp_max,
        humidity_percent=humidity,
        precipitation_mm=rain,
        eto_mm=eto,
    )

    # Generar informe
    console.print("\n[bold yellow]Analitzant...[/bold yellow]\n")
    report = agent.full_diagnosis(soil, crop, weather)

    # Mostrar resultats
    _display_report(report)


@app.command()
def soil():
    """Diagnòstic ràpid de sòl."""
    console.print("[bold cyan]DIAGNÒSTIC RÀPID DE SÒL[/bold cyan]\n")

    ph = typer.prompt("pH", type=float)
    om = typer.prompt("Matèria orgànica (%)", type=float)
    n = typer.prompt("Nitrogen (ppm)", type=float)
    p = typer.prompt("Fòsfor Olsen (ppm)", type=float)
    k = typer.prompt("Potassi (ppm)", type=float)
    ec = typer.prompt("CE (dS/m)", type=float, default=0.5)

    analysis = SoilAnalysis(
        ph=ph, organic_matter=om, nitrogen_ppm=n,
        phosphorus_ppm=p, potassium_ppm=k,
        texture=SoilTexture.LOAM,
        electrical_conductivity=ec,
    )

    diagnosis = agent.quick_soil_check(analysis)

    table = Table(title="Diagnòstic de Sòl", box=box.ROUNDED)
    table.add_column("Paràmetre", style="cyan")
    table.add_column("Estat", style="yellow")
    table.add_column("Recomanació", style="green")

    table.add_row("pH", diagnosis.ph_status, diagnosis.ph_recommendation)
    table.add_row("Matèria orgànica", diagnosis.organic_matter_status, diagnosis.organic_matter_recommendation)
    table.add_row("Nitrogen", diagnosis.nitrogen_status, "")
    table.add_row("Fòsfor", diagnosis.phosphorus_status, "")
    table.add_row("Potassi", diagnosis.potassium_status, "")
    table.add_row("Fertilitat", diagnosis.overall_fertility, f"Puntuació: {diagnosis.score}/100")

    console.print(table)

    if diagnosis.limiting_factors:
        console.print("\n[bold red]Factors limitants:[/bold red]")
        for f in diagnosis.limiting_factors:
            console.print(f"  - {f}")


@app.command()
def crops():
    """Llista de cultius disponibles."""
    table = Table(title="Cultius Disponibles", box=box.ROUNDED)
    table.add_column("Cultiu", style="green")
    table.add_column("pH òptim", style="cyan")
    table.add_column("N (kg/ha)", style="yellow")
    table.add_column("P (kg/ha)", style="yellow")
    table.add_column("K (kg/ha)", style="yellow")
    table.add_column("Aigua (mm/cicle)", style="blue")

    for name in list_crops():
        crop_data = get_crop(name)
        if crop_data:
            table.add_row(
                crop_data.crop_name,
                f"{crop_data.optimal_ph_min}-{crop_data.optimal_ph_max}",
                str(crop_data.nitrogen_kg_ha),
                str(crop_data.phosphorus_kg_ha),
                str(crop_data.potassium_kg_ha),
                str(crop_data.water_mm_cycle),
            )

    console.print(table)


@app.command()
def demo():
    """Executa un diagnòstic de demostració amb dades d'exemple."""
    console.print(
        Panel(
            "[bold green]DEMOSTRACIÓ[/bold green]\n"
            "Finca de tomàquets a la comarca del Maresme\n"
            "Sòl franc-arenós, reg per degoteig, fase de floració",
            box=box.DOUBLE,
        )
    )

    soil_data = SoilAnalysis(
        ph=7.2,
        organic_matter=1.5,
        nitrogen_ppm=18.0,
        phosphorus_ppm=12.0,
        potassium_ppm=160.0,
        texture=SoilTexture.SANDY_LOAM,
        electrical_conductivity=0.8,
    )

    crop_data = CropProfile(
        name="tomàquet",
        category=CropCategory.HORTALISSES,
        variety="Montserrat",
        growth_stage=GrowthStage.FLOWERING,
        area_hectares=2.5,
        irrigation_type="degoteig",
        previous_crop="mongeta",
    )

    weather_data = WeatherData(
        temperature_c=24.0,
        temp_min_c=16.0,
        temp_max_c=32.0,
        humidity_percent=72.0,
        precipitation_mm=0.0,
        eto_mm=5.5,
    )

    report = agent.full_diagnosis(soil_data, crop_data, weather_data)
    _display_report(report)


def _display_report(report):
    """Mostra l'informe complet amb format enriquit."""
    # Puntuació del sòl
    score_color = "green" if report.soil_score >= 70 else "yellow" if report.soil_score >= 40 else "red"
    console.print(
        Panel(
            f"[bold {score_color}]Salut del Sòl: {report.soil_score}/100[/bold {score_color}]",
            title=f"Finca: {report.farm_id} | Cultiu: {report.crop_name}",
            box=box.HEAVY,
        )
    )

    # Accions prioritàries
    console.print("\n[bold red]ACCIONS PRIORITÀRIES[/bold red]")
    for i, action in enumerate(report.priority_actions, 1):
        if "[URGENT]" in action:
            console.print(f"  {i}. [bold red]{action}[/bold red]")
        elif "[IMPORTANT]" in action:
            console.print(f"  {i}. [bold yellow]{action}[/bold yellow]")
        else:
            console.print(f"  {i}. {action}")

    # Alertes fitosanitàries
    if report.active_alerts:
        console.print(f"\n[bold magenta]ALERTES FITOSANITÀRIES ({len(report.active_alerts)})[/bold magenta]")
        for alert in report.active_alerts:
            severity_color = {
                "crític": "red", "alt": "red", "mitjà": "yellow",
                "baix": "green", "informatiu": "blue",
            }.get(alert.severity.value, "white")

            console.print(
                Panel(
                    f"[bold]{alert.pest_name}[/bold]\n"
                    f"Severitat: [{severity_color}]{alert.severity.value.upper()}[/{severity_color}]\n"
                    f"Condicions: {alert.conditions_favoring}\n\n"
                    f"[bold]Símptomes:[/bold] {', '.join(alert.symptoms)}\n\n"
                    f"[bold green]Prevenció:[/bold green]\n"
                    + "\n".join(f"  - {m}" for m in alert.preventive_measures)
                    + f"\n\n[bold yellow]Tractament:[/bold yellow]\n"
                    + "\n".join(f"  - {t}" for t in alert.curative_treatments)
                    + f"\n\n[bold cyan]Alternatives eco:[/bold cyan]\n"
                    + "\n".join(f"  - {o}" for o in alert.organic_alternatives),
                    title=f"Actuar en {alert.action_deadline_days} dies",
                    border_style=severity_color,
                )
            )

    # Pla de fertilització
    if report.fertilization_plan:
        fp = report.fertilization_plan
        fert_table = Table(title="Pla de Fertilització", box=box.ROUNDED)
        fert_table.add_column("Nutrient", style="cyan")
        fert_table.add_column("kg/ha", style="yellow")
        fert_table.add_row("Nitrogen (N)", str(fp.nitrogen_kg_ha))
        fert_table.add_row("Fòsfor (P)", str(fp.phosphorus_kg_ha))
        fert_table.add_row("Potassi (K)", str(fp.potassium_kg_ha))
        fert_table.add_row("Mètode", fp.application_method)
        fert_table.add_row("Moment", fp.timing)
        fert_table.add_row("Cost estimat", f"{fp.estimated_cost_eur_ha} EUR/ha")
        console.print(fert_table)

        console.print("\n[bold]Productes recomanats:[/bold]")
        for prod in fp.recommended_products:
            console.print(f"  - {prod}")

        if fp.notes:
            console.print("\n[bold]Notes:[/bold]")
            for note in fp.notes:
                console.print(f"  - {note}")

    # Pla de reg
    if report.irrigation_plan:
        ip = report.irrigation_plan
        irr_table = Table(title="Pla de Reg", box=box.ROUNDED)
        irr_table.add_column("Paràmetre", style="cyan")
        irr_table.add_column("Valor", style="yellow")
        irr_table.add_row("Necessitat diària", f"{ip['daily_water_need_mm']} mm/dia")
        irr_table.add_row("Dosi bruta", f"{ip['gross_dose_mm']} mm")
        irr_table.add_row("Freqüència", f"Cada {ip['irrigation_frequency_days']} dies")
        irr_table.add_row("Total mensual", f"{ip['monthly_total_m3_ha']} m³/ha")
        irr_table.add_row("Eficiència sistema", f"{ip['efficiency_factor'] * 100:.0f}%")
        console.print(irr_table)

    # Estalvi
    if report.estimated_savings_eur > 0:
        console.print(
            f"\n[bold green]Estalvi estimat seguint recomanacions: "
            f"{report.estimated_savings_eur} EUR[/bold green]"
        )


def _parse_texture(text: str) -> SoilTexture:
    """Converteix text a SoilTexture."""
    text = text.lower().strip()
    for t in SoilTexture:
        if t.value == text or t.name.lower() == text:
            return t
    return SoilTexture.LOAM


def _parse_growth_stage(text: str) -> GrowthStage:
    """Converteix text a GrowthStage."""
    text = text.lower().strip()
    for s in GrowthStage:
        if s.value == text or s.name.lower() == text:
            return s
    return GrowthStage.VEGETATIVE


def _infer_category(crop_name: str) -> CropCategory:
    """Infereix la categoria d'un cultiu pel nom."""
    mapping = {
        "blat": CropCategory.CEREALS,
        "ordi": CropCategory.CEREALS,
        "blat_de_moro": CropCategory.CEREALS,
        "arròs": CropCategory.CEREALS,
        "tomàquet": CropCategory.HORTALISSES,
        "pebrot": CropCategory.HORTALISSES,
        "enciam": CropCategory.HORTALISSES,
        "patata": CropCategory.TUBERCLES,
        "olivera": CropCategory.OLIVOS,
        "vinya": CropCategory.VINYA,
        "taronger": CropCategory.CITRICS,
        "ametller": CropCategory.FRUITA,
        "mongeta": CropCategory.LLEGUMINOSES,
    }
    return mapping.get(crop_name.lower().strip(), CropCategory.HORTALISSES)


if __name__ == "__main__":
    app()
