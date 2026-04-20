from http.server import BaseHTTPRequestHandler
import requests
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs

COOKIE = "YOUR_COOKIE_HERE"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Origin": "https://www.acko.com",
    "Referer": "https://www.acko.com/",
    "Cookie": COOKIE,
}

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        vehicle = query.get("vehicle_number", [None])[0]

        if not vehicle:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error":"Missing vehicle_number"}')
            return

        url = f"https://www.acko.com/vas/api/v1/challans/?registration-number={vehicle}&source=CHALLAN_PAGE"

        try:
            res = requests.get(url, headers=HEADERS, timeout=10)

            output = {
                "vehicle_number": vehicle,
                "status": res.status_code,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "data": res.json()
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(str(output).encode())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str({"error": str(e)}).encode())
