"""
ETL Pipeline — Amazon Ads Auction Analytics
Ingests raw advertising campaign data, validates quality,
transforms into analytics-ready datasets, and outputs
structured tables for KPI reporting and auction analysis.
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

RAW_DATA_PATH = "../data/tech_advertising_campaigns_dataset.csv"
OUTPUT_PATH = "../outputs/"
LOG_PATH = "../outputs/pipeline_log.json"

def ingest(path: str) -> pd.DataFrame:
    print("[INGEST] Loading raw campaign data...")
    df = pd.read_csv(path, parse_dates=["start_date"])
    print(f"[INGEST] Loaded {len(df):,} records | {df.shape[1]} columns")
    return df

def validate(df: pd.DataFrame) -> dict:
    print("[VALIDATE] Running data quality checks...")
    report = {
        "total_records": len(df),
        "null_counts": df.isnull().sum().to_dict(),
        "duplicate_campaign_ids": int(df["campaign_id"].duplicated().sum()),
        "negative_spend": int((df["ad_spend"] < 0).sum()),
        "negative_revenue": int((df["revenue"] < 0).sum()),
        "ctr_out_of_range": int(((df["CTR"] < 0) | (df["CTR"] > 1)).sum()),
        "timestamp": datetime.now().isoformat()
    }
    issues = sum([report["duplicate_campaign_ids"], report["negative_spend"],
                  report["negative_revenue"], report["ctr_out_of_range"]])
    print(f"[VALIDATE] {issues} data quality issues found")
    return report

def transform(df: pd.DataFrame) -> dict:
    print("[TRANSFORM] Cleaning and building analytics-ready datasets...")
    df = df.drop_duplicates(subset="campaign_id")
    df = df[(df["ad_spend"] >= 0) & (df["revenue"] >= 0)]
    df["CTR"] = df["CTR"].clip(0, 1)
    df["profit_margin"] = (df["profit"] / df["revenue"].replace(0, np.nan)).fillna(0)
    df["spend_efficiency"] = (df["revenue"] / df["ad_spend"].replace(0, np.nan)).fillna(0)
    df["bid_pressure"] = df["actual_cpc"] / df["CPC"].replace(0, np.nan).fillna(1)
    df["auction_depth"] = df.groupby(["platform", "ad_placement", "hour_of_day"])["campaign_id"].transform("count")
    df["bid_spread"] = df["actual_cpc"] - df["CPC"]
    df["is_underperforming"] = ((df["ROAS"] < 1.0) & (df["CTR"] < df["CTR"].median())).astype(int)

    campaign_fact = df[["campaign_id", "campaign_objective", "platform", "ad_placement",
        "device_type", "industry_vertical", "budget_tier", "quarter", "day_of_week",
        "hour_of_day", "impressions", "clicks", "conversions", "ad_spend", "revenue",
        "profit", "CTR", "CPC", "actual_cpc", "conversion_rate", "CPA", "ROAS",
        "bid_spread", "bid_pressure", "auction_depth", "profit_margin",
        "spend_efficiency", "is_underperforming"]].copy()

    platform_kpis = df.groupby("platform").agg(
        total_campaigns=("campaign_id", "count"), total_impressions=("impressions", "sum"),
        total_clicks=("clicks", "sum"), total_spend=("ad_spend", "sum"),
        total_revenue=("revenue", "sum"), total_profit=("profit", "sum"),
        avg_CTR=("CTR", "mean"), avg_CPC=("CPC", "mean"), avg_ROAS=("ROAS", "mean"),
        avg_bid_spread=("bid_spread", "mean"), avg_auction_depth=("auction_depth", "mean"),
        underperforming_rate=("is_underperforming", "mean")).reset_index()

    auction_analysis = df.groupby(["platform", "ad_placement", "hour_of_day"]).agg(
        auction_depth=("auction_depth", "mean"), avg_bid_spread=("bid_spread", "mean"),
        avg_actual_cpc=("actual_cpc", "mean"), avg_CTR=("CTR", "mean"),
        avg_ROAS=("ROAS", "mean"), total_spend=("ad_spend", "sum"),
        total_revenue=("revenue", "sum")).reset_index()

    feature_impact = df.groupby("retargeting_flag").agg(
        campaigns=("campaign_id", "count"), avg_CTR=("CTR", "mean"),
        avg_conversion_rate=("conversion_rate", "mean"), avg_ROAS=("ROAS", "mean"),
        avg_CPA=("CPA", "mean"), avg_profit=("profit", "mean")).reset_index()
    feature_impact["retargeting_flag"] = feature_impact["retargeting_flag"].map(
        {True: "Retargeting ON", False: "Retargeting OFF"})

    print("[TRANSFORM] Built 4 analytics-ready tables")
    return {"campaign_fact": campaign_fact, "platform_kpis": platform_kpis,
            "auction_analysis": auction_analysis, "feature_impact": feature_impact}

def load(tables: dict, output_path: str):
    print("[LOAD] Writing analytics-ready datasets...")
    os.makedirs(output_path, exist_ok=True)
    for name, df in tables.items():
        path = os.path.join(output_path, f"{name}.csv")
        df.to_csv(path, index=False)
        print(f"[LOAD] Saved {name} → {path} ({len(df):,} rows)")

def log_run(validation_report: dict, tables: dict, log_path: str):
    log = {"pipeline_run": datetime.now().isoformat(), "validation": validation_report,
           "tables_produced": {k: len(v) for k, v in tables.items()}, "status": "SUCCESS"}
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)
    print(f"[LOG] Pipeline log saved → {log_path}")

if __name__ == "__main__":
    print("=" * 55)
    print("  Amazon Ads Auction Analytics — ETL Pipeline")
    print("=" * 55)
    raw = ingest(RAW_DATA_PATH)
    validation_report = validate(raw)
    tables = transform(raw)
    load(tables, OUTPUT_PATH)
    log_run(validation_report, tables, LOG_PATH)
    print("\n[DONE] Pipeline complete. All tables ready for analysis.")
