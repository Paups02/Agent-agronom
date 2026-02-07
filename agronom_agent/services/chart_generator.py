"""Servei de generació de gràfics agronòmics amb matplotlib.

Genera visualitzacions professionals: radar de salut del sòl,
barres NPK, timeline de reg, i comparatives econòmiques.
Retorna imatges en format base64 per incrustar al frontend.
"""

import base64
import io
import math

import matplotlib
matplotlib.use("Agg")  # Backend sense GUI
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np


# Paleta de colors professional
COLORS = {
    "green": "#16a34a",
    "green_light": "#86efac",
    "amber": "#f59e0b",
    "red": "#ef4444",
    "blue": "#3b82f6",
    "blue_light": "#93c5fd",
    "gray": "#6b7280",
    "gray_light": "#e5e7eb",
    "dark": "#1f2937",
    "white": "#ffffff",
}


def _fig_to_base64(fig: plt.Figure) -> str:
    """Converteix una figura matplotlib a string base64 PNG."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def generate_soil_radar(diagnosis: dict) -> str:
    """Genera un gràfic radar de la salut del sòl.

    Mostra 6 indicadors: pH, MO, N, P, K, Salinitat.
    """
    # Mapejar nivells a valors numèrics (0-100)
    level_scores = {
        "molt_baix": 10, "baix": 30, "molt_àcid": 15,
        "àcid": 30, "lleugerament_àcid": 70,
        "mitjà": 55, "neutre": 95,
        "lleugerament_alcalí": 70, "alcalí": 35, "molt_alcalí": 15,
        "alt": 80, "molt_alt": 90,
        "no_salí": 95, "lleugerament_salí": 60,
        "moderadament_salí": 30, "fortament_salí": 15, "molt_salí": 5,
    }

    labels = ["pH", "Matèria\nOrgànica", "Nitrogen", "Fòsfor", "Potassi", "Salinitat"]
    values = [
        level_scores.get(diagnosis.get("ph_status", ""), 50),
        level_scores.get(diagnosis.get("organic_matter_status", ""), 50),
        level_scores.get(diagnosis.get("nitrogen_status", ""), 50),
        level_scores.get(diagnosis.get("phosphorus_status", ""), 50),
        level_scores.get(diagnosis.get("potassium_status", ""), 50),
        level_scores.get(_salinity_from_risk(diagnosis.get("salinity_risk", "")), 50),
    ]

    # Tancar el polígon
    values_closed = values + [values[0]]
    num_vars = len(labels)
    angles = [n / float(num_vars) * 2 * math.pi for n in range(num_vars)]
    angles_closed = angles + [angles[0]]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))

    # Zones de referència (vermell → groc → verd)
    theta_fill = np.linspace(0, 2 * np.pi, 100)
    ax.fill_between(theta_fill, 0, 30, alpha=0.08, color=COLORS["red"])
    ax.fill_between(theta_fill, 30, 60, alpha=0.06, color=COLORS["amber"])
    ax.fill_between(theta_fill, 60, 100, alpha=0.06, color=COLORS["green"])

    # Dades
    ax.plot(angles_closed, values_closed, "o-", linewidth=2.5,
            color=COLORS["green"], markersize=7)
    ax.fill(angles_closed, values_closed, alpha=0.2, color=COLORS["green_light"])

    # Configuració
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, size=9, fontweight="bold", color=COLORS["dark"])
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75])
    ax.set_yticklabels(["25", "50", "75"], size=7, color=COLORS["gray"])
    ax.spines["polar"].set_color(COLORS["gray_light"])
    ax.grid(color=COLORS["gray_light"], linewidth=0.5)

    score = diagnosis.get("score", 0)
    color = COLORS["green"] if score >= 70 else COLORS["amber"] if score >= 40 else COLORS["red"]
    ax.set_title(f"Salut del Sòl: {score}/100", size=14,
                 fontweight="bold", color=color, pad=20)

    return _fig_to_base64(fig)


def generate_npk_chart(fertilization_plan: dict, crop_requirements: dict | None = None) -> str:
    """Genera gràfic de barres NPK: recomanat vs necessitats del cultiu."""
    nutrients = ["Nitrogen (N)", "Fòsfor (P)", "Potassi (K)"]
    recommended = [
        fertilization_plan.get("nitrogen_kg_ha", 0),
        fertilization_plan.get("phosphorus_kg_ha", 0),
        fertilization_plan.get("potassium_kg_ha", 0),
    ]

    fig, ax = plt.subplots(figsize=(6, 4))
    x = np.arange(len(nutrients))
    width = 0.35

    if crop_requirements:
        base_needs = [
            crop_requirements.get("nitrogen_kg_ha", 0),
            crop_requirements.get("phosphorus_kg_ha", 0),
            crop_requirements.get("potassium_kg_ha", 0),
        ]
        ax.bar(x - width / 2, base_needs, width, label="Necessitat base",
               color=COLORS["blue_light"], edgecolor=COLORS["blue"], linewidth=1)
        ax.bar(x + width / 2, recommended, width, label="Recomanació ajustada",
               color=COLORS["green_light"], edgecolor=COLORS["green"], linewidth=1)
        ax.legend(frameon=False, fontsize=9)
    else:
        colors = [COLORS["blue"], COLORS["amber"], COLORS["green"]]
        bars = ax.bar(x, recommended, width * 1.5, color=colors, edgecolor="white", linewidth=1)
        for bar, val in zip(bars, recommended):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                    f"{val}", ha="center", va="bottom", fontweight="bold",
                    fontsize=10, color=COLORS["dark"])

    ax.set_xticks(x)
    ax.set_xticklabels(nutrients, fontsize=10, fontweight="bold")
    ax.set_ylabel("kg/ha", fontsize=10, color=COLORS["gray"])
    ax.set_title("Pla de Fertilització (kg/ha)", fontsize=13, fontweight="bold",
                 color=COLORS["dark"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLORS["gray_light"])
    ax.spines["bottom"].set_color(COLORS["gray_light"])

    fig.tight_layout()
    return _fig_to_base64(fig)


def generate_irrigation_chart(irrigation_plan: dict) -> str:
    """Genera gràfic de necessitats hídriques mensuals."""
    daily_need = irrigation_plan.get("daily_water_need_mm", 0)
    gross = irrigation_plan.get("gross_dose_mm", 0)
    efficiency = irrigation_plan.get("efficiency_factor", 0.75)

    # Simular variació mensual amb coeficients Kc estacionals
    months = ["Gen", "Feb", "Mar", "Abr", "Mai", "Jun",
              "Jul", "Ago", "Set", "Oct", "Nov", "Des"]
    # Corba típica mediterrània (ETo relatiu)
    eto_factors = [0.3, 0.4, 0.55, 0.7, 0.85, 1.0, 1.1, 1.05, 0.8, 0.6, 0.4, 0.3]

    monthly_need = [daily_need * f * 30 for f in eto_factors]
    monthly_gross = [gross * f * 30 for f in eto_factors]

    fig, ax = plt.subplots(figsize=(7, 4))

    ax.fill_between(range(12), monthly_gross, alpha=0.15, color=COLORS["blue"])
    ax.plot(range(12), monthly_gross, "o-", color=COLORS["blue"], linewidth=2,
            markersize=6, label=f"Dosi bruta (ef. {efficiency*100:.0f}%)")
    ax.plot(range(12), monthly_need, "s--", color=COLORS["green"], linewidth=1.5,
            markersize=5, label="Necessitat neta (ETc)")

    ax.set_xticks(range(12))
    ax.set_xticklabels(months, fontsize=9)
    ax.set_ylabel("mm/mes", fontsize=10, color=COLORS["gray"])
    ax.set_title("Necessitats Hídriques Estimades (mm/mes)", fontsize=13,
                 fontweight="bold", color=COLORS["dark"])
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLORS["gray_light"])
    ax.spines["bottom"].set_color(COLORS["gray_light"])

    fig.tight_layout()
    return _fig_to_base64(fig)


def generate_economic_chart(economic_data: dict) -> str:
    """Genera gràfic comparatiu econòmic: amb vs sense assessoria."""
    categories = ["Fertilitzants", "Fitosanitaris", "Reg", "Total"]
    without = [
        economic_data.get("fert_cost_without", 350),
        economic_data.get("phyto_cost_without", 200),
        economic_data.get("irrig_cost_without", 180),
        0,
    ]
    without[3] = sum(without[:3])

    with_advice = [
        economic_data.get("fert_cost_with", 250),
        economic_data.get("phyto_cost_with", 120),
        economic_data.get("irrig_cost_with", 130),
        0,
    ]
    with_advice[3] = sum(with_advice[:3])

    fig, ax = plt.subplots(figsize=(7, 4.5))
    x = np.arange(len(categories))
    width = 0.32

    bars1 = ax.bar(x - width / 2, without, width, label="Sense assessoria",
                   color="#fca5a5", edgecolor=COLORS["red"], linewidth=1)
    bars2 = ax.bar(x + width / 2, with_advice, width, label="Amb AgroNom",
                   color=COLORS["green_light"], edgecolor=COLORS["green"], linewidth=1)

    # Estalvi total
    saving = without[3] - with_advice[3]
    saving_pct = (saving / without[3] * 100) if without[3] > 0 else 0
    ax.annotate(
        f"Estalvi: {saving:.0f} €/ha ({saving_pct:.0f}%)",
        xy=(3, with_advice[3]), xytext=(2.2, without[3] + 30),
        fontsize=11, fontweight="bold", color=COLORS["green"],
        arrowprops=dict(arrowstyle="->", color=COLORS["green"], lw=1.5),
    )

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=10, fontweight="bold")
    ax.set_ylabel("€/ha", fontsize=10, color=COLORS["gray"])
    ax.set_title("Comparativa Econòmica (€/ha/any)", fontsize=13,
                 fontweight="bold", color=COLORS["dark"])
    ax.legend(frameon=False, fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f €"))

    fig.tight_layout()
    return _fig_to_base64(fig)


def _salinity_from_risk(risk_text: str) -> str:
    """Extreu nivell de salinitat del text de risc."""
    if "no viable" in risk_text.lower() or "molt" in risk_text.lower():
        return "molt_salí"
    if "fortament" in risk_text.lower():
        return "fortament_salí"
    if "moderadament" in risk_text.lower() or "tolerants" in risk_text.lower():
        return "moderadament_salí"
    if "sensibles" in risk_text.lower() or "lleugerament" in risk_text.lower():
        return "lleugerament_salí"
    return "no_salí"
