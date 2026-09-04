import os
import requests
import json
from datetime import datetime

base_url = os.environ["FIREBASE_DB_URL"]
firebase_url = base_url + "/dime_ports/my-real-dime-port.json"
summary_url = base_url + "/dime_summary/current.json"

FINNHUB_API_KEY = os.environ["FINNHUB_API_KEY"]

print("Loading Firebase Ports...")
response = requests.get(firebase_url)
response.raise_for_status()

funds = response.json()
print("Funds loaded:", len(funds))

total_value_usd = 0.0
total_cost_usd = 0.0
total_daily_profit_usd = 0.0

for fund in funds:
    code = fund["code"]
    units = float(fund.get("units", 0))
    avg_nav = float(fund.get("avgNav", 0))

    try:
        quote = requests.get(
            f"https://finnhub.io/api/v1/quote?symbol={code}&token={FINNHUB_API_KEY}",
            timeout=10
        ).json()
    except Exception as e:
        print(f"Error fetching {code}: {e}")
        quote = {}

    if quote.get("c"):
        current_nav = float(quote["c"])
        prev_close = float(quote.get("pc", current_nav))

        fund["currentNav"] = current_nav
        
        # คำนวณกำไรวันนี้ของหุ้นตัวนี้ (USD)
        today_gain = (current_nav - prev_close) * units
        fund["todayGain"] = round(today_gain, 2)
        total_daily_profit_usd += today_gain
    else:
        current_nav = float(fund.get("currentNav", avg_nav))

    total_cost_usd += units * avg_nav
    total_value_usd += units * current_nav

total_profit_usd = total_value_usd - total_cost_usd
total_profit_pct = (total_profit_usd / total_cost_usd * 100) if total_cost_usd > 0 else 0.0

prev_total_value = total_value_usd - total_daily_profit_usd
daily_profit_pct = (total_daily_profit_usd / prev_total_value * 100) if prev_total_value > 0 else 0.0

# 1. บันทึกข้อมูลหุ้นรายตัว
print("Saving Ports to Firebase...")
requests.put(firebase_url, json=funds)

# 2. บันทึก Summary สรุปภาพรวมเข้า /dime_summary/current.json (ระบุ URL ตรงๆ ชัดเจน)
print("Saving Summary to Firebase...")
direct_summary_url = "https://scb-e-class-default-rtdb.asia-southeast1.firebasedatabase.app/dime_summary/current.json"

response = requests.put(direct_summary_url, json=summary_payload)
print("SUMMARY SAVE STATUS =", response.status_code)
response.raise_for_status() 
print("✅ DIME Summary Updated Successfully!")
