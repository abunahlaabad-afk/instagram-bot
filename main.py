from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "my_secret_token")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", "")

RULES = {
    "مرحبا":     "أهلاً وسهلاً! كيف أقدر أساعدك؟ 😊",
    "هلا":       "هلا والله! كيف أقدر أساعدك؟ 😊",
    "السعر":     "يمكنك الاطلاع على أسعارنا عبر الرابط في البايو 🛍️",
    "التوصيل":   "نوصل لجميع المناطق خلال 3-5 أيام عمل 🚚",
    "كيف اطلب": "لطلب المنتج راسلنا برقمك وسنتواصل معك فوراً 📦",
}

DEFAULT_REPLY = "شكراً على رسالتك! سنرد عليك في أقرب وقت ممكن 🙏"

def get_auto_reply(message_text):
    text_lower = message_text.lower()
    for keyword, reply in RULES.items():
        if keyword.lower() in text_lower:
            return reply
    return DEFAULT_REPLY

def send_message(recipient_id, message_text):
    url = "https://graph.facebook.com/v18.0/me/messages"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}, "messaging_type": "RESPONSE"}
    params = {"access_token": PAGE_ACCESS_TOKEN}
    requests.post(url, json=payload, params=params)

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403

@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()
    if data.get("object") != "instagram":
        return "Not Instagram", 404
    for entry in data.get("entry", []):
        for event in entry.get("messaging", []):
            sender_id = event["sender"]["id"]
            text = event.get("message", {}).get("text", "")
            if text:
                send_message(sender_id, get_auto_reply(text))
    return "OK", 200

@app.route("/")
def home():
    return "البوت يعمل ✅", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
