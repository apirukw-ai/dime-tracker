import os
import requests
import json
from datetime import datetime

base_url = os.environ["FIREBASE_DB_URL"]
firebase_url = base_url + "/dime_ports/my-real-dime-port.json"
summary_url = base_url + "/dime_summary/current.json"

FINNHUB_API_KEY = os.environ["FINNHUB_API_KEY"]

print("Loading Firebase...")
print("URL =", firebase_url)

response = requests.get(firebase_url)
response.raise_for_status()

print("STATUS =", response.status_code)
funds = response.json()

print("Funds loaded:")

total_value = 0.0
total_cost = 0.0
total_profit = 0.0
total_daily_profit = 0.0

for fund in funds:
    code = fund["code"]
    units = float(fund.get("units", 0))
    avg_nav = float(fund.get("avgNav", 0))

    print("Checking", code)

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
        today_gain = (current_nav - prev_close) * units
        fund["todayGain"] = round(today_gain, 2)

        print(f"Updated: {code} | Current: {current_nav} | PrevClose: {prev_close} | TodayGain: {fund['todayGain']}")

    cur_nav = float(fund.get("currentNav", avg_nav))
    cost_val = units * avg_nav
    val_val = units * cur_nav
    
    total_cost += cost_val
    total_value += val_val
    
    if quote.get("c"):
        total_daily_profit += (cur_nav - float(quote.get("pc", cur_nav))) * units

total_profit = total_value - total_cost
total_profit_pct = (total_profit / total_cost * 100) if total_cost > 0 else 0.0

prev_total_value = total_value - total_daily_profit
daily_profit_pct = (total_daily_profit / prev_total_value * 100) if prev_total_value > 0 else 0.0

# 1. บันทึกข้อมูลรายการหุ้นรายตัวขึ้น Firebase
print("Saving Firebase (Ports)...")
requests.put(
    firebase_url,
    headers={"Content-Type": "application/json"},
    data=json.dumps(funds)
)

# 2. บันทึกข้อมูลสรุปภาพรวมพอร์ต DIME
print("Saving Firebase (Summary)...")
summary_payload = {
    "value": round(total_value, 2),
    "cost": round(total_cost, 2),
    "profit": round(total_profit, 2),
    "profitPct": round(total_profit_pct, 4),
    "dailyProfit": round(total_daily_profit, 2),
    "dailyProfitPct": round(daily_profit_pct, 4),
    "updatedAt": datetime.now().isoformat()  # 📍 ใช้ datetime ใน Python ตรงๆ แทนการยิง API
}

requests.put(
    summary_url,
    headers={"Content-Type": "application/json"},
    data=json.dumps(summary_payload)
)

print("SAVE STATUS = Success")
print("✅ DIME Prices & Daily Summary Updated Successfully!")
