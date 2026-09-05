from flask import Flask, request, jsonify
import requests

app = Flask(name)

API_URL = "https://backend.vahandetails.com/api/get-challans-details"
API_KEY = "Test_1234"

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": True,
        "message": "Challan API Running"
    })

@app.route("/challan", methods=["GET"])
def challan():
    rc_number = request.args.get("rc")

    if not rc_number:
        return jsonify({
            "status": False,
            "message": "rc parameter required"
        }), 400

    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY,
        "User-Agent": "Mozilla/5.0"
    }

    payload = {
        "rc_number": rc_number.upper()
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)

        try:
            data = response.json()
        except:
            return jsonify({
                "status": False,
                "raw": response.text
            }), 500

        return jsonify(data)

    except Exception as e:
        return jsonify({
            "status": False,
            "error": str(e)
        }), 500

if name == "main":
    app.run(debug=True)
