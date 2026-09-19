import requests
import time
import os
from datetime import datetime
from threading import Thread
from flask import Flask

# ===== تنظیمات =====
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "YOUR_TOKEN_HERE")
CHAT_ID = os.environ.get("CHAT_ID", "YOUR_CHAT_ID_HERE")
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
TAKE_PROFIT = 10
STOP_LOSS = 5

# ===== وب‌سرور ساده =====
app = Flask(__name__)

@app.route('/')
def health():
    return "Bot is alive!", 200

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ===== توابع ربات =====
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"خطا در ارسال پیام: {e}")

def get_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return {"price": float(data["lastPrice"]), "change": float(data["priceChangePercent"]), "low": float(data["lowPrice"])}
    except Exception as e:
        print(f"خطا در گرفتن قیمت {symbol}: {e}")
        return None

def analyze(symbol):
    data = get_price(symbol)
    if not data:
        return None
    price, low, change = data["price"], data["low"], data["change"]
    if ((price - low) / low) * 100 < 2 and change < 0:
        return {"symbol": symbol, "entry": price, "tp": price * 1.1, "sl": price * 0.95, "change": change}
    return None

def bot_loop():
    send_telegram("🤖 ربات روشن شد!")
    while True:
        try:
            now = datetime.now().strftime("%H:%M")
            signals = [analyze(s) for s in SYMBOLS]
            signals = [s for s in signals if s]
            if signals:
                msg = f"🔔 <b>سیگنال جدید - {now}</b>\n\n"
                for s in signals:
                    msg += f"🟢 <b>{s['symbol']}</b>\n💰 ورود: {s['entry']:.4f}\n🎯 سود: {s['tp']:.4f}\n🛑 ضرر: {s['sl']:.4f}\n📉 تغییر: {s['change']:.2f}%\n\n"
                send_telegram(msg)
            time.sleep(300)
        except Exception as e:
            print(f"خطا: {e}")
            time.sleep(60)

if __name__ == "__main__":
    Thread(target=run_web_server).start()
    bot_loop()
