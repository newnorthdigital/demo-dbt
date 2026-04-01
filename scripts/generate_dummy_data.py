"""
Generate realistic dummy ecommerce data for Lightdash demo.
Brand: "Your Brand" — a fictional mid-size sustainable fashion ecommerce store.

Inspired by Coco & Cici Looker Studio dashboard structure.
Generates 12 months of daily data (2025-04-01 to 2026-03-31).
"""

import csv
import random
import math
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
    day_of_year = d.timetuple().tm_yday
    bf_peak = math.exp(-((day_of_year - 328) ** 2) / 200)
    xmas_peak = math.exp(-((day_of_year - 355) ** 2) / 300)
    jan_sale = math.exp(-((day_of_year - 5) ** 2) / 150)
    summer_dip = -0.15 * math.exp(-((day_of_year - 210) ** 2) / 1500)
    return 1.0 + 0.8 * bf_peak + 0.5 * xmas_peak + 0.3 * jan_sale + summer_dip


def weekday_factor(d):
    dow = d.weekday()
    if dow in (5, 6):
        return 0.75 + random.uniform(-0.05, 0.05)
    if dow == 0:
        return 1.1 + random.uniform(-0.05, 0.05)
    return 1.0 + random.uniform(-0.05, 0.05)


def growth_trend(d):
    days_since_start = (d - START_DATE).days
    return 1.0 + 0.25 * (days_since_start / 365)


def noise(base, pct=0.1):
    return base * (1 + random.uniform(-pct, pct))


def weighted_choice(options):
    items, weights = zip(*options)
    return random.choices(items, weights=weights, k=1)[0]


def write_csv(filename, rows):
    if not rows:
        return
    filepath = SEEDS_DIR / filename
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


# ═════════════════════════════════════════════════════════════════════════════
# CHANNEL CONFIG (shared across generators)
# ═════════════════════════════════════════════════════════════════════════════

CHANNELS = [
    # (channel, session_share, conv_rate, new_cust_pct, daily_spend)
    ("Google Ads",      0.28, 0.027, 0.55, 350),
    ("Meta Ads",        0.12, 0.020, 0.65, 180),
    ("Organic Search",  0.25, 0.022, 0.40, 0),
    ("Direct",          0.12, 0.035, 0.25, 0),
    ("Email",           0.10, 0.045, 0.15, 0),
    ("Referral",        0.06, 0.030, 0.50, 0),
    ("Bol.com",         0.04, 0.0,   0.35, 0),  # marketplace — orders come separately
    ("Manual Orders",   0.01, 0.0,   0.10, 0),
]

CATEGORIES = [
    # (name, avg_price, share_of_units, cogs_pct, return_rate)
    ("Tops",        45,  0.25, 0.38, 0.04),
    ("Bottoms",     65,  0.18, 0.35, 0.05),
    ("Outerwear",  120,  0.10, 0.40, 0.08),
    ("Dresses",     85,  0.12, 0.36, 0.06),
    ("Accessories",  25, 0.15, 0.30, 0.02),
    ("Footwear",    95,  0.08, 0.42, 0.07),
    ("Bags",        75,  0.07, 0.33, 0.03),
    ("Activewear",  55,  0.05, 0.37, 0.03),
]

PRODUCTS = [
    # (name, category, price, share_within_category)
    ("Classic Essential Tee",       "Tops",       39, 0.30),
    ("Organic V-Neck",              "Tops",       45, 0.25),
    ("Linen Relaxed Shirt",         "Tops",       59, 0.20),
    ("Oversized Crop Top",          "Tops",       35, 0.15),
    ("Merino Wool Polo",            "Tops",       65, 0.10),
    ("Organic Joggers",             "Bottoms",    59, 0.30),
    ("High-Rise Wide Leg",          "Bottoms",    75, 0.25),
    ("Relaxed Chinos",              "Bottoms",    69, 0.20),
    ("Linen Shorts",                "Bottoms",    49, 0.15),
    ("Denim Straight Leg",          "Bottoms",    89, 0.10),
    ("Premium Hoodie",              "Outerwear", 110, 0.35),
    ("Wool Blend Coat",             "Outerwear", 189, 0.25),
    ("Puffer Jacket Recycled",      "Outerwear", 145, 0.25),
    ("Rain Jacket",                 "Outerwear",  95, 0.15),
    ("Wrap Midi Dress",             "Dresses",    79, 0.30),
    ("Linen Maxi Dress",            "Dresses",    95, 0.25),
    ("Organic Shirt Dress",         "Dresses",    85, 0.25),
    ("Knit Sweater Dress",          "Dresses",    99, 0.20),
    ("Recycled Sneakers",           "Footwear",   89, 0.40),
    ("Leather Ankle Boots",         "Footwear",  139, 0.30),
    ("Canvas Slip-Ons",             "Footwear",   59, 0.30),
    ("Weekend Travel Bag",          "Bags",       89, 0.35),
    ("Canvas Tote",                 "Bags",       45, 0.35),
    ("Crossbody Bag",               "Bags",       65, 0.30),
    ("Bamboo Sunglasses",           "Accessories", 35, 0.25),
    ("Recycled Beanie",             "Accessories", 22, 0.25),
    ("Cork Wallet",                 "Accessories", 29, 0.20),
    ("Organic Socks 3-Pack",        "Accessories", 18, 0.15),
    ("Hemp Belt",                   "Accessories", 25, 0.15),
    ("Seamless Sports Bra",         "Activewear",  45, 0.35),
    ("Performance Leggings",        "Activewear",  65, 0.35),
    ("Running Tank",                "Activewear",  39, 0.30),
]


# ═════════════════════════════════════════════════════════════════════════════
# 1. ORDERS & REVENUE (daily, by channel — like Coco Overview + Orders page)
# ═════════════════════════════════════════════════════════════════════════════

def generate_orders_revenue():
    rows = []
    for d in daterange(START_DATE, END_DATE):
        day_mult = seasonality_factor(d) * weekday_factor(d) * growth_trend(d)
        base_daily_orders = 35

        for ch_name, sess_share, conv_rate, new_pct, daily_spend in CHANNELS:
            # Sessions (0 for marketplace/manual channels)
            if ch_name in ("Bol.com", "Manual Orders"):
                sessions = 0
                # These channels get direct orders
                if ch_name == "Bol.com":
                    orders = max(0, int(noise(base_daily_orders * 0.06 * day_mult, 0.25)))
                else:
                    orders = max(0, int(noise(base_daily_orders * 0.01 * day_mult, 0.4)))
            else:
                sessions = max(1, int(noise(1400 * day_mult * sess_share, 0.12)))
                orders = max(0, int(sessions * noise(conv_rate, 0.15)))

            if orders == 0:
                # Still emit a row with 0 orders for session tracking
                if sessions > 0:
                    rows.append({
                        "order_date": d.isoformat(),
                        "channel": ch_name,
                        "sessions": sessions,
                        "orders": 0,
                        "new_customer_orders": 0,
                        "returning_customer_orders": 0,
                        "gross_revenue": 0,
                        "amount_refunded": 0,
                        "units_sold": 0,
                        "units_returned": 0,
                        "cogs": 0,
                        "ad_spend": 0,
                    })
                continue

            new_orders = int(orders * noise(new_pct, 0.08))
            returning_orders = orders - new_orders
            aov = noise(78, 0.12)  # slightly higher AOV than before
            gross_revenue = round(orders * aov, 2)

            # Items per order ~1.8
            units_sold = int(orders * noise(1.8, 0.1))
            # Return rate ~4% of units
            return_rate = noise(0.04, 0.2)
            units_returned = max(0, int(units_sold * return_rate))
            amount_refunded = round(units_returned * noise(aov / 1.8, 0.15), 2)

            # COGS ~37% of gross revenue
            cogs = round(gross_revenue * noise(0.37, 0.05), 2)

            # Ad spend (only for paid channels)
            if daily_spend > 0:
                spend = round(noise(daily_spend * day_mult, 0.12), 2)
            else:
                spend = 0

            rows.append({
                "order_date": d.isoformat(),
                "channel": ch_name,
                "sessions": sessions,
                "orders": orders,
                "new_customer_orders": new_orders,
                "returning_customer_orders": returning_orders,
                "gross_revenue": gross_revenue,
                "amount_refunded": amount_refunded,
                "units_sold": units_sold,
                "units_returned": units_returned,
                "cogs": cogs,
                "ad_spend": spend,
            })

    write_csv("seed_orders_revenue.csv", rows)
    print(f"  seed_orders_revenue: {len(rows)} rows")


# ═════════════════════════════════════════════════════════════════════════════
# 2. PRODUCT PERFORMANCE (daily, by product — like Coco Products page)
# ═════════════════════════════════════════════════════════════════════════════

def generate_product_performance():
    rows = []
    cat_lookup = {c[0]: c for c in CATEGORIES}

    for d in daterange(START_DATE, END_DATE):
        day_mult = seasonality_factor(d) * weekday_factor(d) * growth_trend(d)
        base_daily_units = 60

        for prod_name, cat_name, price, share_in_cat in PRODUCTS:
            cat = cat_lookup[cat_name]
            cat_share = cat[2]  # share_of_units
            cogs_pct = cat[3]
            return_rate = cat[4]

            units = max(0, int(noise(base_daily_units * day_mult * cat_share * share_in_cat, 0.25)))
            if units == 0:
                continue

            item_price = noise(price, 0.05)
            revenue = round(units * item_price, 2)
            unit_cogs = round(item_price * noise(cogs_pct, 0.05), 2)
            total_cogs = round(units * unit_cogs, 2)
            units_returned = max(0, int(units * noise(return_rate, 0.3)))
            refund_amount = round(units_returned * item_price, 2)

            # Repeat order rate varies by category
            repeat_rate = noise(0.30, 0.15)

            rows.append({
                "order_date": d.isoformat(),
                "product_name": prod_name,
                "category": cat_name,
                "item_price": round(item_price, 2),
                "units_sold": units,
                "revenue": revenue,
                "units_returned": units_returned,
                "refund_amount": refund_amount,
                "cogs": total_cogs,
                "repeat_order_pct": round(repeat_rate, 4),
            })

    write_csv("seed_product_performance.csv", rows)
    print(f"  seed_product_performance: {len(rows)} rows")


# ═════════════════════════════════════════════════════════════════════════════
# 3. CUSTOMERS (daily, new vs returning — like Coco Customers page)
# ═════════════════════════════════════════════════════════════════════════════

def generate_customers():
    rows = []
    for d in daterange(START_DATE, END_DATE):
        day_mult = seasonality_factor(d) * weekday_factor(d) * growth_trend(d)

        total_customers = max(1, int(noise(30 * day_mult, 0.12)))
        new_pct = noise(0.60, 0.08)  # ~60% new customers
        new_customers = int(total_customers * new_pct)
        returning_customers = total_customers - new_customers

        new_aov = noise(72, 0.12)
        returning_aov = noise(85, 0.12)  # returning buy more

        new_revenue = round(new_customers * new_aov, 2)
        returning_revenue = round(returning_customers * returning_aov, 2)

        # Items per order
        new_items = round(new_customers * noise(1.7, 0.1))
        returning_items = round(returning_customers * noise(2.0, 0.1))

        # CLV estimate (cumulative average over cohorts)
        clv = noise(320 + (d - START_DATE).days * 0.3, 0.05)

        rows.append({
            "order_date": d.isoformat(),
            "new_customers": new_customers,
            "returning_customers": returning_customers,
            "total_customers": total_customers,
            "new_customer_revenue": new_revenue,
            "returning_customer_revenue": returning_revenue,
            "new_customer_aov": round(new_aov, 2),
            "returning_customer_aov": round(returning_aov, 2),
            "new_customer_items": int(new_items),
            "returning_customer_items": int(returning_items),
            "customer_lifetime_value": round(clv, 2),
        })

    write_csv("seed_customers.csv", rows)
    print(f"  seed_customers: {len(rows)} rows")


# ═════════════════════════════════════════════════════════════════════════════
# 4. ECOMMERCE FUNNEL (kept from before, slightly simplified)
# ═════════════════════════════════════════════════════════════════════════════

FUNNEL_CHANNELS = ["Google Ads", "Organic Search", "Direct", "Meta Ads", "Email"]
FUNNEL_DEVICES = ["desktop", "mobile"]

def generate_ecommerce_funnel():
    rows = []
    for d in daterange(START_DATE, END_DATE):
        day_mult = seasonality_factor(d) * weekday_factor(d) * growth_trend(d)

        for channel in FUNNEL_CHANNELS:
            for device in FUNNEL_DEVICES:
                channel_share = {"Google Ads": 0.28, "Organic Search": 0.25, "Direct": 0.15,
                                 "Meta Ads": 0.15, "Email": 0.10}.get(channel, 0.07)
                device_mult = 0.55 if device == "desktop" else 0.45

                sessions = max(1, int(noise(1400 * day_mult * channel_share * device_mult, 0.12)))
                product_views = int(sessions * noise(0.65, 0.08))
                add_to_cart = int(sessions * noise(0.12, 0.10))
                begin_checkout = int(add_to_cart * noise(0.55, 0.10))
                purchase_rate = noise(0.60, 0.10)
                if device == "mobile":
                    add_to_cart = int(add_to_cart * 0.85)
                    begin_checkout = int(begin_checkout * 0.90)
                    purchase_rate *= 0.85
                purchases = int(begin_checkout * purchase_rate)
                revenue = round(purchases * noise(78, 0.12), 2)

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


# ═════════════════════════════════════════════════════════════════════════════
# 5. CUSTOMER RETENTION (monthly cohorts — kept from before)
# ═════════════════════════════════════════════════════════════════════════════

def generate_customer_retention():
    rows = []
    for cohort_offset in range(12):
        cohort_month = date(2025 + (3 + cohort_offset) // 12, (3 + cohort_offset) % 12 + 1, 1)
        cohort_str = cohort_month.strftime("%Y-%m")
        base_customers = int(noise(450 + cohort_offset * 20, 0.1))

        rows.append({
            "cohort_month": cohort_str,
            "months_since_first_purchase": 0,
            "new_customers": base_customers,
            "returning_customers": base_customers,
            "retention_rate": 1.0,
            "cohort_revenue": round(base_customers * noise(78, 0.1), 2),
        })

        max_followup = min(11, 11 - cohort_offset)
        for month_after in range(1, max_followup + 1):
            if month_after == 1: ret_rate = noise(0.25, 0.1)
            elif month_after == 2: ret_rate = noise(0.18, 0.1)
            elif month_after == 3: ret_rate = noise(0.15, 0.1)
            elif month_after <= 6: ret_rate = noise(0.12, 0.1)
            else: ret_rate = noise(0.10, 0.12)

            returning = max(0, int(base_customers * ret_rate))
            rev = round(returning * noise(85, 0.12), 2)

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


# ═════════════════════════════════════════════════════════════════════════════
# 6. SEO PERFORMANCE (kept from before)
# ═════════════════════════════════════════════════════════════════════════════

SEO_QUERIES = [
    ("your brand", 0.15, 1.2, 0.45), ("sustainable clothing", 0.08, 8.5, 0.03),
    ("organic cotton tee", 0.06, 5.2, 0.06), ("eco friendly fashion", 0.07, 12.0, 0.02),
    ("recycled sneakers", 0.05, 4.8, 0.07), ("premium hoodie", 0.04, 6.3, 0.05),
    ("best joggers men", 0.05, 9.1, 0.03), ("weekend travel bag", 0.04, 7.5, 0.04),
    ("sustainable accessories", 0.03, 11.0, 0.02), ("your brand review", 0.06, 2.0, 0.25),
    ("organic fashion store", 0.04, 14.0, 0.015), ("buy ethical clothing online", 0.05, 10.5, 0.02),
    ("your brand discount code", 0.04, 1.5, 0.35), ("best sustainable brands", 0.06, 15.0, 0.012),
    ("hemp clothing", 0.03, 8.0, 0.03), ("fair trade fashion", 0.04, 13.0, 0.018),
    ("your brand joggers", 0.03, 1.8, 0.30), ("eco sneakers", 0.04, 6.0, 0.05),
]

def generate_seo_performance():
    rows = []
    for d in daterange(START_DATE, END_DATE):
        day_mult = seasonality_factor(d) * growth_trend(d)
        for query, share, avg_pos, base_ctr in SEO_QUERIES:
            impressions = max(0, int(noise(800 * share * day_mult, 0.2)))
            if impressions == 0: continue
            position = max(1.0, noise(avg_pos, 0.1))
            ctr = base_ctr * max(0.1, (1.0 / (position ** 0.5)))
            clicks = max(0, int(impressions * noise(ctr, 0.15)))
            rows.append({
                "data_date": d.isoformat(), "site_url": "https://www.yourbrand.com",
                "query": query, "search_type": "web",
                "impressions": impressions, "clicks": clicks,
                "sum_top_position": round(position * impressions, 1),
            })
    write_csv("seed_seo_performance.csv", rows)
    print(f"  seed_seo_performance: {len(rows)} rows")


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Generating dummy data for 'Your Brand' demo (v2)...")
    generate_orders_revenue()
    generate_product_performance()
    generate_customers()
    generate_ecommerce_funnel()
    generate_customer_retention()
    generate_seo_performance()
    print("\nDone! CSV files written to seeds/")
