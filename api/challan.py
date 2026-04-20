from flask import Flask, jsonify, request
import requests
from datetime import datetime, timezone

app = Flask(__name__)

COOKIE = (
    "trackerid=c7482668-0b20-43aa-b4e7-180211be4868; "
    "FPID=FPID2.2.vOOop48FBgBBHfz9DTTReXHKcB6XgHEEpdg1n988ZiI%3D.1756586825; "
    "FPAU=1.2.577647451.1756586828; _gtmeec=e30%3D; "
    "_fbp=fb.1.1756586827824.1865711757; "
    "user_id=xdwK3S6Qg0yZVOxOeFWWLg:1756587589955:6e9f1879506e024e198c438011da65b37afbe84c; "
    "_gcl_au=1.1.1799176003.1758281461; "
    "ajs_anonymous_id=c7482668-0b20-43aa-b4e7-180211be4868; "
    "ajs_user_id=xdwK3S6Qg0yZVOxOeFWWLg; "
    "_ga=GA1.1.1660367126.1756586825; "
    "__cf_bm=6ZAxLsPPTZCT9LVrIJF1MFrTn9WjWYnJWVcntSPW.io-1763618863-1.0.1.1-4qIpzes2gSXo.XTnAw_E1WSYQ5a27k4Asdm9qTnJW1azmF_ijlCPTA3nS1Cs56iFYWuI1qG6SaRsKeN.YVAHgrURS5W2bZDhO6twB6_6xiw"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Origin": "https://www.acko.com",
    "Referer": "https://www.acko.com/",
    "Cookie": COOKIE,
}

@app.route("/api/challan", methods=["GET"])
def get_challan():
    vehicle = request.args.get("vehicle_number")
    
    if not vehicle:
        return jsonify({
            "error": "Missing vehicle_number",
            "example": "/api/challan?vehicle_number=DL10AB1234"
        }), 400
    
    url = f"https://www.acko.com/vas/api/v1/challans/?registration-number={vehicle}&source=CHALLAN_PAGE"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        return jsonify({
            "vehicle_number": vehicle,
            "status": response.status_code,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "data": response.json()
        }), 200
    
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out"}), 504
    
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to fetch challan", "message": str(e)}), 500
    
    except Exception as e:
        return jsonify({"error": "Unexpected error", "message": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Challan API is running",
        "usage": "/api/challan?vehicle_number=VEHICLE_NUMBER",
        "example": "/api/challan?vehicle_number=DL10AB1234"
    })

# Vercel requires this
app.debug = False
