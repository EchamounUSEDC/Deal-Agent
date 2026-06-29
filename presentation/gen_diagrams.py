"""Generate original diagrams for the Co-Gen CUP deck in the IC template palette."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Polygon
import numpy as np
import os

OUT = os.path.dirname(os.path.abspath(__file__)) + "/assets"
os.makedirs(OUT, exist_ok=True)

NAVY = "#0F113C"
RED = "#AA2226"
RED2 = "#C60000"
CREAM = "#F3F2DC"
SLATE = "#808DA0"
GREEN = "#1D3A18"
DK = "#292934"
plt.rcParams["font.family"] = "DejaVu Sans"


# ----------------------------------------------------------------------------
# 1. Combined-cycle co-generation schematic  -> "Long Term Economic Payback"
# ----------------------------------------------------------------------------
def combined_cycle():
    fig, ax = plt.subplots(figsize=(11, 6.0), dpi=200)
    ax.set_xlim(0, 100); ax.set_ylim(0, 60); ax.axis("off")
    fig.patch.set_facecolor("white")

    def block(x, y, w, h, label, fc=NAVY, tc="white", fs=11):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                     boxstyle="round,pad=0.3,rounding_size=1.2",
                     fc=fc, ec=DK, lw=1.4))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                color=tc, fontsize=fs, weight="bold", wrap=True)

    def arrow(x1, y1, x2, y2, color=RED, lw=2.6, style="-|>"):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                     mutation_scale=18, color=color, lw=lw,
                     shrinkA=2, shrinkB=2))

    block(2, 40, 17, 11, "Natural Gas\n+ Air", fc=SLATE, tc=NAVY)
    block(24, 40, 19, 11, "Gas Turbine\nGenerator  (1.5 MW)", fc=NAVY)
    block(50, 40, 19, 11, "Heat Recovery\nSteam Generator", fc=RED)
    block(76, 40, 21, 11, "Steam Turbine\nGenerator", fc=NAVY)
    block(50, 16, 19, 11, "Condenser /\nCooling Tower", fc=SLATE, tc=NAVY)
    block(76, 16, 21, 13, "CASINO RESORT\nFree Heating & Cooling\n(superheated steam)",
          fc=GREEN, fs=10)

    arrow(19, 45.5, 24, 45.5)
    arrow(43, 45.5, 50, 45.5)
    ax.text(46.5, 48.0, "1,150°F\nexhaust", ha="center", fontsize=8, color=DK)
    arrow(69, 45.5, 76, 45.5)
    ax.text(72.5, 48.5, "1,500 psi\nsteam", ha="center", fontsize=8, color=DK)
    # steam turbine down to condenser & casino
    arrow(86, 40, 86, 29, color=NAVY)
    arrow(76, 33, 69, 27, color=NAVY)
    ax.text(60, 9, "Stack discharge heat captured and delivered to the Casino "
            "Mechanical Room via steam / condensate pipe bridge",
            ha="center", fontsize=9, color=DK, style="italic")
    # electricity callout
    ax.text(33.5, 37.5, "Electricity →", ha="center", fontsize=8.5, color=RED2, weight="bold")
    ax.text(86.5, 37.5, "Electricity →", ha="center", fontsize=8.5, color=RED2, weight="bold")

    ax.set_title("Co-Generation Combined Cycle  —  one fuel, two energy products",
                 color=NAVY, fontsize=14, weight="bold", pad=12)
    fig.tight_layout()
    fig.savefig(f"{OUT}/combined_cycle.png", facecolor="white", bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------------------------------
# 2. Plume concentration / exhaust dilution  -> emissions control slide
# ----------------------------------------------------------------------------
def plume():
    fig, ax = plt.subplots(figsize=(11, 5.6), dpi=200)
    x = np.linspace(0, 150, 400)
    # concentration bands (decay with downwind distance), height axis 0..35
    H = np.linspace(0, 35, 300)
    X, Y = np.meshgrid(x, H)
    # simple gaussian-ish plume falling with distance
    plume_center = 8 + 18 * (1 - np.exp(-x / 25))
    conc = np.zeros_like(X)
    for j, xi in enumerate(x):
        c = 100000 * np.exp(-((H - plume_center[j]) ** 2) / (2 * (3 + xi / 12) ** 2)) * np.exp(-xi / 60)
        conc[:, j] = c
    levels = [0, 10, 100, 1000, 10000, 100000]
    colors = ["#9ecae1", "#fff176", "#ffb300", "#e8741e", RED2]
    ax.contourf(X, Y, conc, levels=levels, colors=colors, extend="neither")
    # plume rise line
    ax.plot(x, plume_center, color=NAVY, lw=2.6, label="Plume rise")
    # point of interest
    ax.scatter([120], [10], s=70, facecolor="white", edgecolor=NAVY, zorder=5, lw=2)
    ax.annotate("Point of Interest\n(120 ft downwind, 10 ft high)\n~1,392 PPM",
                xy=(120, 10), xytext=(70, 4), fontsize=9, color=NAVY,
                arrowprops=dict(arrowstyle="->", color=NAVY))
    ax.text(3, 33, "Stack 100,000 PPM →", fontsize=9, color="white", weight="bold")
    ax.set_xlabel("Downwind Distance (ft)", color=DK, fontsize=11)
    ax.set_ylabel("Height (ft)", color=DK, fontsize=11)
    ax.set_xlim(0, 150); ax.set_ylim(0, 35)
    ax.set_title("Exhaust Plume Dilution — SCR-controlled stack discharge",
                 color=NAVY, fontsize=14, weight="bold")
    # legend for bands
    from matplotlib.patches import Patch
    leg = [Patch(fc=RED2, label="≥ 10,000 ppm"), Patch(fc="#e8741e", label="≥ 1,000 ppm"),
           Patch(fc="#ffb300", label="≥ 100 ppm"), Patch(fc="#fff176", label="≥ 10 ppm"),
           Patch(fc="#9ecae1", label="> 0 ppm")]
    ax.legend(handles=leg, loc="upper right", fontsize=8, framealpha=0.9)
    fig.tight_layout()
    fig.savefig(f"{OUT}/plume.png", facecolor="white", bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------------------------------
# 3. Site context schematic  -> "CUP Location" (Mammoth Hill)
# ----------------------------------------------------------------------------
def site_map():
    fig, ax = plt.subplots(figsize=(11, 6.4), dpi=200)
    ax.set_xlim(0, 100); ax.set_ylim(0, 62); ax.axis("off")
    fig.patch.set_facecolor("white")
    # terrain backdrop
    ax.add_patch(Rectangle((0, 0), 100, 62, fc="#eef0e6", ec="none"))

    # Mammoth Hill CUP parcel (highlighted, cyan-ish tinted to match aerial)
    parcel = Polygon([(30, 8), (22, 30), (28, 50), (55, 56), (88, 44),
                      (92, 30), (78, 14), (50, 6)], closed=True,
                     fc="#5fe0d8", ec=NAVY, lw=2, alpha=0.45)
    ax.add_patch(parcel)
    ax.text(55, 33, "MAMMOTH HILL\nProposed CUP Site", ha="center", va="center",
            color=NAVY, fontsize=15, weight="bold")

    # CUP plant box
    ax.add_patch(FancyBboxPatch((40, 40), 16, 8,
                 boxstyle="round,pad=0.3,rounding_size=1.0", fc=NAVY, ec=DK, lw=1.4))
    ax.text(48, 44, "CUP\n(Co-Gen Plant)", ha="center", va="center", color="white",
            fontsize=9.5, weight="bold")

    # Casino box (NW, toward town)
    ax.add_patch(FancyBboxPatch((10, 50), 18, 8,
                 boxstyle="round,pad=0.3,rounding_size=1.0", fc=RED, ec=DK, lw=1.4))
    ax.text(19, 54, "CASINO RESORT\nMechanical Room", ha="center", va="center",
            color="white", fontsize=9.5, weight="bold")

    # pipe bridge (short) between CUP and Casino
    ax.add_patch(FancyArrowPatch((40, 44), (28, 53), arrowstyle="<|-|>",
                 mutation_scale=16, color=RED2, lw=3))
    ax.text(46, 49.5, "Steam / condensate\npipe bridge (minimized)",
            ha="left", fontsize=8.5, color=RED2, weight="bold")

    # streets
    for (x1, y1, x2, y2, name) in [
        (4, 5, 8, 60, "Spring St"),
        (2, 58, 40, 61, "Gregory St"),
        (8, 2, 30, 14, "Virginia Canyon Rd"),
        (88, 6, 96, 50, "Packard St"),
    ]:
        ax.plot([x1, x2], [y1, y2], color=SLATE, lw=4, solid_capstyle="round", alpha=0.7)
        ax.text((x1 + x2) / 2, (y1 + y2) / 2, name, fontsize=8, color=DK, rotation=0,
                ha="center", style="italic")

    # Idaho Springs power direction
    ax.add_patch(FancyArrowPatch((92, 8), (99, 2), arrowstyle="-|>",
                 mutation_scale=14, color=GREEN, lw=2))
    ax.text(86, 4, "Alternate power\nfrom Idaho Springs", fontsize=8, color=GREEN, ha="center")

    ax.text(50, 60.5, "CUP Location — proximity maximizes reliability, minimizes pipe-bridge length & risk",
            ha="center", fontsize=12.5, color=NAVY, weight="bold")
    fig.tight_layout()
    fig.savefig(f"{OUT}/site_map.png", facecolor="white", bbox_inches="tight")
    plt.close(fig)


combined_cycle()
plume()
site_map()
print("done:", os.listdir(OUT))
