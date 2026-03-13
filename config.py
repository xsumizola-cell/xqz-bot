import os

TELEGRAM_TOKEN    = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID           = os.environ.get("CHAT_ID", "1675630605")
TV_CHART_ID       = "jwwgzT2J"
TV_SNAPSHOT_URL   = f"https://www.tradingview.com/x/{TV_CHART_ID}/"
WEBHOOK_PORT      = int(os.environ.get("PORT", 8080))
WEBHOOK_SECRET    = "xqz_webhook_secret_2026"
BRIEFING_HOUR_WIB = 7
TIMEZONE          = "Asia/Jakarta"
SYMBOL            = "BTC/USDT"
OB_DIST_FIRE      = 0.5
OB_DIST_WATCH     = 1.5
QUANT_FIRE        = 9
QUANT_WATCH       = 7
NEWS_FIRE_HOURS   = 4
NEWS_WATCH_HOURS  = 24
```

Commit changes.

---

**STEP 2 — Update `Procfile` di GitHub**

Klik `Procfile` → edit → hapus semua → paste ini:
```
web: gunicorn main:app --bind 0.0.0.0:$PORT --workers 1 --threads 2
```

Commit changes.

---

**STEP 3 — Update `requirements.txt`**

Klik `requirements.txt` → edit → pastikan isinya:
```
flask==3.0.0
requests==2.31.0
schedule==1.2.1
pytz==2024.1
gunicorn==21.2.0
