import json
import os
import requests

DB_URL = os.environ["https://my-dime-port-default-rtdb.asia-southeast1.firebasedatabase.app"]
FINNHUB_API_KEY = os.environ["da22fjpr01qp0a26e6ugda22fjpr01qp0a26e6v0"]

url = f"{DB_URL}/dime_ports/my-real-dime-port.json"

# โหลดข้อมูลพอร์ต
funds = requests.get(url).json()

for fund in funds:

    code = fund["code"]

    quote = requests.get(
        f"https://finnhub.io/api/v1/quote?symbol={code}&token={FINNHUB_API_KEY}"
    ).json()

    if quote.get("c"):
        fund["currentNav"] = quote["c"]

# save firebase
requests.put(
    url,
    headers={"Content-Type": "application/json"},
    data=json.dumps(funds)
)

print("✅ Prices Updated")
