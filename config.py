# ================================================
# XQZ TRADING BOT — CONFIG
# ================================================
# PENTING: Ganti TELEGRAM_TOKEN dengan token baru Anda
# Jangan pernah share file ini ke publik

TELEGRAM_TOKEN   = "8646798354:AAHAvTT2fKeeeDiDzBldy6FyOYD0s8UKkew"
CHAT_ID          = "1675630605"

# TradingView chart snapshot base URL
TV_CHART_ID      = "jwwgzT2J"
TV_SNAPSHOT_URL  = f"https://www.tradingview.com/x/{TV_CHART_ID}/"

# Webhook server
WEBHOOK_PORT     = 8080
WEBHOOK_SECRET   = "xqz_webhook_secret_2026"

# Briefing jadwal (WIB / UTC+7)
BRIEFING_HOUR_WIB = 7    # 07:00 WIB setiap hari

# Timezone
TIMEZONE = "Asia/Jakarta"

# Alert thresholds
OB_DIST_FIRE     = 0.5   # % Dist untuk FIRE ALERT
OB_DIST_WATCH    = 1.5   # % Dist untuk WATCH ALERT
QUANT_FIRE       = 9     # Score >= 9 = FIRE
QUANT_WATCH      = 7     # Score >= 7 = WATCH
NEWS_FIRE_HOURS  = 4     # Jam sebelum news = FIRE
NEWS_WATCH_HOURS = 24    # Jam sebelum news = WATCH

# Symbol
SYMBOL = "BTC/USDT"
