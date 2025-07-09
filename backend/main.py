from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

@app.route("/", methods=["GET"])
def home():
    return "✅ ATSAVE MQTT Backend Running!"

@app.route("/ingest", methods=["POST"])
def ingest():
    try:
        data = request.get_json()
        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/device_logs",
            headers=HEADERS,
            json=data
        )
        if resp.status_code in [200, 201]:
            return jsonify({"status": "ok"}), 201
        return jsonify({"error": resp.text}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # ⬅️ 這裡改為讀取 Railway 給的 PORT
    app.run(host="0.0.0.0", port=port)
