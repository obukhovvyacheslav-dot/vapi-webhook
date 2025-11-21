from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = "5912766897"

def send_text(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": message})

def send_log_file(log_data):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    files = {
        "document": ("log.json", json.dumps(log_data, ensure_ascii=False), "application/json")
    }
    data = {"chat_id": CHAT_ID, "caption": "RAW LOG"}
    requests.post(url, data=data, files=files)

def extract_summary(data):
    """
    Поддержка всех вариантов структуры summary в VAPI.
    """

    # 1. summary в корне
    if "summary" in data and data["summary"]:
        return data["summary"]

    # 2. summary → call.analysis.summary
    try:
        return data["call"]["analysis"]["summary"]
    except:
        pass

    # 3. summary → analysis.summary
    try:
        return data["analysis"]["summary"]
    except:
        pass

    # 4. summary внутри event data
    try:
        return data["data"]["summary"]
    except:
        pass

    # Не нашли
    return None


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    # Фильтруем только финальное событие
    event_type = data.get("type") or data.get("event") or ""

    if event_type.lower() not in ["call.completed", "completed", "analysis.completed", "call.ended"]:
        return jsonify({"ignored": True}), 200

    # Summary
    summary = extract_summary(data)
    if summary:
        send_text("SUMMARY:\n" + summary)

    # Raw log
    send_log_file(data)

    return jsonify({"status": "ok"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
