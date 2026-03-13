# ================================================
# MAIN — XQZ Trading Bot
# Jalankan webhook handler + briefing scheduler
# secara bersamaan (threading)
# ================================================
import threading
import time
import schedule
from datetime import datetime
import pytz

from config import TIMEZONE, BRIEFING_HOUR_WIB, WEBHOOK_PORT
from telegram_sender import test_connection
from briefing import send_morning_briefing, run_scheduler
from webhook_handler import app

tz = pytz.timezone(TIMEZONE)

def run_webhook():
    """Jalankan Flask webhook server."""
    print(f"[Webhook] Server starting on port {WEBHOOK_PORT}...")
    app.run(host="0.0.0.0", port=WEBHOOK_PORT, debug=False, use_reloader=False)

def run_briefing():
    """Jalankan briefing scheduler."""
    briefing_time = f"{BRIEFING_HOUR_WIB:02d}:00"
    print(f"[Briefing] Scheduler starting — setiap hari {briefing_time} WIB")
    schedule.every().day.at(briefing_time).do(send_morning_briefing)
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    print("=" * 50)
    print("  XQZ TRADING BOT — Starting")
    print(f"  {datetime.now(tz).strftime('%Y-%m-%d %H:%M WIB')}")
    print("=" * 50)

    # Test koneksi Telegram
    print("[Bot] Testing Telegram connection...")
    if test_connection():
        print("[Bot] Telegram OK")
    else:
        print("[Bot] Telegram GAGAL — cek token di config.py")

    # Jalankan webhook + briefing bersamaan
    t1 = threading.Thread(target=run_webhook,  daemon=True)
    t2 = threading.Thread(target=run_briefing, daemon=True)

    t1.start()
    t2.start()

    print("[Bot] Semua service aktif. Bot berjalan...")

    # Keep main thread alive
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n[Bot] Stopped.")
