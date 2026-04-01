"""
Build demo dashboards in Lightdash via API.
Creates charts and assembles them into tabbed dashboards.
"""

import json
import uuid
import requests
import time

BASE = "https://maegis.newnorth.nl/api/v1"
API_KEY = "ldpat_c1eb5f2f2d993548b7d18d4fa3c4d59e32b3528f"
PROJECT = "011b6d7e-4c48-45d2-bb95-62842a41da51"
SPACE = "fca0171b-8247-4269-a93f-c8f348f756c5"
HEADERS = {"Authorization": f"ApiKey {API_KEY}", "Content-Type": "application/json"}


def create_chart(payload):
    """Create a saved chart and return its UUID."""
    resp = requests.post(f"{BASE}/projects/{PROJECT}/saved", headers=HEADERS, json=payload)
    data = resp.json()
    if data["status"] != "ok":
        print(f"  ERROR creating chart '{payload['name']}': {data}")
        return None
    chart_uuid = data["results"]["uuid"]
    print(f"  Created chart: {payload['name']} ({chart_uuid})")
    return chart_uuid


def base_query(explore, dimensions, metrics, sorts=None, limit=500, filters=None):
    """Build a standard metricQuery."""
    return {
        "exploreName": explore,
        "dimensions": dimensions,
        "metrics": metrics,
        "filters": filters or {"dimensions": {"id": "root", "and": []}, "metrics": {"id": "root", "and": []}},
        "sorts": sorts or [{"fieldId": dimensions[0], "descending": False}] if dimensions else [],
        "limit": limit,
        "tableCalculations": [],
        "additionalMetrics": [],
    }


# ── KPI CARDS ────────────────────────────────────────────────────────────────

def kpi_chart(name, explore, metric_field, style="normal"):
    return {
        "name": name,
        "tableName": explore,
        "spaceUuid": SPACE,
        "metricQuery": base_query(explore, [], [metric_field], sorts=[]),
        "chartConfig": {
            "type": "big_number",
            "config": {
                "selectedField": metric_field,
                "showComparison": False,
                "showBigNumberLabel": True,
                "style": style,
            },
        },
        "tableConfig": {"columnOrder": []},
        "pivotConfig": None,
    }


# ── LINE/BAR/AREA CHARTS ────────────────────────────────────────────────────

def time_series(name, explore, date_field, metric_fields, chart_type="line", area=False, pivot_field=None):
    dims = [date_field]
    if pivot_field:
        dims.append(pivot_field)

    series = []
    for mf in metric_fields:
        s = {
            "type": chart_type,
            "encode": {
                "xRef": {"field": date_field},
                "yRef": {"field": mf},
            },
        }
        if area:
            s["areaStyle"] = {"opacity": 0.12}
        series.append(s)

    payload = {
        "name": name,
        "tableName": explore,
        "spaceUuid": SPACE,
        "metricQuery": base_query(explore, dims, metric_fields),
        "chartConfig": {
            "type": "cartesian",
            "config": {
                "layout": {
                    "xField": date_field,
                    "yField": metric_fields,
                    "flipAxes": False,
                },
                "eChartsConfig": {
                    "series": series,
                    "legend": {"show": len(metric_fields) > 1 or pivot_field},
                },
            },
        },
        "tableConfig": {"columnOrder": []},
        "pivotConfig": {"columns": [pivot_field]} if pivot_field else None,
    }
    return payload


def bar_chart(name, explore, dim_field, metric_fields, horizontal=False, stacked=False):
    series = []
    for mf in metric_fields:
        s = {
            "type": "bar",
            "encode": {
                "xRef": {"field": dim_field if not horizontal else mf},
                "yRef": {"field": mf if not horizontal else dim_field},
            },
        }
        if stacked:
            s["stack"] = "total"
        series.append(s)

    return {
        "name": name,
        "tableName": explore,
        "spaceUuid": SPACE,
        "metricQuery": base_query(
            explore, [dim_field], metric_fields,
            sorts=[{"fieldId": metric_fields[0], "descending": True}],
        ),
        "chartConfig": {
            "type": "cartesian",
            "config": {
                "layout": {
                    "xField": dim_field if not horizontal else metric_fields[0],
                    "yField": metric_fields if not horizontal else [dim_field],
                    "flipAxes": horizontal,
                },
                "eChartsConfig": {
                    "series": series,
                    "legend": {"show": len(metric_fields) > 1},
                },
            },
        },
        "tableConfig": {"columnOrder": []},
        "pivotConfig": None,
    }


def table_chart(name, explore, dimensions, metrics, sorts=None):
    return {
        "name": name,
        "tableName": explore,
        "spaceUuid": SPACE,
        "metricQuery": base_query(explore, dimensions, metrics, sorts=sorts, limit=20),
        "chartConfig": {
            "type": "table",
            "config": {
                "showTableNames": False,
                "showResultsTotal": True,
                "columns": {},
            },
        },
        "tableConfig": {"columnOrder": []},
        "pivotConfig": None,
    }


# ── FUNNEL CHART (using horizontal stacked bar) ─────────────────────────────

def funnel_chart(name, explore, metric_fields):
    """Create a funnel using big number KPIs (Lightdash doesn't have native funnel)."""
    # We'll use a table chart showing the funnel steps
    return {
        "name": name,
        "tableName": explore,
        "spaceUuid": SPACE,
        "metricQuery": base_query(explore, [], metric_fields, sorts=[]),
        "chartConfig": {
            "type": "table",
            "config": {
                "showTableNames": False,
                "showResultsTotal": False,
                "columns": {},
            },
        },
        "tableConfig": {"columnOrder": []},
        "pivotConfig": None,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# BUILD ALL CHARTS
# ═══════════════════════════════════════════════════════════════════════════════

print("Creating charts...")

charts = {}

# ── Tab 1: Overview KPIs ─────────────────────────────────────────────────────

E = "mart_daily_performance"
charts["kpi_revenue"] = create_chart(kpi_chart(
    "Total Revenue", E, f"{E}_total_revenue"))
charts["kpi_sessions"] = create_chart(kpi_chart(
    "Total Sessions", E, f"{E}_total_sessions"))
charts["kpi_transactions"] = create_chart(kpi_chart(
    "Total Transactions", E, f"{E}_total_transactions"))
charts["kpi_conversion_rate"] = create_chart(kpi_chart(
    "Conversion Rate", E, f"{E}_conversion_rate"))

charts["revenue_over_time"] = create_chart(time_series(
    "Revenue over time", E,
    f"{E}_session_date_week",
    [f"{E}_total_revenue"],
    area=True))

charts["sessions_over_time"] = create_chart(time_series(
    "Sessions over time", E,
    f"{E}_session_date_week",
    [f"{E}_total_sessions"],
    area=True))

charts["revenue_by_channel"] = create_chart(time_series(
    "Revenue by channel", E,
    f"{E}_session_date_month",
    [f"{E}_total_revenue"],
    chart_type="bar",
    pivot_field=f"{E}_session_default_channel_grouping"))

charts["sessions_by_device"] = create_chart(bar_chart(
    "Sessions by device", E,
    f"{E}_device_category",
    [f"{E}_total_sessions", f"{E}_total_revenue"]))

charts["top_landing_pages"] = create_chart(table_chart(
    "Top landing pages", E,
    [f"{E}_landing_page_path"],
    [f"{E}_total_sessions", f"{E}_total_revenue", f"{E}_conversion_rate"],
    sorts=[{"fieldId": f"{E}_total_sessions", "descending": True}]))

charts["performance_by_country"] = create_chart(table_chart(
    "Performance by country", E,
    [f"{E}_country"],
    [f"{E}_total_sessions", f"{E}_total_revenue", f"{E}_conversion_rate", f"{E}_avg_order_value"],
    sorts=[{"fieldId": f"{E}_total_revenue", "descending": True}]))


# ── Tab 2: Ecommerce Funnel ─────────────────────────────────────────────────

F = "mart_ecommerce_funnel"
charts["kpi_funnel_sessions"] = create_chart(kpi_chart(
    "Funnel - Sessions", F, f"{F}_total_sessions"))
charts["kpi_funnel_purchases"] = create_chart(kpi_chart(
    "Funnel - Purchases", F, f"{F}_total_purchases"))
charts["kpi_funnel_conv"] = create_chart(kpi_chart(
    "Funnel - Conversion Rate", F, f"{F}_overall_conversion_rate"))
charts["kpi_funnel_aov"] = create_chart(kpi_chart(
    "Funnel - AOV", F, f"{F}_avg_order_value"))

# Funnel steps as bar chart
charts["funnel_steps"] = create_chart(bar_chart(
    "Conversion funnel steps", F,
    f"{F}_channel_grouping",
    [f"{F}_total_sessions", f"{F}_total_product_views", f"{F}_total_add_to_cart",
     f"{F}_total_begin_checkout", f"{F}_total_purchases"]))

charts["funnel_by_device"] = create_chart(bar_chart(
    "Funnel conversion by device", F,
    f"{F}_device_category",
    [f"{F}_total_sessions", f"{F}_total_product_views", f"{F}_total_add_to_cart",
     f"{F}_total_begin_checkout", f"{F}_total_purchases"]))

charts["funnel_rates_over_time"] = create_chart(time_series(
    "Conversion rates over time", F,
    f"{F}_event_date_month",
    [f"{F}_product_view_rate", f"{F}_add_to_cart_rate",
     f"{F}_overall_conversion_rate"]))

charts["funnel_revenue_by_channel"] = create_chart(time_series(
    "Revenue by channel (funnel)", F,
    f"{F}_event_date_month",
    [f"{F}_total_revenue"],
    chart_type="bar",
    pivot_field=f"{F}_channel_grouping"))


# ── Tab 3: Google Ads ────────────────────────────────────────────────────────

G = "mart_google_ads_performance"
charts["kpi_ads_cost"] = create_chart(kpi_chart(
    "Ad Spend", G, f"{G}_total_cost"))
charts["kpi_ads_roas"] = create_chart(kpi_chart(
    "ROAS", G, f"{G}_roas"))
charts["kpi_ads_conversions"] = create_chart(kpi_chart(
    "Ad Conversions", G, f"{G}_total_conversions"))
charts["kpi_ads_cpc"] = create_chart(kpi_chart(
    "CPC", G, f"{G}_cpc"))

charts["ads_cost_over_time"] = create_chart(time_series(
    "Ad spend over time", G,
    f"{G}_report_date_week",
    [f"{G}_total_cost", f"{G}_total_conversion_value"],
    area=True))

charts["ads_roas_over_time"] = create_chart(time_series(
    "ROAS over time", G,
    f"{G}_report_date_month",
    [f"{G}_roas"]))

charts["ads_by_campaign"] = create_chart(table_chart(
    "Campaign performance", G,
    [f"{G}_campaign_name"],
    [f"{G}_total_cost", f"{G}_total_clicks", f"{G}_total_conversions",
     f"{G}_total_conversion_value", f"{G}_roas", f"{G}_cpc"],
    sorts=[{"fieldId": f"{G}_total_cost", "descending": True}]))

charts["ads_by_type"] = create_chart(bar_chart(
    "Performance by campaign type", G,
    f"{G}_channel_type",
    [f"{G}_total_cost", f"{G}_total_conversion_value"]))


# ── Tab 4: SEO ───────────────────────────────────────────────────────────────

S = "mart_seo_performance"
charts["kpi_seo_clicks"] = create_chart(kpi_chart(
    "Organic Clicks", S, f"{S}_total_clicks"))
charts["kpi_seo_impressions"] = create_chart(kpi_chart(
    "Organic Impressions", S, f"{S}_total_impressions"))
charts["kpi_seo_ctr"] = create_chart(kpi_chart(
    "Organic CTR", S, f"{S}_ctr"))
charts["kpi_seo_position"] = create_chart(kpi_chart(
    "Avg Position", S, f"{S}_avg_position"))

charts["seo_clicks_over_time"] = create_chart(time_series(
    "Organic clicks over time", S,
    f"{S}_data_date_week",
    [f"{S}_total_clicks"],
    area=True))

charts["seo_impressions_over_time"] = create_chart(time_series(
    "Organic impressions over time", S,
    f"{S}_data_date_week",
    [f"{S}_total_impressions"],
    area=True))

charts["seo_top_queries"] = create_chart(table_chart(
    "Top search queries", S,
    [f"{S}_query"],
    [f"{S}_total_clicks", f"{S}_total_impressions", f"{S}_ctr", f"{S}_avg_position"],
    sorts=[{"fieldId": f"{S}_total_clicks", "descending": True}]))

P = "mart_seo_pages"
charts["seo_top_pages"] = create_chart(table_chart(
    "Top pages by clicks", P,
    [f"{P}_url"],
    [f"{P}_total_clicks", f"{P}_total_impressions", f"{P}_ctr", f"{P}_avg_position"],
    sorts=[{"fieldId": f"{P}_total_clicks", "descending": True}]))


# ── Tab 5: Customer Retention ────────────────────────────────────────────────

R = "mart_customer_retention"
charts["kpi_new_customers"] = create_chart(kpi_chart(
    "Total New Customers", R, f"{R}_total_new_customers"))
charts["kpi_retention_rate"] = create_chart(kpi_chart(
    "Avg Retention Rate", R, f"{R}_avg_retention_rate"))
charts["kpi_cohort_revenue"] = create_chart(kpi_chart(
    "Total Cohort Revenue", R, f"{R}_total_cohort_revenue"))
charts["kpi_rev_per_customer"] = create_chart(kpi_chart(
    "Revenue per Returning Customer", R, f"{R}_avg_revenue_per_customer"))

charts["retention_by_cohort"] = create_chart(table_chart(
    "Retention by cohort", R,
    [f"{R}_cohort_month", f"{R}_months_since_first_purchase"],
    [f"{R}_total_returning_customers", f"{R}_avg_retention_rate", f"{R}_total_cohort_revenue"],
    sorts=[{"fieldId": f"{R}_cohort_month", "descending": False}]))

charts["retention_curve"] = create_chart(time_series(
    "Retention curve by cohort", R,
    f"{R}_months_since_first_purchase",
    [f"{R}_avg_retention_rate"],
    pivot_field=f"{R}_cohort_month"))

charts["cohort_revenue_over_time"] = create_chart(time_series(
    "Cohort revenue over time", R,
    f"{R}_months_since_first_purchase",
    [f"{R}_total_cohort_revenue"],
    chart_type="bar",
    pivot_field=f"{R}_cohort_month"))


# ═══════════════════════════════════════════════════════════════════════════════
# BUILD DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

print("\nCreating dashboard...")

# Tab UUIDs
tab_overview = str(uuid.uuid4())
tab_funnel = str(uuid.uuid4())
tab_ads = str(uuid.uuid4())
tab_seo = str(uuid.uuid4())
tab_retention = str(uuid.uuid4())

def tile(chart_key, x, y, w, h, tab):
    if charts.get(chart_key) is None:
        return None
    return {
        "type": "saved_chart",
        "properties": {"savedChartUuid": charts[chart_key]},
        "x": x, "y": y, "w": w, "h": h,
        "tabUuid": tab,
    }

def md_tile(content, x, y, w, h, tab):
    return {
        "type": "markdown",
        "properties": {"title": "", "content": content},
        "x": x, "y": y, "w": w, "h": h,
        "tabUuid": tab,
    }

tiles = []

# ── Overview tab ──
y = 0
for chart_key, x_pos in [("kpi_revenue", 0), ("kpi_sessions", 9), ("kpi_transactions", 18), ("kpi_conversion_rate", 27)]:
    t = tile(chart_key, x_pos, y, 9, 3, tab_overview)
    if t: tiles.append(t)

y = 3
t = tile("revenue_over_time", 0, y, 18, 7, tab_overview)
if t: tiles.append(t)
t = tile("sessions_over_time", 18, y, 18, 7, tab_overview)
if t: tiles.append(t)

y = 10
t = tile("revenue_by_channel", 0, y, 36, 8, tab_overview)
if t: tiles.append(t)

y = 18
tiles.append(md_tile("### Breakdown", 0, y, 36, 1, tab_overview))

y = 19
t = tile("sessions_by_device", 0, y, 12, 7, tab_overview)
if t: tiles.append(t)
t = tile("performance_by_country", 12, y, 24, 7, tab_overview)
if t: tiles.append(t)

y = 26
t = tile("top_landing_pages", 0, y, 36, 10, tab_overview)
if t: tiles.append(t)

# ── Funnel tab ──
y = 0
for chart_key, x_pos in [("kpi_funnel_sessions", 0), ("kpi_funnel_purchases", 9), ("kpi_funnel_conv", 18), ("kpi_funnel_aov", 27)]:
    t = tile(chart_key, x_pos, y, 9, 3, tab_funnel)
    if t: tiles.append(t)

y = 3
t = tile("funnel_steps", 0, y, 18, 8, tab_funnel)
if t: tiles.append(t)
t = tile("funnel_by_device", 18, y, 18, 8, tab_funnel)
if t: tiles.append(t)

y = 11
t = tile("funnel_rates_over_time", 0, y, 18, 7, tab_funnel)
if t: tiles.append(t)
t = tile("funnel_revenue_by_channel", 18, y, 18, 7, tab_funnel)
if t: tiles.append(t)

# ── Google Ads tab ──
y = 0
for chart_key, x_pos in [("kpi_ads_cost", 0), ("kpi_ads_roas", 9), ("kpi_ads_conversions", 18), ("kpi_ads_cpc", 27)]:
    t = tile(chart_key, x_pos, y, 9, 3, tab_ads)
    if t: tiles.append(t)

y = 3
t = tile("ads_cost_over_time", 0, y, 18, 7, tab_ads)
if t: tiles.append(t)
t = tile("ads_roas_over_time", 18, y, 18, 7, tab_ads)
if t: tiles.append(t)

y = 10
t = tile("ads_by_type", 0, y, 12, 7, tab_ads)
if t: tiles.append(t)
t = tile("ads_by_campaign", 12, y, 24, 10, tab_ads)
if t: tiles.append(t)

# ── SEO tab ──
y = 0
for chart_key, x_pos in [("kpi_seo_clicks", 0), ("kpi_seo_impressions", 9), ("kpi_seo_ctr", 18), ("kpi_seo_position", 27)]:
    t = tile(chart_key, x_pos, y, 9, 3, tab_seo)
    if t: tiles.append(t)

y = 3
t = tile("seo_clicks_over_time", 0, y, 18, 7, tab_seo)
if t: tiles.append(t)
t = tile("seo_impressions_over_time", 18, y, 18, 7, tab_seo)
if t: tiles.append(t)

y = 10
t = tile("seo_top_queries", 0, y, 36, 10, tab_seo)
if t: tiles.append(t)

y = 20
t = tile("seo_top_pages", 0, y, 36, 10, tab_seo)
if t: tiles.append(t)

# ── Retention tab ──
y = 0
for chart_key, x_pos in [("kpi_new_customers", 0), ("kpi_retention_rate", 9), ("kpi_cohort_revenue", 18), ("kpi_rev_per_customer", 27)]:
    t = tile(chart_key, x_pos, y, 9, 3, tab_retention)
    if t: tiles.append(t)

y = 3
t = tile("retention_curve", 0, y, 18, 8, tab_retention)
if t: tiles.append(t)
t = tile("cohort_revenue_over_time", 18, y, 18, 8, tab_retention)
if t: tiles.append(t)

y = 11
t = tile("retention_by_cohort", 0, y, 36, 12, tab_retention)
if t: tiles.append(t)


# Filter out None tiles
tiles = [t for t in tiles if t is not None]

dashboard_payload = {
    "name": "Ecommerce Dashboard - Your Brand",
    "description": "Complete ecommerce analytics dashboard showcasing website performance, conversion funnel, Google Ads, SEO, and customer retention.",
    "spaceUuid": SPACE,
    "tabs": [
        {"uuid": tab_overview, "name": "Overview", "order": 0},
        {"uuid": tab_funnel, "name": "Conversion Funnel", "order": 1},
        {"uuid": tab_ads, "name": "Google Ads", "order": 2},
        {"uuid": tab_seo, "name": "SEO", "order": 3},
        {"uuid": tab_retention, "name": "Customer Retention", "order": 4},
    ],
    "tiles": tiles,
}

resp = requests.post(f"{BASE}/projects/{PROJECT}/dashboards", headers=HEADERS, json=dashboard_payload)
data = resp.json()

if data["status"] == "ok":
    dash_uuid = data["results"]["uuid"]
    print(f"\nDashboard created: {dash_uuid}")
    print(f"URL: https://maegis.newnorth.nl/projects/{PROJECT}/dashboards/{dash_uuid}")
else:
    print(f"\nERROR creating dashboard: {json.dumps(data, indent=2)}")


# ── Add date filter to dashboard ─────────────────────────────────────────────

print("\nAdding date filter...")

# Get dashboard details
dash_data = requests.get(f"{BASE}/dashboards/{dash_uuid}", headers=HEADERS).json()["results"]

# Build tile targets for each tile
tile_targets = {}
explore_date_fields = {
    "mart_daily_performance": "mart_daily_performance_session_date_day",
    "mart_ecommerce_funnel": "mart_ecommerce_funnel_event_date_day",
    "mart_google_ads_performance": "mart_google_ads_performance_report_date_day",
    "mart_seo_performance": "mart_seo_performance_data_date_day",
    "mart_seo_pages": "mart_seo_pages_data_date_day",
    "mart_customer_retention": None,  # no date filter for retention
}

for t in dash_data["tiles"]:
    if t["type"] == "saved_chart" and t["properties"].get("savedChartUuid"):
        # Get chart to find its explore
        chart_resp = requests.get(f"{BASE}/saved/{t['properties']['savedChartUuid']}", headers=HEADERS).json()
        if chart_resp["status"] == "ok":
            explore = chart_resp["results"]["tableName"]
            date_field = explore_date_fields.get(explore)
            if date_field:
                tile_targets[t["uuid"]] = {
                    "fieldId": date_field,
                    "tableName": explore,
                }
            else:
                tile_targets[t["uuid"]] = False

filters = {
    "dimensions": [{
        "id": str(uuid.uuid4()),
        "target": {
            "fieldId": "mart_daily_performance_session_date_day",
            "tableName": "mart_daily_performance",
        },
        "operator": "inThePast",
        "values": [12],
        "settings": {"unitOfTime": "months", "completed": False},
        "label": "Date range",
        "disabled": False,
        "tileTargets": tile_targets,
    }],
    "metrics": [],
    "tableCalculations": [],
}

resp = requests.patch(f"{BASE}/dashboards/{dash_uuid}", headers=HEADERS, json={
    "name": dash_data["name"],
    "filters": filters,
    "tiles": dash_data["tiles"],
    "tabs": dash_data.get("tabs", []),
})

if resp.json()["status"] == "ok":
    print("Date filter added successfully!")
else:
    print(f"Filter error: {resp.json()}")

print(f"\nDone! Dashboard URL: https://maegis.newnorth.nl/projects/{PROJECT}/dashboards/{dash_uuid}")
