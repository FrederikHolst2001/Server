from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# DIN VPS URL
VPS_URL = "http://74.50.94.149:5000/webhook"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        print("Incoming:", data)

        # Send videre til din MT5 VPS
        r = requests.post(VPS_URL, json=data)

        return jsonify({
            "status": "forwarded",
            "vps_response": r.text
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/')
def home():
    return "Webhook running"
