from flask_cors import CORS
from flask import Flask, request, jsonify
import requests
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

app = Flask(__name__)
CORS(app)  # ✅ 允許跨來源請求

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

from datetime import datetime, timedelta, timezone

@app.route("/summary-by-date", methods=["GET"])
def summary_by_date():
    date_str = request.args.get("date")  # e.g., "2025-05-27"
    if not date_str:
        return jsonify({"error": "Missing date"}), 400

    try:
        # 建立 UTC 時區的起始與結束時間
        tz = timezone.utc
        date_start = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=tz)
        date_end = date_start + timedelta(days=1)

        start_iso = date_start.isoformat()  # e.g., "2025-05-27T00:00:00+00:00"
        end_iso = date_end.isoformat()      # e.g., "2025-05-28T00:00:00+00:00"

        url = f"{SUPABASE_URL}/rest/v1/device_logs?timestamp=gte.{start_iso}&timestamp=lt.{end_iso}"
        r = requests.get(url, headers=headers)
        if not r.ok:
            return jsonify({"error": "Failed to fetch data"}), 400

        data = r.json()
        total_energy = sum([d.get("energy_wh", 0) for d in data])
        total_emission = sum([d.get("co2_emission", 0) for d in data])

        device_counts = {}
        for d in data:
            device_id = d.get("device_id", "unknown")
            device_counts[device_id] = device_counts.get(device_id, 0) + 1

        return jsonify({
            "date": date_str,
            "data_count": len(data),
            "total_energy": round(total_energy, 2),
            "total_emission": round(total_emission, 2),
            "device_counts": device_counts
        })
    except Exception as e:
        return jsonify({"error": f"解析失敗: {str(e)}"}), 500

@app.route("/")
def home():
    return "SBIR API is running"

# ✅ Railway 專案執行 Flask 所需的入口點
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
