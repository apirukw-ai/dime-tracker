import os
import requests
import json

firebase_url = os.environ["FIREBASE_DB_URL"]

print("Loading Firebase...")

response = requests.get(firebase_url)
response.raise_for_status()

funds = response.json()

print("Funds loaded:")

for fund in funds:
    print(
        fund.get("code"),
        fund.get("currentNav")
    )
