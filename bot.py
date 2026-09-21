import requests
import time
import os
from datetime import datetime
from threading import Thread
from flask import Flask

# ===== تنظیمات =====
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
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    
    if not token or not chat_id:
        print("❌ ERROR: TELEGRAM_TOKEN or CHAT_ID is not set in Environment!")
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try:
        r = requests.post(url, data=data, timeout=10)
        print(f"TELEGRAM RESPONSE: {r.text}")
    except Exception as e:
        print(f"خطا در ارسال پیام: {e}")

def get_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return {
            "price": float(data["lastPrice"]),
            "change": float(data["priceChangePercent"]),
            "low": float(data["lowPrice"])
        }
    except Exception as e:
        print(f"خطا در گرفتن قیمت {symbol}: {e}")
        return None

def analyze(symbol):
    data = get_price(symbol)
    if not data:
        return None
    price = data["price"]
    low = data["low"]
    change = data["change"]
    if ((price - low) / low) * 100 < 2 and change < 0:
        return {
            "symbol": symbol,
            "entry": price,
            "tp": price * 1.1,
            "sl": price * 0.95,
            "change": change
        }
    return None

def bot_loop():
    print(f"CHECK ENV KEYS: {[k for k in os.environ.keys() if 'TELEGRAM' in k or 'CHAT' in k]}")
    
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    print(f"BOT LOOP STARTED - Token exists: {token is not None} - Chat exists: {chat_id is not None}")
    
    send_telegram("🤖 ربات روشن شد!")
    
    while True:
        try:
            now = datetime.now().strftime("%H:%M")
            signals = []
            for s in SYMBOLS:
                result = analyze(s)
                if result:
                    signals.append(result)
            if signals:
                msg = f"🔔 <b>سیگنال جدید - {now}</b>\n\n"
                for s in signals:
                    msg += f"🟢 <b>{s['symbol']}</b>\n"
                    msg += f"💰 ورود: {s['entry']:.4f}\n"
                    msg += f"🎯 سود: {s['tp']:.4f}\n"
                    msg += f"🛑 ضرر: {s['sl']:.4f}\n"
                    msg += f"📉 تغییر: {s['change']:.2f}%\n\n"
                send_telegram(msg)
            time.sleep(300)
        except Exception as e:
            print(f"خطا: {e}")
            time.sleep(60)

if __name__ == "__main__":
    Thread(target=run_web_server).start()
    bot_loop()
