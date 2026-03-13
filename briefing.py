# ================================================
# BRIEFING SCHEDULER
# Kirim briefing pagi 07:00 WIB setiap hari
# Jalankan terus di Railway sebagai background process
# ================================================
import time
import schedule
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import pytz

from config import TIMEZONE, BRIEFING_HOUR_WIB, SYMBOL
from telegram_sender import send_alert_with_chart, send_text
from alert_formatter import fmt_briefing

tz  = pytz.timezone(TIMEZONE)
wib = timezone(timedelta(hours=7))
utc = timezone.utc

# ================================================
# FETCH HARGA DARI BINANCE (gratis, no API key)
# ================================================
def get_btc_price():
    try:
        r = requests.get(
            "https://api.binance.com/api/v3/ticker/24hr",
            params={"symbol": "BTCUSDT"}, timeout=5
        )
        d = r.json()
        return {
            "price":      float(d["lastPrice"]),
            "change_pct": round(float(d["priceChangePercent"]), 2),
        }
    except Exception as e:
        print(f"[Binance] Error: {e}")
        return {"price": 0, "change_pct": 0}


# ================================================
# FETCH NEWS DARI FOREX FACTORY XML
# ================================================
def get_todays_news():
    url     = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
    headers = {"User-Agent": "Mozilla/5.0 Chrome/120.0.0.0"}
    events  = []
    try:
        r    = requests.get(url, headers=headers, timeout=10)
        root = ET.fromstring(r.content)
        now_wib   = datetime.now(wib)
        today_str = now_wib.strftime("%m-%d-%Y")

        for ev in root.findall("event"):
            def g(tag):
                el = ev.find(tag)
                return el.text.strip() if el is not None and el.text else ""

            if g("country") != "USD" or g("impact") != "High":
                continue
            if g("date") != today_str:
                continue
            if not g("time") or g("time").lower() in ["all day", "tentative"]:
                continue

            # Convert UTC → WIB
            ts = g("time").strip().lower()
            for fmt in ["%m-%d-%Y %I:%M%p", "%m-%d-%Y %I%p"]:
                try:
                    dt = datetime.strptime(f"{g('date')} {ts}", fmt).replace(tzinfo=utc)
                    dt_wib = dt.astimezone(wib)

                    # Jam hindari entry = 4 jam sebelum news
                    avoid_dt   = dt_wib - timedelta(hours=4)
                    avoid_from = avoid_dt.strftime("%H:%M")

                    events.append({
                        "event":      g("title"),
                        "time":       dt_wib.strftime("%H:%M"),
                        "forecast":   g("forecast"),
                        "previous":   g("previous"),
                        "avoid_from": avoid_from,
                    })
                    break
                except ValueError:
                    pass
    except Exception as e:
        print(f"[FF Calendar] Error: {e}")

    return events


# ================================================
# GENERATE SARAN OTOMATIS
# Berdasarkan data yang tersedia
# ================================================
def generate_saran(data: dict) -> str:
    bias     = data.get("bias", "NETRAL")
    dem_dist = str(data.get("demand_dist", "99"))
    sup_dist = str(data.get("supply_dist", "99"))
    news     = data.get("news_today", [])
    score    = data.get("quant_score", 5)

    try:
        dd = float(dem_dist)
        sd = float(sup_dist)
        sc = float(str(score))
    except Exception:
        dd, sd, sc = 99, 99, 5

    # Ada news hari ini
    if news:
        first = news[0]
        return (
            f"Ada {len(news)} news HIGH impact hari ini. "
            f"Hindari entry baru {first['avoid_from']}–{first['time']} WIB. "
            f"Masuk setelah news jika OB konfirm."
        )

    # Harga dekat demand
    if dd < 1.0 and "BELI" in bias:
        return f"Demand OB terdekat hanya {dd}% — potensi entry beli jika CVD berbalik positif."

    # Harga dekat supply
    if sd < 1.0 and "JUAL" in bias:
        return f"Supply OB terdekat hanya {sd}% — waspadai penolakan, pertimbangkan reduce posisi."

    # Score tinggi
    if sc >= 8:
        return "Quant score tinggi — sinyal beli kuat. Konfirmasi dengan OB sebelum entry."

    # Score rendah
    if sc <= 3:
        return "Quant score rendah — hindari entry beli. Waspadai kelanjutan tekanan jual."

    # Default
    return "Pantau OB terdekat. Tunggu konfluensi minimal 3 cluster sebelum entry."


# ================================================
# KIRIM BRIEFING
# ================================================
def send_morning_briefing():
    print(f"[Briefing] Sending at {datetime.now(tz).strftime('%H:%M WIB')}...")

    # Fetch data live
    price_data = get_btc_price()
    news_today = get_todays_news()

    # Data briefing — untuk OB/Quant/Outlook
    # Ini diisi dari Pine Script via webhook jika ada
    # Fallback: gunakan placeholder yang informatif
    data = {
        # Harga live dari Binance
        "price":       price_data["price"],
        "change_pct":  price_data["change_pct"],

        # Outlook — akan diisi oleh Pine Script webhook
        # Sementara gunakan nilai default
        "bias":        "Cek chart",
        "d1_outlook":  "Cek chart",
        "h4_outlook":  "Cek chart",

        # OB terdekat — akan diisi oleh Pine Script webhook
        "demand_tf":    "H4",
        "demand_price": 0,
        "demand_dist":  "--",
        "supply_tf":    "H4",
        "supply_price": 0,
        "supply_dist":  "--",

        # Quant
        "quant_score": "--",
        "hurst":       "--",
        "regime":      "--",

        # News hari ini dari FF XML
        "news_today":  news_today,
    }

    data["saran"] = generate_saran(data)

    msg = fmt_briefing(data)
    send_alert_with_chart(msg)
    print(f"[Briefing] Sent OK")


# ================================================
# SCHEDULER SETUP
# ================================================
def run_scheduler():
    briefing_time = f"{BRIEFING_HOUR_WIB:02d}:00"
    print(f"[Scheduler] Briefing dijadwalkan: {briefing_time} WIB setiap hari")

    schedule.every().day.at(briefing_time).do(send_morning_briefing)

    # Test kirim saat pertama jalan (opsional — comment jika tidak mau)
    # send_morning_briefing()

    while True:
        schedule.run_pending()
        time.sleep(30)  # Cek setiap 30 detik


if __name__ == "__main__":
    print("[XQZ Bot] Briefing scheduler starting...")
    run_scheduler()
