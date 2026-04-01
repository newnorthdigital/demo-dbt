"""
Generate realistic dummy ecommerce data for Lightdash demo.
Brand: "Your Brand" — a fictional mid-size ecommerce store.

Generates 12 months of daily data (2025-04-01 to 2026-03-31) with:
- Realistic seasonality (Black Friday, Christmas, summer dip)
- Weekday/weekend patterns
- Growth trend
- Multiple traffic sources and campaigns
"""

import csv
import random
import math
import os
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

SEEDS_DIR = Path(__file__).parent.parent / "seeds"
SEEDS_DIR.mkdir(exist_ok=True)

START_DATE = date(2025, 4, 1)
END_DATE = date(2026, 3, 31)

def daterange(start, end):
    for n in range((end - start).days + 1):
        yield start + timedelta(n)

def seasonality_factor(d):
    """Seasonal multiplier: peak around Black Friday/Christmas, dip in summer."""
    day_of_year = d.timetuple().tm_yday
    # Black Friday ~ late Nov (day 325-330), Christmas ~ day 355
    # Summer dip ~ Jul/Aug (day 180-240)
    bf_peak = math.exp(-((day_of_year - 328) ** 2) / 200)  # Black Friday spike
    xmas_peak = math.exp(-((day_of_year - 355) ** 2) / 300)  # Christmas
    jan_sale = math.exp(-((day_of_year - 5) ** 2) / 150)  # New Year sale
    summer_dip = -0.15 * math.exp(-((day_of_year - 210) ** 2) / 1500)
    return 1.0 + 0.8 * bf_peak + 0.5 * xmas_peak + 0.3 * jan_sale + summer_dip

def weekday_factor(d):
    """Weekdays get more traffic than weekends for B2C ecom."""
    dow = d.weekday()
    if dow in (5, 6):  # Sat, Sun
        return 0.75 + random.uniform(-0.05, 0.05)
    if dow == 0:  # Monday peak
        return 1.1 + random.uniform(-0.05, 0.05)
    return 1.0 + random.uniform(-0.05, 0.05)

def growth_trend(d):
    """Gradual 25% YoY growth."""
    days_since_start = (d - START_DATE).days
    return 1.0 + 0.25 * (days_since_start / 365)

def noise(base, pct=0.1):
    return base * (1 + random.uniform(-pct, pct))


# ── 1. DAILY PERFORMANCE (GA4) ──────────────────────────────────────────────

SOURCES = [
    # (source, medium, channel_grouping, share_of_sessions)
    ("google", "cpc", "Paid Search", 0.25),
    ("google", "organic", "Organic Search", 0.30),
    ("(direct)", "(none)", "Direct", 0.15),
    ("facebook", "paid", "Paid Social", 0.10),
    ("instagram", "paid", "Paid Social", 0.05),
    ("email", "newsletter", "Email", 0.08),
    ("bing", "organic", "Organic Search", 0.04),
    ("pinterest", "referral", "Social", 0.03),
]

CAMPAIGNS = {
    "google/cpc": ["Brand - NL", "Brand - BE", "Shopping - All Products", "Shopping - Best Sellers", "Performance Max - Prospecting", "Search - Generic"],
    "facebook/paid": ["Retargeting - Website Visitors", "Lookalike - Purchasers", "Broad - Interest Based"],
    "instagram/paid": ["Stories - New Collection", "Reels - Product Highlights"],
    "email/newsletter": ["Weekly Newsletter", "Abandoned Cart", "Post-Purchase Flow"],
}

DEVICE_CATEGORIES = [("desktop", 0.45), ("mobile", 0.48), ("tablet", 0.07)]
COUNTRIES = [("Netherlands", 0.55), ("Belgium", 0.25), ("Germany", 0.12), ("France", 0.05), ("Other", 0.03)]

LANDING_PAGES = [
    ("/", 0.20),
    ("/collections/new-arrivals", 0.15),
    ("/collections/best-sellers", 0.12),
    ("/products/classic-essential-tee", 0.08),
    ("/products/premium-hoodie", 0.07),
    ("/products/organic-joggers", 0.06),
    ("/collections/sale", 0.10),
    ("/pages/about-us", 0.04),
    ("/blogs/style-guide", 0.05),
    ("/collections/accessories", 0.05),
    ("/products/weekend-bag", 0.04),
    ("/products/recycled-sneakers", 0.04),
]

def weighted_choice(options):
    items, weights = zip(*options)
    return random.choices(items, weights=weights, k=1)[0]

def generate_daily_performance():
    rows = []
    for d in daterange(START_DATE, END_DATE):
        base_sessions = 1200
        day_mult = seasonality_factor(d) * weekday_factor(d) * growth_trend(d)
        total_sessions = int(noise(base_sessions * day_mult, 0.08))

        for source, medium, channel, share in SOURCES:
            for _ in range(3):  # multiple device/country combos per source
                device = weighted_choice(DEVICE_CATEGORIES)
                country = weighted_choice(COUNTRIES)
                landing = weighted_choice(LANDING_PAGES)

                src_sessions = max(1, int(noise(total_sessions * share / 3, 0.15)))

                # Engagement varies by source
                eng_rate = {"Paid Search": 0.55, "Organic Search": 0.62, "Direct": 0.50,
                            "Paid Social": 0.45, "Email": 0.65, "Social": 0.40}.get(channel, 0.50)
                engaged = int(src_sessions * noise(eng_rate, 0.1))

                # Conversion funnel
                conv_rate = {"Paid Search": 0.028, "Organic Search": 0.022, "Direct": 0.035,
                             "Paid Social": 0.015, "Email": 0.042, "Social": 0.010}.get(channel, 0.02)
                # Mobile converts lower
                if device == "mobile":
                    conv_rate *= 0.7
                elif device == "tablet":
                    conv_rate *= 0.85

                transactions = max(0, int(src_sessions * noise(conv_rate, 0.2)))
                aov = noise(65, 0.15)  # Average order value ~65 EUR
                revenue = round(transactions * aov, 2)

                page_views = int(src_sessions * noise(2.8, 0.15))
                add_to_cart = int(src_sessions * noise(0.08, 0.2))
                begin_checkout = int(add_to_cart * noise(0.55, 0.15))
                purchases = transactions

                campaign = ""
                key = f"{source}/{medium}"
                if key in CAMPAIGNS:
                    campaign = random.choice(CAMPAIGNS[key])

                rows.append({
                    "session_date": d.isoformat(),
                    "session_source": source,
                    "session_medium": medium,
                    "session_campaign": campaign,
                    "session_default_channel_grouping": channel,
                    "device_category": device,
                    "country": country,
                    "landing_page_path": landing,
                    "sessions": src_sessions,
                    "engaged_sessions": engaged,
                    "revenue": revenue,
                    "page_views": page_views,
                    "add_to_cart_events": add_to_cart,
                    "begin_checkout_events": begin_checkout,
                    "purchase_events": purchases,
                    "transactions": transactions,
                })

    write_csv("seed_daily_performance.csv", rows)
    print(f"  seed_daily_performance: {len(rows)} rows")


# ── 2. GOOGLE ADS PERFORMANCE ───────────────────────────────────────────────

ADS_CAMPAIGNS = [
    {"name": "Brand - NL", "type": "SEARCH", "budget": 50},
    {"name": "Brand - BE", "type": "SEARCH", "budget": 30},
    {"name": "Shopping - All Products", "type": "SHOPPING", "budget": 80},
    {"name": "Shopping - Best Sellers", "type": "SHOPPING", "budget": 60},
    {"name": "Performance Max - Prospecting", "type": "PERFORMANCE_MAX", "budget": 100},
    {"name": "Search - Generic", "type": "SEARCH", "budget": 45},
    {"name": "Search - Competitor", "type": "SEARCH", "budget": 25},
    {"name": "Display - Retargeting", "type": "DISPLAY", "budget": 35},
]

DEVICES_ADS = ["DESKTOP", "MOBILE", "TABLET"]

def generate_google_ads_performance():
    rows = []
    for d in daterange(START_DATE, END_DATE):
        day_mult = seasonality_factor(d) * weekday_factor(d) * growth_trend(d)

        for camp in ADS_CAMPAIGNS:
            for device in DEVICES_ADS:
                device_mult = {"DESKTOP": 0.45, "MOBILE": 0.48, "TABLET": 0.07}[device]

                base_impressions = camp["budget"] * 25 * device_mult
                impressions = max(0, int(noise(base_impressions * day_mult, 0.15)))

                # CTR varies by campaign type
                ctr = {"SEARCH": 0.065, "SHOPPING": 0.012, "PERFORMANCE_MAX": 0.025, "DISPLAY": 0.004}[camp["type"]]
                clicks = max(0, int(impressions * noise(ctr, 0.15)))

                # CPC varies by type
                avg_cpc = {"SEARCH": 0.45, "SHOPPING": 0.28, "PERFORMANCE_MAX": 0.35, "DISPLAY": 0.18}[camp["type"]]
                cost = round(clicks * noise(avg_cpc, 0.2), 2)

                # Conversion rate
                conv_rate = {"SEARCH": 0.04, "SHOPPING": 0.025, "PERFORMANCE_MAX": 0.03, "DISPLAY": 0.008}[camp["type"]]
                if device == "MOBILE":
                    conv_rate *= 0.7
                conversions = max(0, int(clicks * noise(conv_rate, 0.25)))
                conv_value = round(conversions * noise(65, 0.15), 2)

                rows.append({
                    "report_date": d.isoformat(),
                    "account_name": "your_brand",
                    "campaign_name": camp["name"],
                    "campaign_status": "ENABLED",
                    "channel_type": camp["type"],
                    "device": device,
                    "ad_network_type": "SEARCH" if camp["type"] in ("SEARCH", "SHOPPING") else "CONTENT",
                    "impressions": impressions,
                    "clicks": clicks,
                    "cost": cost,
                    "conversions": conversions,
                    "conversions_value": conv_value,
                })

    write_csv("seed_google_ads_performance.csv", rows)
    print(f"  seed_google_ads_performance: {len(rows)} rows")


# ── 3. SEO PERFORMANCE (site-level) ─────────────────────────────────────────

SEO_QUERIES = [
    ("your brand", 0.15, 1.2, 0.45),  # brand query, high CTR
    ("sustainable clothing", 0.08, 8.5, 0.03),
    ("organic cotton tee", 0.06, 5.2, 0.06),
    ("eco friendly fashion", 0.07, 12.0, 0.02),
    ("recycled sneakers", 0.05, 4.8, 0.07),
    ("premium hoodie", 0.04, 6.3, 0.05),
    ("best joggers men", 0.05, 9.1, 0.03),
    ("weekend travel bag", 0.04, 7.5, 0.04),
    ("sustainable accessories", 0.03, 11.0, 0.02),
    ("your brand review", 0.06, 2.0, 0.25),
    ("organic fashion store", 0.04, 14.0, 0.015),
    ("buy ethical clothing online", 0.05, 10.5, 0.02),
    ("your brand discount code", 0.04, 1.5, 0.35),
    ("best sustainable brands", 0.06, 15.0, 0.012),
    ("hemp clothing", 0.03, 8.0, 0.03),
    ("fair trade fashion", 0.04, 13.0, 0.018),
    ("your brand joggers", 0.03, 1.8, 0.30),
    ("eco sneakers", 0.04, 6.0, 0.05),
]

def generate_seo_performance():
    rows = []
    for d in daterange(START_DATE, END_DATE):
        day_mult = seasonality_factor(d) * growth_trend(d)
        for query, share, avg_pos, base_ctr in SEO_QUERIES:
            base_impr = 800 * share
            impressions = max(0, int(noise(base_impr * day_mult, 0.2)))
            if impressions == 0:
                continue

            position = max(1.0, noise(avg_pos, 0.1))
            ctr = base_ctr * max(0.1, (1.0 / (position ** 0.5)))
            clicks = max(0, int(impressions * noise(ctr, 0.15)))
            sum_top_position = round(position * impressions, 1)

            rows.append({
                "data_date": d.isoformat(),
                "site_url": "https://www.yourbrand.com",
                "query": query,
                "search_type": "web",
                "impressions": impressions,
                "clicks": clicks,
                "sum_top_position": sum_top_position,
            })

    write_csv("seed_seo_performance.csv", rows)
    print(f"  seed_seo_performance: {len(rows)} rows")


# ── 4. SEO PAGES (URL-level) ────────────────────────────────────────────────

SEO_URLS = [
    ("https://www.yourbrand.com/", 0.20, 1.5, 0.35),
    ("https://www.yourbrand.com/collections/new-arrivals", 0.12, 5.0, 0.06),
    ("https://www.yourbrand.com/collections/best-sellers", 0.10, 4.5, 0.07),
    ("https://www.yourbrand.com/products/classic-essential-tee", 0.08, 6.0, 0.05),
    ("https://www.yourbrand.com/products/premium-hoodie", 0.07, 7.0, 0.04),
    ("https://www.yourbrand.com/products/organic-joggers", 0.06, 8.0, 0.035),
    ("https://www.yourbrand.com/products/recycled-sneakers", 0.06, 5.5, 0.055),
    ("https://www.yourbrand.com/products/weekend-bag", 0.05, 9.0, 0.03),
    ("https://www.yourbrand.com/collections/sale", 0.08, 6.5, 0.045),
    ("https://www.yourbrand.com/blogs/style-guide", 0.05, 12.0, 0.02),
    ("https://www.yourbrand.com/blogs/sustainability", 0.04, 14.0, 0.015),
    ("https://www.yourbrand.com/pages/about-us", 0.04, 3.0, 0.10),
    ("https://www.yourbrand.com/collections/accessories", 0.05, 10.0, 0.025),
]

def generate_seo_pages():
    rows = []
    for d in daterange(START_DATE, END_DATE):
        day_mult = seasonality_factor(d) * growth_trend(d)
        for url, share, avg_pos, base_ctr in SEO_URLS:
            base_impr = 600 * share
            impressions = max(0, int(noise(base_impr * day_mult, 0.2)))
            if impressions == 0:
                continue

            position = max(1.0, noise(avg_pos, 0.1))
            ctr = base_ctr * max(0.1, (1.0 / (position ** 0.5)))
            clicks = max(0, int(impressions * noise(ctr, 0.15)))
            sum_top_position = round(position * impressions, 1)

            # Random boolean flags for rich results
            is_product = "/products/" in url
            rows.append({
                "data_date": d.isoformat(),
                "url": url,
                "query": "",  # aggregated at URL level
                "impressions": impressions,
                "clicks": clicks,
                "sum_top_position": sum_top_position,
                "is_organic_shopping": is_product,
                "is_product_snippets": is_product,
                "is_merchant_listings": is_product and random.random() > 0.3,
            })

    write_csv("seed_seo_pages.csv", rows)
    print(f"  seed_seo_pages: {len(rows)} rows")


# ── 5. ECOMMERCE FUNNEL (daily, by device + channel) ────────────────────────

FUNNEL_CHANNELS = ["Paid Search", "Organic Search", "Direct", "Paid Social", "Email"]
FUNNEL_DEVICES = ["desktop", "mobile"]

def generate_ecommerce_funnel():
    rows = []
    for d in daterange(START_DATE, END_DATE):
        day_mult = seasonality_factor(d) * weekday_factor(d) * growth_trend(d)

        for channel in FUNNEL_CHANNELS:
            for device in FUNNEL_DEVICES:
                channel_share = {"Paid Search": 0.25, "Organic Search": 0.30, "Direct": 0.15,
                                 "Paid Social": 0.15, "Email": 0.08}.get(channel, 0.07)
                device_mult = 0.55 if device == "desktop" else 0.45

                sessions = max(1, int(noise(1200 * day_mult * channel_share * device_mult, 0.12)))

                # Funnel drop-off rates (realistic ecommerce)
                product_view_rate = noise(0.65, 0.08)
                add_to_cart_rate = noise(0.12, 0.10)  # % of sessions
                begin_checkout_rate = noise(0.55, 0.10)  # % of add_to_cart
                purchase_rate = noise(0.60, 0.10)  # % of begin_checkout

                # Mobile has worse conversion
                if device == "mobile":
                    add_to_cart_rate *= 0.85
                    begin_checkout_rate *= 0.90
                    purchase_rate *= 0.85

                product_views = int(sessions * product_view_rate)
                add_to_cart = int(sessions * add_to_cart_rate)
                begin_checkout = int(add_to_cart * begin_checkout_rate)
                purchases = int(begin_checkout * purchase_rate)

                aov = noise(65, 0.12)
                revenue = round(purchases * aov, 2)

                rows.append({
                    "event_date": d.isoformat(),
                    "device_category": device,
                    "channel_grouping": channel,
                    "sessions": sessions,
                    "product_views": product_views,
                    "add_to_cart": add_to_cart,
                    "begin_checkout": begin_checkout,
                    "purchases": purchases,
                    "revenue": revenue,
                })

    write_csv("seed_ecommerce_funnel.csv", rows)
    print(f"  seed_ecommerce_funnel: {len(rows)} rows")


# ── 6. CUSTOMER RETENTION (monthly cohorts) ──────────────────────────────────

def generate_customer_retention():
    """
    Monthly cohort retention: for each cohort month (first purchase),
    track what % return in months 1-11 after.
    """
    rows = []
    cohort_start = date(2025, 4, 1)

    for cohort_offset in range(12):  # 12 monthly cohorts
        cohort_month = date(2025 + (3 + cohort_offset) // 12, (3 + cohort_offset) % 12 + 1, 1)
        cohort_str = cohort_month.strftime("%Y-%m")

        # New customers in this cohort (growing over time)
        base_customers = int(noise(450 + cohort_offset * 20, 0.1))

        # Month 0 = 100% (first purchase)
        rows.append({
            "cohort_month": cohort_str,
            "months_since_first_purchase": 0,
            "new_customers": base_customers,
            "returning_customers": base_customers,
            "retention_rate": 1.0,
            "cohort_revenue": round(base_customers * noise(65, 0.1), 2),
        })

        # Retention curve: steep drop month 1, then gradual
        max_followup = min(11, 11 - cohort_offset)  # can't have data beyond Mar 2026
        for month_after in range(1, max_followup + 1):
            # Typical ecommerce retention: ~25% M1, ~18% M2, ~15% M3, then ~12% steady
            if month_after == 1:
                ret_rate = noise(0.25, 0.1)
            elif month_after == 2:
                ret_rate = noise(0.18, 0.1)
            elif month_after == 3:
                ret_rate = noise(0.15, 0.1)
            elif month_after <= 6:
                ret_rate = noise(0.12, 0.1)
            else:
                ret_rate = noise(0.10, 0.12)

            returning = max(0, int(base_customers * ret_rate))
            rev = round(returning * noise(72, 0.12), 2)  # returning customers have slightly higher AOV

            rows.append({
                "cohort_month": cohort_str,
                "months_since_first_purchase": month_after,
                "new_customers": base_customers,
                "returning_customers": returning,
                "retention_rate": round(ret_rate, 4),
                "cohort_revenue": rev,
            })

    write_csv("seed_customer_retention.csv", rows)
    print(f"  seed_customer_retention: {len(rows)} rows")


# ── UTILS ────────────────────────────────────────────────────────────────────

def write_csv(filename, rows):
    if not rows:
        return
    filepath = SEEDS_DIR / filename
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


# ── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Generating dummy data for 'Your Brand' demo...")
    generate_daily_performance()
    generate_google_ads_performance()
    generate_seo_performance()
    generate_seo_pages()
    generate_ecommerce_funnel()
    generate_customer_retention()
    print("\nDone! CSV files written to seeds/")
