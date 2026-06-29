# Amazon Ads Auction Analytics

An end-to-end data engineering and analytics project analyzing advertising campaign performance, auction dynamics, bid spreads, and feature adoption impact — built to mirror the analytical workflows of an Ads Scientist role.

## Project Overview

This project ingests raw advertising campaign data, runs it through a production-style ETL pipeline, models it into analytics-ready datasets, and produces deep-dive analysis across four key business areas:

- Auction structure analysis — bid spread distribution, auction depth by placement and hour
- Platform KPI intelligence — standardized performance metrics across 6 ad platforms
- Feature adoption impact — evaluating retargeting ON vs OFF on ROAS, CTR, and profit
- Ad revenue & supply intelligence — spend efficiency and revenue trends by industry vertical

## Project Structure

amazon-ads-auction-analytics/
├── pipeline/etl_pipeline.py        # ETL: ingest → validate → transform → load → log
├── sql/auction_analysis.sql        # 8 SQL queries for Redshift/Snowflake/PostgreSQL
├── dashboard/ads_analytics.py      # KPI dashboards + executive summary generation
├── data/                           # Raw campaign data (10,000 records, 41 features)
└── requirements.txt

## Key Findings

| Metric | Value |
|---|---|
| Total campaigns analyzed | 10,000 |
| Retargeting ROAS lift | +86.5% vs non-retargeting |
| Peak auction congestion hour | 2:00 AM |
| Underperforming campaigns flagged | 814 |
| Best performing platform | TikTok |

## Actionable Recommendations
1. Prioritize retargeting expansion — 86.5% ROAS lift justifies engineering investment
2. Optimize ad load at 2:00 AM — peak auction depth creates congestion
3. Reallocate budget from LinkedIn to TikTok to improve portfolio ROAS
4. Audit 814 underperforming campaigns for targeting and creative optimization

## Tech Stack
- Python 3.12, Pandas, NumPy, Matplotlib, Seaborn
- SQL — compatible with Amazon Redshift, Snowflake, PostgreSQL
- Git, AI-assisted development (Claude)

## Setup
pip install -r requirements.txt
python3 pipeline/etl_pipeline.py
python3 dashboard/ads_analytics.py
