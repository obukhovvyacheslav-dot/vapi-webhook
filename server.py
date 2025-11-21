from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = "5912766897"

def send_text(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

def send_log_file(log):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"

    files = {
        "document": ("log.json", json.dumps(log, ensure_ascii=False), "application/json")
    }

    data = {"chat_id": CHAT_ID, "caption": "RAW LOG"}

    requests.post(url, data=data, files=files)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    # ---- ищем summary в правильном месте ----
    summary = None

    # У VAPI summary находится здесь:
    # data["analysis"]["summary"]
    if isinstance(data, dict):
        summary = (
            data.get("analysis", {}).get("summary")
            or data.get("call", {}).get("analysis", {}).get("summary")
        )

    if summary:
        send_text("SUMMARY:\n" + summary)
    else:
        send_text("SUMMARY: not found")

    # Отправляем весь лог
    send_log_file(data)

    return jsonify({"ok": True}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
