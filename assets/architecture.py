"""Generate the dataxplan-mcp architecture figure (academic style).

How an AI agent calls the server, which routes to the validated dataxplan core
and returns a structured result or a chart.
Run:  python assets/architecture.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5})

INK = "#1f2d3d"
MUT = "#5b6b7b"
NEUT_F, NEUT_E = "#eef1f4", "#9aa7b3"
CORE_F, CORE_E = "#dce8f5", "#2c5f8a"
ANA_F, ANA_E = "#eef3f8", "#3b6ea5"
OPT_F, OPT_E = "#e3f1ec", "#3a8f78"
CONT_F, CONT_E = "#f7f9fb", "#c9d2db"
BAN_F, BAN_E = "#f5f7f9", "#cdd6df"
ARROW = "#7c8a99"

fig, ax = plt.subplots(figsize=(11.5, 6.3))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")


def box(x, y, w, h, text, fill, edge, fs=8.4, bold=False, tcol=INK):
    ax.add_patch(FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.35,rounding_size=1.4",
        linewidth=1.25, edgecolor=edge, facecolor=fill, zorder=2))
    ax.text(x, y, text, ha="center", va="center", color=tcol, fontsize=fs,
            fontweight="bold" if bold else "normal", zorder=5)


def arrow(x0, y0, x1, y1, color=ARROW, lw=1.2):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), zorder=1,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                shrinkA=1, shrinkB=1))


ax.text(3, 96, "dataxplan-mcp", fontsize=13.5, fontweight="bold", color=INK, ha="left")
ax.text(3, 91, "EXPLAIN-plan analysis for AI agents", fontsize=9.5, color=MUT,
        ha="left", fontstyle="italic")

# agent
box(12, 58, 18, 22, "AI agent\n\nMCP client", NEUT_F, NEUT_E, fs=8.2)

# server container
ax.add_patch(FancyBboxPatch((27, 32), 44, 50,
             boxstyle="round,pad=0.4,rounding_size=1.6",
             linewidth=1.4, edgecolor=CONT_E, facecolor=CONT_F, zorder=0))
ax.text(49, 78, "dataxplan-mcp server  (stdio)", ha="center", fontsize=9.5,
        color=MUT, fontweight="bold")
box(49, 62, 40, 16,
    "Analysis tools  (4)\n"
    "analyze_plan · compare_plans\n"
    "plan_tree · describe_inputs",
    ANA_F, ANA_E, fs=7.7)
box(49, 44, 40, 11, "Chart tools  (1)\nplan_chart", OPT_F, OPT_E, fs=7.7)

# core
box(88, 56, 20, 26, "dataxplan\n\nvalidated\nanalysis\n+ provenance",
    CORE_F, CORE_E, fs=8.4, bold=True)

# forward arrows
arrow(21.2, 58, 26.8, 58)
ax.text(24, 61.5, "call", ha="center", fontsize=7.6, color=MUT)
arrow(69.2, 62, 77.8, 58)
arrow(69.2, 44, 77.8, 54)
ax.text(74, 61, "calls", ha="center", fontsize=7.6, color=MUT)

# return lane
arrow(80, 18, 16, 18, color=OPT_E, lw=1.4)
ax.text(48, 21.5, "results to the agent:  structured JSON "
        "(metrics · findings · references)   or   PNG chart",
        ha="center", fontsize=7.7, color="#2e7d6b")
arrow(88, 43, 88, 18, color=OPT_E, lw=1.2)
arrow(12, 18, 12, 47, color=OPT_E, lw=1.2)

# banner
box(50, 8, 94, 5,
    "the agent interprets   ·   validated code computes   ·   no database connection",
    BAN_F, BAN_E, fs=8.2, tcol=MUT)

fig.savefig("assets/architecture.png", dpi=200, bbox_inches="tight",
            facecolor="white")
print("wrote assets/architecture.png")
