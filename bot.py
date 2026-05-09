import requests, time, os
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "1838882696")
NIN = os.environ.get("NIN", "")
PASSWORD = os.environ.get("PASSWORD", "")
WILAYA = "Annaba"

S = requests.Session()
S.headers.update({
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Linux; Android 13) Chrome/120.0.0.0",
    "Accept": "application/json",
    "Origin": "https://adhahi.dz",
    "Referer": "https://adhahi.dz/register"
})

def login():
    r = S.post("https://adhahi.dz/api/auth/login",
               json={"nin": NIN, "password": PASSWORD}, timeout=15)
    d = r.json()
    t = d.get("token") or d.get("access_token") or (d.get("data") or {}).get("token")
    if t:
        S.headers["Authorization"] = "Bearer " + t
        print("LOGIN OK")
        return True
    print("LOGIN FAIL", d)
    return False

def get_wilayas():
    r = S.get("https://adhahi.dz/api/booking/wilayas", timeout=15)
    if r.status_code == 401:
        login()
        r = S.get("https://adhahi.dz/api/booking/wilayas", timeout=15)
    print("WILAYAS:", r.status_code, r.text[:200])
    return r.json()

def notif(m):
    requests.post(
        "https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage",
        json={"chat_id": CHAT_ID, "text": m}, timeout=10)

def avail(data):
    out = []
    items = data if isinstance(data, list) else data.get("data", data.get("wilayas", []))
    for w in items:
        n = w.get("name") or w.get("nom") or w.get("wilaya", "")
        s = str(w.get("available", w.get("status", w.get("booking_open", "")))).lower()
        if s not in ["false", "0", "closed", "none", "", "غير متوفر"]:
            out.append(n)
    return out

print("START", datetime.now())
if login():
    data = get_wilayas()
    if data:
        cur = avail(data)
        print("Available:", cur)
        if cur:
            notif("HEJZ MEFTOH!\n" + "\n".join(cur))
        if WILAYA in cur:
            notif("TAZKER! " + WILAYA + " متاح الآن!")
    else:
        print("No data")
else:
    notif("LOGIN FAIL - Check credentials")
