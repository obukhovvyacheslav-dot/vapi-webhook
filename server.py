from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = "5912766897"

def send_text(msg):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": msg}
    )

def send_file(data):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument",
        data={"chat_id": CHAT_ID, "caption": "RAW LOG"},
        files={
            "document": (
                "log.json",
                json.dumps(data, ensure_ascii=False, indent=2),
                "application/json"
            )
        }
    )

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    summary = (
        data.get("message", {}).get("analysis", {}).get("summary")
        or data.get("analysis", {}).get("summary")
        or data.get("summary")
        or "not found"
    )

    send_text("SUMMARY: " + summary)
    send_file(data)

    return jsonify({"ok": True}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
