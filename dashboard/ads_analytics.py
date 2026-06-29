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
ax8.axvline(0, color="red", linestyle="--", linewidth=1.5, label="At Market")
ax8.set_xlabel("Bid Spread (Actual CPC - Expected CPC)", fontsize=9)
ax8.set_ylabel("Campaigns", fontsize=9)
ax8.set_title("Bid Spread Distribution", fontsize=10, fontweight="bold")
ax8.legend(fontsize=8)

ax9 = fig.add_subplot(gs[2, 2])
hourly = df.groupby("hour_of_day")["auction_depth"].mean()
ax9.plot(hourly.index, hourly.values, color=COLORS[0], linewidth=2, marker="o", markersize=4)
ax9.fill_between(hourly.index, hourly.values, alpha=0.15, color=COLORS[0])
ax9.set_xlabel("Hour of Day", fontsize=9)
ax9.set_ylabel("Avg Auction Depth", fontsize=9)
ax9.set_title("Auction Depth by Hour", fontsize=10, fontweight="bold")

plt.savefig("../outputs/01_executive_kpi_dashboard.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: 01_executive_kpi_dashboard.png")

# FIGURE 2 — AUCTION & BID ANALYSIS
print("Building Auction & Bid Analysis...")
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle("Auction Structure Analysis — Bid Spreads, Depth & Performance",
             fontsize=14, fontweight="bold")

ax = axes[0, 0]
df.boxplot(column="bid_spread", by="platform", ax=ax,
           boxprops=dict(color=COLORS[0]),
           medianprops=dict(color=COLORS[1], linewidth=2))
ax.set_xlabel("Platform")
ax.set_ylabel("Bid Spread")
ax.axhline(0, color="red", linestyle="--", alpha=0.5)
plt.sca(ax)
plt.title("Bid Spread by Platform", fontweight="bold")

ax = axes[0, 1]
scatter = ax.scatter(df["auction_depth"], df["CTR"] * 100,
                     c=df["ROAS"], cmap="RdYlGn", alpha=0.4, s=15, vmin=0, vmax=5)
plt.colorbar(scatter, ax=ax, label="ROAS")
ax.set_xlabel("Auction Depth (# Competing Campaigns)")
ax.set_ylabel("CTR (%)")
ax.set_title("Auction Depth vs CTR (colored by ROAS)", fontweight="bold")

ax = axes[1, 0]
df["bid_segment"] = pd.cut(df["bid_spread"],
    bins=[-np.inf, -0.5, 0, 0.5, np.inf],
    labels=["Under Bid", "Slightly Under", "Slightly Over", "Over Bid"])
seg_profit = df.groupby("bid_segment")["profit"].mean()
bars = ax.bar(seg_profit.index, seg_profit.values,
              color=[COLORS[4], COLORS[3], COLORS[1], COLORS[0]])
ax.set_xlabel("Bid Segment")
ax.set_ylabel("Avg Profit ($)")
ax.set_title("Avg Profit by Bid Segment", fontweight="bold")
ax.axhline(0, color="black", linewidth=0.8)
for bar, val in zip(bars, seg_profit.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
            f"${val:.0f}", ha="center", fontsize=9, fontweight="bold")

ax = axes[1, 1]
quarterly = df.groupby(["quarter", "platform"])["impressions"].sum().unstack()
quarterly.plot(kind="bar", ax=ax, color=COLORS[:quarterly.shape[1]], alpha=0.85, edgecolor="white")
ax.set_xlabel("Quarter")
ax.set_ylabel("Total Impressions")
ax.set_title("Supply Trend — Impressions by Quarter & Platform", fontweight="bold")
ax.legend(title="Platform", fontsize=8)
ax.set_xticklabels([f"Q{q}" for q in quarterly.index], rotation=0)

plt.tight_layout()
plt.savefig("../outputs/02_auction_bid_analysis.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: 02_auction_bid_analysis.png")

# FIGURE 3 — FEATURE ADOPTION IMPACT
print("Building Feature Adoption Impact Analysis...")
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("Feature Adoption Impact — Retargeting ON vs OFF", fontsize=14, fontweight="bold")

metrics = [("avg_CTR", "Avg CTR (%)"), ("avg_ROAS", "Avg ROAS"), ("avg_profit", "Avg Profit ($)")]
for ax, (metric, label) in zip(axes, metrics):
    vals = feature.set_index("retargeting_flag")[metric]
    bars = ax.bar(vals.index, vals.values,
                  color=[COLORS[0], COLORS[1]], alpha=0.85, edgecolor="white", width=0.5)
    ax.set_title(label, fontweight="bold")
    ax.set_ylabel(label)
    for bar, val in zip(bars, vals.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.01,
                f"{val:.2f}", ha="center", fontsize=10, fontweight="bold")
    if len(vals) == 2:
        lift = ((vals.iloc[0] - vals.iloc[1]) / abs(vals.iloc[1])) * 100
        ax.text(0.5, 0.92, f"Lift: {lift:+.1f}%", ha="center",
                transform=ax.transAxes, fontsize=10, color=COLORS[2], fontweight="bold")

plt.tight_layout()
plt.savefig("../outputs/03_feature_adoption_impact.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: 03_feature_adoption_impact.png")

# FIGURE 4 — AD REVENUE INTELLIGENCE
print("Building Ad Revenue Intelligence...")
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle("Ad Revenue & Supply Intelligence by Industry Vertical", fontsize=14, fontweight="bold")

rev_by_vertical = df.groupby("industry_vertical").agg(
    total_revenue=("revenue", "sum"), avg_roas=("ROAS", "mean"),
    total_spend=("ad_spend", "sum")).sort_values("total_revenue", ascending=True)

ax = axes[0]
bars = ax.barh(rev_by_vertical.index, rev_by_vertical["total_revenue"] / 1e6,
               color=COLORS[1], alpha=0.85)
ax.set_xlabel("Total Revenue ($M)")
ax.set_title("Revenue by Industry Vertical", fontweight="bold")
for bar, val in zip(bars, rev_by_vertical["total_revenue"] / 1e6):
    ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
            f"${val:.1f}M", va="center", fontsize=8)

ax = axes[1]
ax.scatter(rev_by_vertical["total_spend"] / 1e6, rev_by_vertical["avg_roas"],
           s=rev_by_vertical["total_revenue"] / 5000,
           color=COLORS[0], alpha=0.7, edgecolors=COLORS[1], linewidth=1.5)
for idx, row in rev_by_vertical.iterrows():
    ax.annotate(idx, (row["total_spend"] / 1e6, row["avg_roas"]),
                fontsize=7, ha="center", va="bottom")
ax.axhline(1.0, color="red", linestyle="--", alpha=0.5, label="Break-even ROAS")
ax.set_xlabel("Total Ad Spend ($M)")
ax.set_ylabel("Avg ROAS")
ax.set_title("Spend vs ROAS by Vertical (size = revenue)", fontweight="bold")
ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig("../outputs/04_revenue_intelligence.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: 04_revenue_intelligence.png")

# EXECUTIVE SUMMARY
print("\nGenerating Executive Summary...")
platform_kpis["overall_roas"] = platform_kpis["total_revenue"] / platform_kpis["total_spend"].replace(0, np.nan)
top_platform = platform_kpis.sort_values("overall_roas", ascending=False).iloc[0]
worst_platform = platform_kpis.sort_values("overall_roas").iloc[0]
retargeting_on = feature[feature["retargeting_flag"] == "Retargeting ON"].iloc[0]
retargeting_off = feature[feature["retargeting_flag"] == "Retargeting OFF"].iloc[0]
roas_lift = ((retargeting_on["avg_ROAS"] - retargeting_off["avg_ROAS"]) / retargeting_off["avg_ROAS"]) * 100
peak_hour = df.groupby("hour_of_day")["auction_depth"].mean().idxmax()

summary = f"""
AMAZON ADS AUCTION ANALYTICS — EXECUTIVE SUMMARY

DATASET: {len(df):,} campaigns | {df['platform'].nunique()} platforms | {df['industry_vertical'].nunique()} verticals

PORTFOLIO KPIs
  Total Ad Spend:       ${df['ad_spend'].sum():>12,.0f}
  Total Revenue:        ${df['revenue'].sum():>12,.0f}
  Overall ROAS:         {df['revenue'].sum()/df['ad_spend'].sum():>12.2f}x
  Avg CTR:              {df['CTR'].mean()*100:>11.2f}%
  Underperforming Rate: {df['is_underperforming'].mean()*100:>11.1f}%

AUCTION INSIGHTS
  Peak Auction Hour:    {peak_hour}:00
  Avg Bid Spread:       {df['bid_spread'].mean():>+.4f}
  Best Platform:        {top_platform['platform']} (ROAS: {top_platform['overall_roas']:.2f}x)
  Retargeting ROAS Lift: {roas_lift:+.1f}%

RECOMMENDATIONS
  1. Expand retargeting — {roas_lift:.1f}% ROAS lift justifies engineering investment
  2. Optimize ad load at {peak_hour}:00 — peak auction congestion
  3. Reallocate spend from {worst_platform['platform']} to {top_platform['platform']}
  4. Audit {df['is_underperforming'].sum():,} underperforming campaigns
"""

print(summary)
with open("../outputs/executive_summary.txt", "w") as f:
    f.write(summary)

print("\n[DONE] All analyses complete.")
