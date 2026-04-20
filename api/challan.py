from http.server import BaseHTTPRequestHandler
import json
import requests
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone

COOKIE = (
    "trackerid=c7482668-0b20-43aa-b4e7-180211be4868; "
    "FPID=FPID2.2.vOOop48FBgBBHfz9DTTReXHKcB6XgHEEpdg1n988ZiI%3D.1756586825; "
    "FPAU=1.2.577647451.1756586828; "
    "_gtmeec=e30%3D; "
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
    "Cookie": COOKIE
}


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        params = parse_qs(parsed_url.query)

        vehicle_number = params.get("vehicle_number", [None])[0]

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        if not vehicle_number:
            self.wfile.write(json.dumps({
                "success": False,
                "message": "vehicle_number is required",
                "example": "/api/challan?vehicle_number=DL10AB1234"
            }).encode())
            return

        vehicle_number = vehicle_number.upper().replace(" ", "")
        url = f"https://www.acko.com/vas/api/v1/challans/?registration-number={vehicle_number}&source=CHALLAN_PAGE"

        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            raw = response.json()

            data = []
            for item in raw.get("data", []):
                v = item.get("violations", {})

                # Clean offences
                offences = []
                for d in v.get("details", []):
                    off = d.get("offence", "")
                    off = off.replace("( NA )", "").replace("( null )", "")
                    off = " ".join(off.split())
                    if "(" in off:
                        off = off.split("(")[0].strip()
                    if off:
                        offences.append(off)

                # Extract name
                name = (
                    item.get("owner_name")
                    or item.get("name")
                    or v.get("owner_name")
                    or v.get("name")
                    or None
                )

                data.append({
                    "number": item.get("number"),
                    "state": item.get("state"),
                    "amount": int(float(item.get("amount", {}).get("total", 0))),
                    "status": item.get("challan_status"),
                    "date": (v.get("date") or "").replace("T", " ").split(".")[0],
                    "name": name,
                    "location": v.get("location"),
                    "source": item.get("challan_search_source"),
                    "offences": list(set(offences))
                })

            result = {
                "success": True,
                "data": data
            }

            self.wfile.write(json.dumps(result, indent=2).encode())

        except requests.exceptions.Timeout:
            self.wfile.write(json.dumps({
                "success": False,
                "message": "Request timed out"
            }).encode())

        except requests.exceptions.RequestException as e:
            self.wfile.write(json.dumps({
                "success": False,
                "message": "Failed to fetch challan data",
                "error": str(e)
            }).encode())

        except Exception as e:
            self.wfile.write(json.dumps({
                "success": False,
                "message": "Unexpected error",
                "error": str(e)
            }).encode())
