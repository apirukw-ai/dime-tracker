import os
import requests
import json

firebase_url = (
    os.environ["FIREBASE_DB_URL"]
    + "/dime_ports/my-real-dime-port.json"
)

print("Loading Firebase...")
print("URL =", firebase_url)

response = requests.get(firebase_url)
response.raise_for_status()

print("STATUS =", response.status_code)
print("TEXT =", response.text[:500])

funds = response.json()

print("Funds loaded:")

for fund in funds:
    print(
        fund.get("code"),
        fund.get("currentNav")
    )
