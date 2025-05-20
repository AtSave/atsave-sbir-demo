from flask import Flask, request, jsonify
import requests
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

app = Flask(__name__)

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

@app.route("/latest", methods=["GET"])
def latest_data():
    devices = ["device01", "device02", "device03", "device04", "device05"]
    results = []
    for device in devices:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/device_logs?device_id=eq.{device}&order=timestamp.desc&limit=1",
            headers=headers,
        )
        if r.ok and r.json():
            results.append(r.json()[0])
    return jsonify(results)

@app.route("/query-logs", methods=["GET"])
def query_logs():
    device_id = request.args.get("device_id")
    start = request.args.get("start")
    end = request.args.get("end")

    url = f"{SUPABASE_URL}/rest/v1/device_logs?device_id=eq.{device_id}&timestamp=gte.{start}&timestamp=lte.{end}&order=timestamp.asc"
    r = requests.get(url, headers=headers)
    return jsonify(r.json())

@app.route("/summary-by-date", methods=["GET"])
def summary_by_date():
    date = request.args.get("date")  # format: 2025-05-05
    start = f"{date}T00:00:00Z"
    end = f"{date}T23:59:59Z"
    url = f"{SUPABASE_URL}/rest/v1/device_logs?timestamp=gte.{start}&timestamp=lte.{end}"
    r = requests.get(url, headers=headers)
    if not r.ok:
        return jsonify({"error": "Failed to fetch data"}), 400

    data = r.json()
    total_energy = sum([d["power"] for d in data])
    total_emission = sum([d["emission"] for d in data])
    return jsonify({"date": date, "total_energy": total_energy, "total_emission": total_emission})

@app.route("/")
def home():
    return "SBIR API is running"

# ✅ Railway 專案執行 Flask 所需的入口點
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
