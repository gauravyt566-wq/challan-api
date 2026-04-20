from http.server import BaseHTTPRequestHandler
import json
import requests
import re
from urllib.parse import urlparse, parse_qs
from datetime import datetime

COOKIE = "trackerid=c7482668-0b20-43aa-b4e7-180211be4868; FPID=FPID2.2.vOOop48FBgBBHfz9DTTReXHKcB6XgHEEpdg1n988ZiI%3D.1756586825; FPAU=1.2.577647451.1756586828; _gtmeec=e30%3D; _fbp=fb.1.1756586827824.1865711757; user_id=xdwK3S6Qg0yZVOxOeFWWLg:1756587589955:6e9f1879506e024e198c438011da65b37afbe84c; _gcl_au=1.1.1799176003.1758281461; ajs_anonymous_id=c7482668-0b20-43aa-b4e7-180211be4868; ajs_user_id=xdwK3S6Qg0yZVOxOeFWWLg; _ga=GA1.1.1660367126.1756586825; __cf_bm=6ZAxLsPPTZCT9LVrIJF1MFrTn9WjWYnJWVcntSPW.io-1763618863-1.0.1.1-4qIpzes2gSXo.XTnAw_E1WSYQ5a27k4Asdm9qTnJW1azmF_ijlCPTA3nS1Cs56iFYWuI1qG6SaRsKeN.YVAHgrURS5W2bZDhO6twB6_6xiw"

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

        if not vehicle_number:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "message": "vehicle_number is required"}).encode())
            return

        vehicle_number = vehicle_number.upper().replace(" ", "")
        url = f"https://www.acko.com/vas/api/v1/challans/?registration-number={vehicle_number}&source=CHALLAN_PAGE"
        fetched_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            raw = resp.json()
            challans = raw.get("data", {}).get("challans", []) if isinstance(raw, dict) else []
            
            cleaned = []
            for c in challans:
                if not isinstance(c, dict):
                    continue
                amt = c.get("amount", {})
                amount = int(amt.get("total", 0)) if isinstance(amt, dict) else 0
                
                raw_off = c.get("offence", [])
                offences = []
                seen = set()
                for o in (raw_off if isinstance(raw_off, list) else []):
                    if isinstance(o, str):
                        o_clean = re.sub(r'\(NA\)|\(null\)', '', o, flags=re.IGNORECASE).strip()
                        o_clean = re.sub(r'\([^)]*(?:section|act|rule)[^)]*\)', '', o_clean, flags=re.IGNORECASE)
                        o_clean = re.sub(r'\s+', ' ', o_clean).strip()
                        if o_clean and o_clean.lower() not in seen:
                            seen.add(o_clean.lower())
                            offences.append(o_clean)
                
                date_str = c.get("date", "")
                try:
                    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    date_fmt = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    date_fmt = ""
                
                cleaned.append({
                    "number": c.get("number", ""),
                    "state": c.get("state", ""),
                    "amount": amount,
                    "status": c.get("status", ""),
                    "date": date_fmt,
                    "location": c.get("location", ""),
                    "offences": offences
                })

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "vehicle_number": vehicle_number,
                "total_challans": len(cleaned),
                "fetched_on": fetched_on,
                "data": cleaned
            }).encode())

        except requests.exceptions.Timeout:
            self.send_response(504)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "message": "Request timed out"}).encode())
        except requests.exceptions.RequestException:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "message": "Failed to fetch challan data"}).encode())
        except Exception:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "message": "Internal server error"}).encode())
