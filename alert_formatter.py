# ================================================
# ALERT FORMATTER
# Format semua jenis pesan untuk Telegram
# ================================================
from datetime import datetime
import pytz
from config import TIMEZONE, SYMBOL

tz = pytz.timezone(TIMEZONE)

def now_str():
    return datetime.now(tz).strftime("%d/%m/%Y %H:%M WIB")

def price_str(p):
    try:
        return f"{float(p):,.2f}"
    except Exception:
        return str(p)

# ================================================
# FIRE ALERT — OB Cluster
# ================================================
def fmt_fire_ob(data: dict) -> str:
    """
    data keys:
        price, side (Demand/Supply), tf, dist_pct,
        confluence, quant_score, outlook, cvd
    """
    side      = data.get("side", "Demand")
    emoji     = "🟢" if side == "Demand" else "🔴"
    action    = "BELI" if side == "Demand" else "JUAL"
    tf        = data.get("tf", "H4")
    dist      = data.get("dist_pct", "--")
    conf      = data.get("confluence", "--")
    score     = data.get("quant_score", "--")
    outlook   = data.get("outlook", "--")
    cvd       = data.get("cvd", "--")
    price     = price_str(data.get("price", 0))

    return (
        f"🔴 <b>FIRE ALERT — {SYMBOL}</b>\n"
        f"{'─' * 28}\n"
        f"{emoji} <b>Harga mendekati {side} OB {tf}</b>\n\n"
        f"💰 Harga Sekarang : <b>{price}</b>\n"
        f"📏 Dist%          : <b>{dist}%</b>\n"
        f"🔗 Confluence     : <b>{conf}</b>\n"
        f"{'─' * 28}\n"
        f"📊 Quant Score    : <b>{score}/11</b>\n"
        f"🧭 Outlook {tf}    : <b>{outlook}</b>\n"
        f"📈 CVD            : <b>{cvd}</b>\n"
        f"{'─' * 28}\n"
        f"⚡ <b>Saran: Cek chart — potensi {action}</b>\n"
        f"🕐 {now_str()}"
    )


# ================================================
# FIRE ALERT — Quant Score Ekstrem
# ================================================
def fmt_fire_quant(data: dict) -> str:
    score   = data.get("score", "--")
    label   = data.get("label", "--")
    price   = price_str(data.get("price", 0))
    hurst   = data.get("hurst", "--")
    zscore  = data.get("zscore", "--")
    outlook = data.get("outlook", "--")

    is_buy  = float(score) >= 9 if str(score).replace('.','').isdigit() else True
    emoji   = "🟢" if is_buy else "🔴"
    action  = "BELI KUAT" if is_buy else "JUAL KUAT"

    return (
        f"🔴 <b>FIRE ALERT — SINYAL EKSTREM</b>\n"
        f"{'─' * 28}\n"
        f"{emoji} <b>{label} ({SYMBOL})</b>\n\n"
        f"💰 Harga       : <b>{price}</b>\n"
        f"🎯 Quant Score : <b>{score}/11</b>\n"
        f"📐 Hurst       : <b>{hurst}</b>\n"
        f"📊 Z-Score     : <b>{zscore}</b>\n"
        f"🧭 Outlook     : <b>{outlook}</b>\n"
        f"{'─' * 28}\n"
        f"⚡ <b>Saran: {action} — Konfirmasi OB</b>\n"
        f"🕐 {now_str()}"
    )


# ================================================
# FIRE ALERT — News < 4 jam
# ================================================
def fmt_fire_news(data: dict) -> str:
    event     = data.get("event", "High Impact News")
    time_wib  = data.get("time_wib", "--")
    hours_left = data.get("hours_left", "--")
    mins_left  = data.get("mins_left", "--")
    price     = price_str(data.get("price", 0))
    forecast  = data.get("forecast", "--")
    previous  = data.get("previous", "--")

    return (
        f"🔴 <b>FIRE ALERT — NEWS IMMINENT</b>\n"
        f"{'─' * 28}\n"
        f"📰 <b>{event}</b>\n\n"
        f"🕐 Waktu      : <b>{time_wib} WIB</b>\n"
        f"⏳ Dalam      : <b>{hours_left}j {mins_left}m lagi</b>\n"
        f"📈 Forecast   : <b>{forecast}</b>\n"
        f"📉 Previous   : <b>{previous}</b>\n"
        f"{'─' * 28}\n"
        f"💰 Harga Skrg : <b>{price}</b>\n"
        f"⚠️ <b>JANGAN buka posisi baru!</b>\n"
        f"🕐 {now_str()}"
    )


# ================================================
# WATCH ALERT — OB Cluster
# ================================================
def fmt_watch_ob(data: dict) -> str:
    side    = data.get("side", "Demand")
    emoji   = "🟡" if side == "Demand" else "🟠"
    tf      = data.get("tf", "H1")
    dist    = data.get("dist_pct", "--")
    price   = price_str(data.get("price", 0))
    score   = data.get("quant_score", "--")
    news_in = data.get("news_in_hours", None)

    news_line = ""
    if news_in and float(str(news_in).replace('--','999')) < 24:
        news_line = f"⚠️ News dalam {news_in}j — hati-hati\n"

    return (
        f"🟡 <b>WATCH — {SYMBOL}</b>\n"
        f"{'─' * 28}\n"
        f"{emoji} {side} OB {tf} — Dist% <b>{dist}%</b>\n"
        f"💰 Harga  : <b>{price}</b>\n"
        f"🎯 Score  : <b>{score}/11</b>\n"
        f"{news_line}"
        f"👁 Monitor — belum urgent\n"
        f"🕐 {now_str()}"
    )


# ================================================
# WATCH ALERT — Outlook berubah
# ================================================
def fmt_watch_outlook(data: dict) -> str:
    tf_signals = data.get("tf_signals", {})
    price      = price_str(data.get("price", 0))
    direction  = data.get("direction", "--")
    emoji      = "🟢" if "BELI" in direction else "🔴"

    lines = ""
    for tf, val in tf_signals.items():
        icon = "🟢" if "BELI" in val else "🔴" if "JUAL" in val else "⚪"
        lines += f"  {icon} {tf}: {val}\n"

    return (
        f"🟡 <b>WATCH — OUTLOOK UPDATE</b>\n"
        f"{'─' * 28}\n"
        f"{emoji} <b>{direction}</b> ({SYMBOL})\n\n"
        f"💰 Harga : <b>{price}</b>\n\n"
        f"Breakdown per TF:\n{lines}"
        f"{'─' * 28}\n"
        f"👁 Konfirmasi dengan OB sebelum entry\n"
        f"🕐 {now_str()}"
    )


# ================================================
# DAILY BRIEFING — 07:00 WIB
# ================================================
def fmt_briefing(data: dict) -> str:
    price      = price_str(data.get("price", 0))
    change_pct = data.get("change_pct", "--")
    change_em  = "📈" if str(change_pct).replace('-','').replace('.','').isdigit() and float(str(change_pct)) >= 0 else "📉"

    # Outlook
    d1_out = data.get("d1_outlook", "--")
    h4_out = data.get("h4_outlook", "--")
    bias   = data.get("bias", "--")
    bias_em = "🟢" if "BELI" in str(bias) else "🔴" if "JUAL" in str(bias) else "⚪"

    # OB terdekat
    dem_tf    = data.get("demand_tf", "--")
    dem_price = price_str(data.get("demand_price", 0))
    dem_dist  = data.get("demand_dist", "--")
    sup_tf    = data.get("supply_tf", "--")
    sup_price = price_str(data.get("supply_price", 0))
    sup_dist  = data.get("supply_dist", "--")

    # News hari ini
    news_list = data.get("news_today", [])
    news_lines = ""
    if news_list:
        for n in news_list:
            news_lines += f"  ⏰ {n['time']} — {n['event']}\n"
        # Ambil jam news pertama untuk saran hindari entry
        first_news_h = news_list[0].get("time", "")
        avoid_start  = news_list[0].get("avoid_from", "")
        news_lines  += f"\n  ⛔ Hindari entry {avoid_start}–{first_news_h} WIB\n"
    else:
        news_lines = "  ✅ Tidak ada high impact news hari ini\n"

    # Quant
    score   = data.get("quant_score", "--")
    hurst   = data.get("hurst", "--")
    regime  = data.get("regime", "--")

    # Saran
    saran = data.get("saran", "Pantau OB terdekat sebelum entry.")

    return (
        f"📊 <b>BRIEFING PAGI — {datetime.now(tz).strftime('%d/%m/%Y')}</b>\n"
        f"{'─' * 28}\n"
        f"💰 {SYMBOL}: <b>{price}</b>  {change_em} {change_pct}%\n\n"
        f"🧭 <b>BIAS HARI INI: {bias_em} {bias}</b>\n"
        f"  D1 Outlook : {d1_out}\n"
        f"  H4 Outlook : {h4_out}\n\n"
        f"{'─' * 28}\n"
        f"📍 <b>OB TERDEKAT:</b>\n"
        f"  🟢 Demand {dem_tf} : {dem_price}  ({dem_dist}%)\n"
        f"  🔴 Supply {sup_tf} : {sup_price}  ({sup_dist}%)\n\n"
        f"{'─' * 28}\n"
        f"📰 <b>NEWS HARI INI (USD HIGH):</b>\n"
        f"{news_lines}\n"
        f"{'─' * 28}\n"
        f"📐 Regime  : <b>{regime}</b>  |  Hurst: <b>{hurst}</b>\n"
        f"🎯 Score   : <b>{score}/11</b>\n\n"
        f"💡 <b>Saran:</b> {saran}\n"
        f"{'─' * 28}\n"
        f"🕐 {now_str()}"
    )


# ================================================
# POST-NEWS ALERT
# ================================================
def fmt_post_news(data: dict) -> str:
    event     = data.get("event", "News Event")
    price     = price_str(data.get("price", 0))
    direction = data.get("direction", "--")
    ob_formed = data.get("ob_formed", "--")
    score     = data.get("quant_score", "--")
    em        = "🟢" if direction == "BULLISH" else "🔴"

    return (
        f"🔵 <b>POST-NEWS — {SYMBOL}</b>\n"
        f"{'─' * 28}\n"
        f"📰 {event} — selesai\n\n"
        f"{em} Reaksi    : <b>{direction}</b>\n"
        f"💰 Harga    : <b>{price}</b>\n"
        f"📦 OB Baru  : <b>{ob_formed}</b>\n"
        f"🎯 Score    : <b>{score}/11</b>\n"
        f"{'─' * 28}\n"
        f"🔵 <b>Window opportunity — cari OB retest</b>\n"
        f"🕐 {now_str()}"
    )
