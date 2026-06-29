-- ============================================================
-- Amazon Ads Auction Analytics — SQL Analysis Queries
-- Analyzes bid spreads, auction depth, KPI trends, and
-- feature adoption impact across the campaign dataset.
-- Compatible with: Amazon Redshift, Snowflake, PostgreSQL
-- ============================================================


-- 1. PLATFORM KPI SUMMARY
SELECT
    platform,
    COUNT(campaign_id)                          AS total_campaigns,
    SUM(impressions)                            AS total_impressions,
    ROUND(AVG(CTR) * 100, 2)                   AS avg_ctr_pct,
    ROUND(AVG(CPC), 2)                         AS avg_cpc,
    ROUND(AVG(ROAS), 2)                        AS avg_roas,
    ROUND(SUM(revenue) / NULLIF(SUM(ad_spend), 0), 2) AS overall_roas,
    ROUND(SUM(profit), 2)                      AS total_profit,
    ROUND(AVG(conversion_rate) * 100, 2)       AS avg_conversion_rate_pct
FROM campaign_fact
GROUP BY platform
ORDER BY overall_roas DESC;


-- 2. AUCTION DEPTH ANALYSIS
SELECT
    platform,
    ad_placement,
    hour_of_day,
    ROUND(AVG(auction_depth), 1)               AS avg_auction_depth,
    ROUND(AVG(bid_spread), 4)                  AS avg_bid_spread,
    ROUND(AVG(actual_cpc), 2)                  AS avg_actual_cpc,
    ROUND(AVG(CTR) * 100, 2)                   AS avg_ctr_pct,
    ROUND(AVG(ROAS), 2)                        AS avg_roas,
    COUNT(campaign_id)                          AS campaigns_in_auction
FROM campaign_fact
GROUP BY platform, ad_placement, hour_of_day
ORDER BY avg_auction_depth DESC, avg_bid_spread DESC
LIMIT 20;


-- 3. BID SPREAD DISTRIBUTION
SELECT
    CASE
        WHEN bid_spread < -0.5  THEN 'Significantly Under Bid'
        WHEN bid_spread < 0     THEN 'Slightly Under Bid'
        WHEN bid_spread = 0     THEN 'At Market'
        WHEN bid_spread <= 0.5  THEN 'Slightly Over Bid'
        ELSE 'Significantly Over Bid'
    END                                         AS bid_segment,
    COUNT(campaign_id)                          AS campaigns,
    ROUND(AVG(CTR) * 100, 2)                   AS avg_ctr_pct,
    ROUND(AVG(ROAS), 2)                        AS avg_roas,
    ROUND(AVG(conversion_rate) * 100, 2)       AS avg_conversion_rate_pct,
    ROUND(SUM(profit), 2)                      AS total_profit
FROM campaign_fact
GROUP BY bid_segment
ORDER BY total_profit DESC;


-- 4. SUPPLY & AD LOAD TRENDS BY QUARTER
SELECT
    quarter,
    platform,
    SUM(impressions)                            AS total_impressions,
    SUM(clicks)                                 AS total_clicks,
    SUM(ad_spend)                               AS total_spend,
    ROUND(AVG(CTR) * 100, 2)                   AS avg_ctr_pct,
    ROUND(AVG(auction_depth), 1)               AS avg_auction_depth,
    COUNT(campaign_id)                          AS active_campaigns,
    ROUND(SUM(revenue) / NULLIF(SUM(ad_spend), 0), 2) AS overall_roas
FROM campaign_fact
GROUP BY quarter, platform
ORDER BY quarter, platform;


-- 5. FEATURE ADOPTION IMPACT — RETARGETING
SELECT
    CASE WHEN retargeting_flag = 1 THEN 'Retargeting ON'
         ELSE 'Retargeting OFF' END             AS feature_status,
    COUNT(campaign_id)                          AS campaigns,
    ROUND(AVG(CTR) * 100, 2)                   AS avg_ctr_pct,
    ROUND(AVG(conversion_rate) * 100, 2)       AS avg_conversion_rate_pct,
    ROUND(AVG(ROAS), 2)                        AS avg_roas,
    ROUND(AVG(CPA), 2)                         AS avg_cpa,
    ROUND(AVG(profit), 2)                      AS avg_profit,
    ROUND(
        100.0 * SUM(CASE WHEN is_underperforming = 1 THEN 1 ELSE 0 END)
        / COUNT(campaign_id), 1
    )                                           AS underperforming_rate_pct
FROM campaign_fact
GROUP BY feature_status;


-- 6. UNDERPERFORMING CAMPAIGN ROOT CAUSE
SELECT
    platform,
    ad_placement,
    device_type,
    industry_vertical,
    COUNT(campaign_id)                          AS underperforming_campaigns,
    ROUND(AVG(CTR) * 100, 2)                   AS avg_ctr_pct,
    ROUND(AVG(ROAS), 2)                        AS avg_roas,
    ROUND(AVG(bid_spread), 4)                  AS avg_bid_spread,
    ROUND(AVG(auction_depth), 1)               AS avg_auction_depth
FROM campaign_fact
WHERE is_underperforming = 1
GROUP BY platform, ad_placement, device_type, industry_vertical
ORDER BY underperforming_campaigns DESC
LIMIT 15;


-- 7. AD REVENUE INTELLIGENCE — INDUSTRY VERTICAL
SELECT
    industry_vertical,
    budget_tier,
    COUNT(campaign_id)                          AS campaigns,
    ROUND(SUM(ad_spend), 2)                    AS total_spend,
    ROUND(SUM(revenue), 2)                     AS total_revenue,
    ROUND(SUM(profit), 2)                      AS total_profit,
    ROUND(AVG(ROAS), 2)                        AS avg_roas,
    ROUND(AVG(CPA), 2)                         AS avg_cpa,
    ROUND(AVG(CTR) * 100, 2)                   AS avg_ctr_pct
FROM campaign_fact
GROUP BY industry_vertical, budget_tier
ORDER BY total_revenue DESC;


-- 8. HOUR-OF-DAY AD LOAD & PERFORMANCE
SELECT
    hour_of_day,
    COUNT(campaign_id)                          AS total_campaigns,
    ROUND(AVG(auction_depth), 1)               AS avg_auction_depth,
    ROUND(AVG(CTR) * 100, 2)                   AS avg_ctr_pct,
    ROUND(AVG(ROAS), 2)                        AS avg_roas,
    ROUND(SUM(impressions), 0)                 AS total_impressions,
    ROUND(SUM(revenue), 2)                     AS total_revenue
FROM campaign_fact
GROUP BY hour_of_day
ORDER BY hour_of_day;
