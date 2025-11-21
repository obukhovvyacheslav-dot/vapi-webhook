from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

TELEGRAM_TOKEN = "8554754701:AAHQwOWyLUfSWKY8xzP4Cg6L5MhbSI8Go00"
CHAT_ID = "5912766897"  # твой id в Telegram

def send_text(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": message})

def send_log_file(log_data):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"

    files = {
        "document": ("log.json", json.dumps(log_data), "application/json")
    }

    data = {"chat_id": CHAT_ID, "caption": "RAW LOG"}

    requests.post(url, data=data, files=files)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    # summary
    summary = (
        data.get("summary")
        or data.get("call", {}).get("analysis", {}).get("summary", "")
    )

    if summary:
        send_text("SUMMARY:\n" + summary)

    # raw log
    send_log_file(data)

    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
