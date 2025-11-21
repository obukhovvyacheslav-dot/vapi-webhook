from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = "5912766897"

def tg_text(msg):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": msg}
    )

def tg_file(data):
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

def get_summary(data):
    paths = [
        ["analysis", "summary"],
        ["artifact", "analysis", "summary"],
        ["call", "analysis", "summary"]
    ]
    for p in paths:
        d = data
        ok = True
        for key in p:
            if key in d:
                d = d[key]
            else:
                ok = False
                break
        if ok and isinstance(d, str) and d.strip():
            return d
    return None


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    summary = get_summary(data)

    if summary:
        tg_text("SUMMARY:\n" + summary)
    else:
        tg_text("SUMMARY: not found")

    tg_file(data)
    return jsonify({"ok": True}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
