from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)

UPSTREAM_URL = "https://restapi.vahandetails.com/api/vehicles/search"


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "message": "Vehicle API is running"
    })


@app.route("/api/vehicle", methods=["GET"])
def vehicle():
    number = request.args.get("number", "").strip().upper()

    if not number:
        return jsonify({
            "success": False,
            "error": "Vehicle number is required"
        }), 400

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 Chrome/152.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://vahandetails.com",
        "Referer": "https://vahandetails.com/"
    }

    start = time.perf_counter()

    try:
        response = requests.get(
            UPSTREAM_URL,
            params={"rc_regn_no": number},
            headers=headers,
            timeout=15
        )

        response_time_ms = round(
            (time.perf_counter() - start) * 1000, 2
        )

        try:
            data = response.json()
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid response from upstream",
                "response_time_ms": response_time_ms
            }), 502

        return jsonify({
            "success": response.ok,
            "vehicle_number": number,
            "data": data,
            "response_time_ms": response_time_ms
        }), response.status_code

    except requests.Timeout:
        return jsonify({
            "success": False,
            "error": "Request timed out"
        }), 504

    except requests.RequestException as e:
        return jsonify({
            "success": False,
            "error": "Request failed",
            "details": str(e)
        }), 502
