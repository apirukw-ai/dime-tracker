import os
import requests
from datetime import datetime, timezone, timedelta

# 1. ดึง Environment Variables
FIREBASE_SECRET = os.environ.get('FIREBASE_SECRET')
base_url = os.environ["FIREBASE_DB_URL"]
FINNHUB_API_KEY = os.environ["FINNHUB_API_KEY"]

# 2. เตรียม URL แบบ Dynamic (อ้างอิงจาก base_url และแนบ Secret สำหรับสิทธิ์การเขียน)
read_ports_url = f"{base_url}/dime_ports/my-real-dime-port.json"
write_ports_url = f"{base_url}/dime_ports/my-real-dime-port.json?auth={FIREBASE_SECRET}"
write_summary_url = f"{base_url}/dime_summary/current.json?auth={FIREBASE_SECRET}"

print("Loading Firebase Ports...")
response = requests.get(read_ports_url)
response.raise_for_status()

funds = response.json()
print("Funds loaded:", len(funds) if isinstance(funds, list) else 0)

total_value_usd = 0.0
total_cost_usd = 0.0
total_daily_profit_usd = 0.0

# 3. วนลูปดึงราคาหุ้นจาก Finnhub
if isinstance(funds, list):
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
            today_gain = (current_nav - prev_close) * units
            fund["todayGain"] = round(today_gain, 2)
            total_daily_profit_usd += today_gain
        else:
            current_nav = float(fund.get("currentNav", avg_nav))

        total_cost_usd += units * avg_nav
        total_value_usd += units * current_nav

# 4. คำนวณสรุปภาพรวม (USD) พร้อมสมการ Daily Profit Pct ที่ถูกต้อง
total_profit_usd = total_value_usd - total_cost_usd
total_profit_pct = (total_profit_usd / total_cost_usd * 100) if total_cost_usd > 0 else 0.0

prev_total_value = total_value_usd - total_daily_profit_usd
daily_profit_pct = (total_daily_profit_usd / prev_total_value * 100) if prev_total_value > 0 else 0.0

# 5. จัดการเวลา
tz_th = timezone(timedelta(hours=7))
now_th = datetime.now(tz_th)
now_th_iso = now_th.isoformat()
now_th_str = now_th.strftime('%d/%m/%Y %H:%M:%S')

# 6. 📍 บันทึกราคาหุ้นรายตัว (พอร์ต) กลับขึ้น Firebase
print("Saving Updated Ports to Firebase...")
res_ports = requests.put(write_ports_url, json=funds)
res_ports.raise_for_status()
print("✅ DIME Ports Updated Successfully!")

# 7. 📍 บันทึก Summary เข้า Firebase
print("Saving Summary to Firebase...")
summary_payload = {
    "value": round(total_value_usd, 2),
    "cost": round(total_cost_usd, 2),
    "profit": round(total_profit_usd, 2),
    "profitPct": round(total_profit_pct, 4),
    "dailyProfit": round(total_daily_profit_usd, 2),
    "dailyProfitPct": round(daily_profit_pct, 4),
    "updatedAt": now_th_iso,
    "updatedAtStr": now_th_str
}

res_summary = requests.put(write_summary_url, json=summary_payload)
res_summary.raise_for_status()
print("✅ DIME Summary Updated Successfully!")
