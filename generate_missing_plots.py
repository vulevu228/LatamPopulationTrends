"""
Regenerates the two charts analysis.R produces (highest_vs_lowest.png,
net_demographic_shifts.png) that were never committed to plots/. Kept as a
plain pandas/matplotlib equivalent since R isn't available in every
environment this repo gets checked out in; colors match analysis.R's ggplot
palette so the output sits consistently next to the other five charts.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

RED = "#c0392b"
BLUE = "#2980b9"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.edgecolor": "#dddddd",
})


def style_axes(ax):
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#dddddd")
    ax.tick_params(axis="y", length=0)


df = pd.read_excel("data/population_latin_america.xlsx", sheet_name="Data")
df = df[df["Country Code"].notna()].copy()

# ---------------------------------------------------------------------------
# Plot 4: Highest vs. lowest populations (2019), log scale
# ---------------------------------------------------------------------------
pop_2019 = df[["Country Name", "2019 [YR2019]"]].rename(columns={"2019 [YR2019]": "Population"})
pop_2019["Population_Millions"] = pop_2019["Population"] / 1e6
pop_2019 = pop_2019.sort_values("Population", ascending=False)
extremes = pd.concat([pop_2019.head(3), pop_2019.tail(3)]).copy()
extremes["Group"] = extremes["Population_Millions"].apply(
    lambda v: "Top 3 Largest" if v > 10 else "Bottom 3 Smallest")
extremes = extremes.sort_values("Population")

fig, ax = plt.subplots(figsize=(9, 5))
colors = extremes["Group"].map({"Top 3 Largest": RED, "Bottom 3 Smallest": BLUE})
ax.barh(extremes["Country Name"], extremes["Population"], color=colors, height=0.6)
ax.set_xscale("log")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax.set_xlabel("Total Population Count (Log Scale)")
ax.set_title("The Scale Contrast: Largest vs. Smallest Populations (2019)",
             loc="left", fontsize=12, fontweight="bold")
handles = [plt.Rectangle((0, 0), 1, 1, color=RED), plt.Rectangle((0, 0), 1, 1, color=BLUE)]
ax.legend(handles, ["Top 3 Largest", "Bottom 3 Smallest"], loc="lower right", frameon=False)
style_axes(ax)
plt.tight_layout()
plt.savefig("plots/highest_vs_lowest.png", dpi=300)
plt.close()

# ---------------------------------------------------------------------------
# Plot 6: Net demographic shifts, 2010 vs 2019 (top/bottom 5 by net change)
# ---------------------------------------------------------------------------
net = df[["Country Name", "2010 [YR2010]", "2019 [YR2019]"]].copy()
net["Net_Change_Thousands"] = (net["2019 [YR2019]"] - net["2010 [YR2010]"]) / 1000
net = net.sort_values("Net_Change_Thousands")
net_change = pd.concat([net.head(5), net.tail(5)]).drop_duplicates()

fig, ax = plt.subplots(figsize=(9, 5))
colors = net_change["Net_Change_Thousands"].apply(lambda v: BLUE if v > 0 else RED)
ax.barh(net_change["Country Name"], net_change["Net_Change_Thousands"], color=colors, height=0.6)
ax.axvline(0, color="#999999", linewidth=1)
ax.set_xlabel("Net Headcount Change (Thousands)")
ax.set_title("Net Demographic Shifts (2010 vs 2019)", loc="left", fontsize=12, fontweight="bold")
ax.text(0.99, 0.02, "Red indicates population decline", transform=ax.transAxes,
        ha="right", fontsize=9, color="#666666")
style_axes(ax)
plt.tight_layout()
plt.savefig("plots/net_demographic_shifts.png", dpi=300)
plt.close()

print("Wrote plots/highest_vs_lowest.png and plots/net_demographic_shifts.png")
