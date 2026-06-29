"""
Amazon Ads Auction Analytics — KPI Dashboard & Deep-Dive Analysis
Analyzes bid spreads, auction depth, supply trends, feature adoption
impact, and ad revenue intelligence to produce executive-ready insights.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import warnings
import os

warnings.filterwarnings("ignore")

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "figure.facecolor": "white"
})
COLORS = ["#232F3E", "#FF9900", "#146EB4", "#2ECC71", "#E74C3C", "#9B59B6"]

os.makedirs("../outputs", exist_ok=True)

print("Loading analytics-ready datasets...")
df = pd.read_csv("../outputs/campaign_fact.csv")
platform_kpis = pd.read_csv("../outputs/platform_kpis.csv")
auction = pd.read_csv("../outputs/auction_analysis.csv")
feature = pd.read_csv("../outputs/feature_impact.csv")
print(f"Loaded {len(df):,} campaigns across {df['platform'].nunique()} platforms\n")

# FIGURE 1 — EXECUTIVE KPI DASHBOARD
print("Building Executive KPI Dashboard...")
fig = plt.figure(figsize=(18, 12))
fig.suptitle("Amazon Ads Auction Analytics — Executive KPI Dashboard",
             fontsize=16, fontweight="bold", y=0.98)
gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35)

kpis = [
    ("Total Campaigns", f"{len(df):,}", "#232F3E"),
    ("Total Revenue", f"${df['revenue'].sum()/1e6:.1f}M", "#FF9900"),
    ("Avg ROAS", f"{df['ROAS'].mean():.2f}x", "#146EB4"),
    ("Avg CTR", f"{df['CTR'].mean()*100:.2f}%", "#2ECC71"),
    ("Total Ad Spend", f"${df['ad_spend'].sum()/1e6:.1f}M", "#E74C3C"),
    ("Underperforming", f"{df['is_underperforming'].mean()*100:.1f}%", "#9B59B6"),
]
for i, (label, value, color) in enumerate(kpis):
    ax = fig.add_subplot(gs[0, i % 3]) if i < 3 else fig.add_subplot(gs[1, i % 3])
    ax.set_facecolor(color)
    ax.text(0.5, 0.6, value, ha="center", va="center", fontsize=22,
            fontweight="bold", color="white", transform=ax.transAxes)
    ax.text(0.5, 0.2, label, ha="center", va="center", fontsize=9,
            color="white", alpha=0.85, transform=ax.transAxes)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

ax7 = fig.add_subplot(gs[2, 0])
platform_kpis_sorted = platform_kpis.sort_values("avg_ROAS", ascending=True)
bars = ax7.barh(platform_kpis_sorted["platform"], platform_kpis_sorted["avg_ROAS"],
                color=COLORS[:len(platform_kpis_sorted)])
ax7.set_xlabel("Avg ROAS", fontsize=9)
ax7.set_title("Avg ROAS by Platform", fontsize=10, fontweight="bold")
ax7.axvline(1.0, color="red", linestyle="--", alpha=0.5, linewidth=1)
for bar, val in zip(bars, platform_kpis_sorted["avg_ROAS"]):
    ax7.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
             f"{val:.2f}x", va="center", fontsize=8)

ax8 = fig.add_subplot(gs[2, 1])
ax8.hist(df["bid_spread"].clip(-2, 2), bins=40, color=COLORS[1], alpha=0.8, edgecolor="white")
ax8.axvline(0, color="red", linestyle="--",
