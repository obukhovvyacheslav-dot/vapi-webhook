from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# Токен бота читаем из переменной окружения на Render
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = "5912766897"   # Твой Telegram ID


# -------------------------------------------
#  Отправка текстового сообщения
# -------------------------------------------
def send_text(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("ERROR send_text:", e)



# -------------------------------------------
#  Отправка RAW LOG как файла
# -------------------------------------------
def send_log_file(log_data):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"

    files = {
        "document": ("log.json", json.dumps(log_data, ensure_ascii=False), "application/json")
    }

    data = {"chat_id": CHAT_ID, "caption": "RAW LOG"}

    try:
        requests.post(url, data=data, files=files)
    except Exception as e:
        print("ERROR send_log_file:", e)



# -------------------------------------------
#  Основной обработчик Webhook
# -------------------------------------------
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    print("\n=== INCOMING WEBHOOK ===")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("=========================\n")

    # ---------- ИЩЕМ SUMMARY ВО ВСЕХ ФОРМАТАХ -------------
    summary = None

    # новый формат VAPI (analysis.summary)
    if isinstance(data, dict) and "analysis" in data:
        summary = data["analysis"].get("summary")

    # вариант: data["summary"]
    if not summary:
        summary = data.get("summary")

    # вариант: data["call"]["analysis"]["summary"]
    if not summary:
        summary = data.get("call", {}).get("analysis", {}).get("summary")

    # -------------------------------------------------------

    if summary:
        send_text("SUMMARY:\n" + summary)
    else:
        send_text("SUMMARY: not found")

    # Отправляем RAW JSON
    send_log_file(data)

    return jsonify({"status": "ok"}), 200



# -------------------------------------------
#  Запуск локально (на Render не используется)
# -------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
