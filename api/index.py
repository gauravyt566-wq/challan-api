from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)

UPSTREAM_URL = "https://restapi.vahandetails.com/api/vehicles/search"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://vahandetails.com",
    "Referer": "https://vahandetails.com/"
}


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "message": "Challan API is running"
    })


@app.route("/api/vehicle", methods=["GET"])
def vehicle():
    number = request.args.get("number", "").strip().upper()

    if not number:
        return jsonify({
            "success": False,
            "error": "Vehicle number is required"
        }), 400

    start = time.perf_counter()

    try:
        response = requests.get(
            UPSTREAM_URL,
            params={"rc_regn_no": number},
            headers=HEADERS,
            timeout=15
        )

        response_time_ms = round(
            (time.perf_counter() - start) * 1000,
            2
        )

        try:
            result = response.json()
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid response from upstream",
                "response_time_ms": response_time_ms
            }), 502

        challans = []

        if isinstance(result, dict):
            outer_data = result.get("data", {})

            if isinstance(outer_data, dict):
                inner_data = outer_data.get("data", {})

                if isinstance(inner_data, dict):
                    challans = inner_data.get("challans", [])

        return jsonify({
            "success": True,
            "vehicle_number": number,
            "challans": challans,
            "challan_count": len(challans),
            "response_time_ms": response_time_ms
        })

    except requests.Timeout:
        return jsonify({
            "success": False,
            "error": "Request timed out"
        }), 504

    except requests.RequestException as e:
        return jsonify({
            "success": False,
            "error": "Upstream request failed",
            "details": str(e)
        }), 502

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500
