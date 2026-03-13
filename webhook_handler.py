# ================================================
# WEBHOOK HANDLER
# Menerima alert dari TradingView Pine Script
# lalu format dan kirim ke Telegram
# ================================================
from flask import Flask, request, jsonify
from datetime import datetime
import pytz
import json
import hmac
import hashlib

from config import WEBHOOK_SECRET, TIMEZONE, WEBHOOK_PORT
from telegram_sender import send_alert_with_chart, send_text
from alert_formatter import (
    fmt_fire_ob, fmt_fire_quant, fmt_fire_news,
    fmt_watch_ob, fmt_watch_outlook, fmt_post_news
)

app = Flask(__name__)
tz  = pytz.timezone(TIMEZONE)

# ================================================
# HELPER — parse payload dari TradingView
# TradingView kirim JSON via webhook
# ================================================
def parse_tv_payload(raw: dict) -> dict:
    """
    TradingView webhook payload format:
    {
        "type":       "fire_ob" | "fire_quant" | "fire_news" |
                      "watch_ob" | "watch_outlook" | "post_news",
        "price":      "71120.50",
        "side":       "Demand" | "Supply",
        "tf":         "H4",
        "dist_pct":   "0.42",
        "confluence": "KUAT 3/4",
        "score":      "9",
        "outlook":    "BELI KUAT",
        "cvd":        "Positif ▲",
        "event":      "Core PCE m/m",
        "time_wib":   "19:30",
        "hours_left": "3",
        "mins_left":  "45",
        "forecast":   "0.3%",
        "previous":   "0.4%",
        "hurst":      "0.42",
        "zscore":     "-2.1",
        "label":      "STRONG BUY",
        "direction":  "BULLISH",
        "ob_formed":  "69,240"
    }
    """
    return raw


# ================================================
# ROUTE — Health check
# ================================================
@app.route("/", methods=["GET"])
def health():
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M WIB")
    return jsonify({"status": "ok", "time": now, "bot": "XQZ Trading Bot"})


# ================================================
# ROUTE — TradingView Webhook
# ================================================
@app.route("/webhook", methods=["POST"])
def webhook():
    # Verifikasi secret
    secret = request.headers.get("X-Webhook-Secret", "")
    if secret != WEBHOOK_SECRET:
        return jsonify({"error": "Unauthorized"}), 401

    # Parse payload
    try:
        if request.content_type == "application/json":
            data = request.get_json(force=True)
        else:
            # TradingView kadang kirim sebagai text
            raw  = request.data.decode("utf-8")
            data = json.loads(raw)
    except Exception as e:
        return jsonify({"error": f"Parse error: {e}"}), 400

    alert_type = data.get("type", "unknown")
    print(f"[Webhook] Received: {alert_type} at {datetime.now(tz).strftime('%H:%M:%S')}")

    # Route ke formatter yang sesuai
    msg = None
    try:
        if alert_type == "fire_ob":
            msg = fmt_fire_ob(data)
        elif alert_type == "fire_quant":
            msg = fmt_fire_quant(data)
        elif alert_type == "fire_news":
            msg = fmt_fire_news(data)
        elif alert_type == "watch_ob":
            msg = fmt_watch_ob(data)
        elif alert_type == "watch_outlook":
            msg = fmt_watch_outlook(data)
        elif alert_type == "post_news":
            msg = fmt_post_news(data)
        else:
            # Unknown type — kirim raw sebagai fallback
            msg = f"⚠️ <b>Alert dari TradingView</b>\n\n<code>{json.dumps(data, indent=2)}</code>"
    except Exception as e:
        msg = f"⚠️ <b>Alert Error</b>\nType: {alert_type}\nError: {e}"

    # Kirim ke Telegram dengan screenshot chart
    if msg:
        send_alert_with_chart(msg)

    return jsonify({"status": "ok", "type": alert_type}), 200


# ================================================
# ROUTE — Test manual (untuk cek bot hidup)
# ================================================
@app.route("/test", methods=["GET"])
def test():
    send_text(
        "🤖 <b>XQZ Trading Bot — Test OK</b>\n"
        f"Server aktif: {datetime.now(tz).strftime('%d/%m/%Y %H:%M WIB')}"
    )
    return jsonify({"status": "test sent"}), 200


# ================================================
# MAIN
# ================================================
if __name__ == "__main__":
    print(f"[XQZ Bot] Webhook server starting on port {WEBHOOK_PORT}...")
    app.run(host="0.0.0.0", port=WEBHOOK_PORT)
