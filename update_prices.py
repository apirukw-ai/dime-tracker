import os
import requests
import json

firebase_url = (
    os.environ["FIREBASE_DB_URL"]
    + "/dime_ports/my-real-dime-port.json"
)

FINNHUB_API_KEY = os.environ["FINNHUB_API_KEY"]

print("Loading Firebase...")
print("URL =", firebase_url)

response = requests.get(firebase_url)
response.raise_for_status()

print("STATUS =", response.status_code)
print("TEXT =", response.text[:500])

funds = response.json()

print("Funds loaded:")

for fund in funds:

    code = fund["code"]

    print("Checking", code)

    quote = requests.get(
        f"https://finnhub.io/api/v1/quote?symbol={code}&token={FINNHUB_API_KEY}"
    ).json()

    print(code, quote)

    if quote.get("c"):
        fund["currentNav"] = quote["c"]

        print(
            "Updated:",
            code,
            quote["c"]
        )

# จบ for แล้วค่อย Save ทีเดียว

print("Saving Firebase...")

response = requests.put(
    firebase_url,
    headers={"Content-Type": "application/json"},
    data=json.dumps(funds)
)

print("SAVE STATUS =", response.status_code)

print("✅ Prices Updated")
