from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# Токен берем из переменных окружения Render
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = "5912766897"   # Твой телеграм ID


def send_text(msg: str):
    """Отправка текстового сообщения в Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("send_text ERROR:", e)


def send_log_file(log_data):
    """Отправка сырых логов как JSON-файла."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    files = {
        "document": (
            "log.json",
            json.dumps(log_data, ensure_ascii=False, indent=2),
            "application/json"
        )
    }
    data = {"chat_id": CHAT_ID, "caption": "RAW LOG"}

    try:
        requests.post(url, data=data, files=files)
    except Exception as e:
        print("send_log_file ERROR:", e)


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    # --- ИЩЕМ SUMMARY ВО ВСЕХ ВАРИАНТАХ ---
    summary = (
        data.get("analysis", {}).get("summary")
        or data.get("summary")
        or "not found"
    )

    # Отправляем краткое содержание
    send_text("SUMMARY: " + summary)

    # Отправляем полный лог
    send_log_file(data)

    return jsonify({"status": "ok"}), 200


@app.route('/')
def home():
    return "Server is running", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
