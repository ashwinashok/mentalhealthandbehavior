import os
from dotenv import load_dotenv
from twilio.rest import Client

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(REPO, ".env"))

out_number = input("Enter destination phone number: ")
from_number = os.getenv("NUMBER")
account_sid = os.getenv("SID")
account_auth = os.getenv("AUTH_TOKEN")
if not all([from_number, account_sid, account_auth]):
    raise SystemExit("Missing Twilio credentials. Copy .env.example to .env and fill SID, AUTH_TOKEN, NUMBER.")

client = Client(account_sid, account_auth)
body = input("Message text: ").strip() or "AttentionSpan session ping."
message = client.messages.create(body=body, from_=from_number, to=out_number)
print("Sent:", message.sid)