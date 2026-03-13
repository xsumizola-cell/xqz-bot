# ================================================
# TELEGRAM SENDER
# ================================================
import requests
import time
from config import TELEGRAM_TOKEN, CHAT_ID, TV_SNAPSHOT_URL

API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def send_text(text, parse_mode="HTML"):
    """Kirim pesan teks ke Telegram."""
    try:
        r = requests.post(f"{API}/sendMessage", json={
            "chat_id":    CHAT_ID,
            "text":       text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False,
        }, timeout=10)
        r.raise_for_status()
        return True
    except Exception as e:
        print(f"[Telegram] send_text error: {e}")
        return False


def send_photo_url(photo_url, caption="", parse_mode="HTML"):
    """Kirim foto dari URL ke Telegram."""
    try:
        r = requests.post(f"{API}/sendPhoto", json={
            "chat_id":   CHAT_ID,
            "photo":     photo_url,
            "caption":   caption,
            "parse_mode": parse_mode,
        }, timeout=15)
        r.raise_for_status()
        return True
    except Exception as e:
        print(f"[Telegram] send_photo error: {e}")
        return False


def send_photo_file(filepath, caption="", parse_mode="HTML"):
    """Kirim foto dari file lokal ke Telegram."""
    try:
        with open(filepath, "rb") as f:
            r = requests.post(f"{API}/sendPhoto",
                data={"chat_id": CHAT_ID, "caption": caption, "parse_mode": parse_mode},
                files={"photo": f},
                timeout=15
            )
        r.raise_for_status()
        return True
    except Exception as e:
        print(f"[Telegram] send_photo_file error: {e}")
        return False


def send_alert_with_chart(text, parse_mode="HTML"):
    """
    Kirim teks alert + screenshot chart TradingView.
    TradingView snapshot URL bisa langsung dikirim sebagai foto.
    """
    # Coba kirim sebagai foto dengan caption
    try:
        r = requests.post(f"{API}/sendPhoto", json={
            "chat_id":   CHAT_ID,
            "photo":     TV_SNAPSHOT_URL,
            "caption":   text,
            "parse_mode": parse_mode,
        }, timeout=15)
        if r.status_code == 200:
            return True
    except Exception:
        pass

    # Fallback: kirim teks saja
    return send_text(text, parse_mode)


def send_divider():
    """Kirim separator visual."""
    send_text("─────────────────────")


def test_connection():
    """Test apakah bot bisa mengirim pesan."""
    return send_text(
        "🤖 <b>XQZ Trading Bot</b> — Koneksi OK\n"
        f"Chat ID: <code>{CHAT_ID}</code>\n"
        "Bot siap menerima sinyal."
    )
