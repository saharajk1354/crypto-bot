import requests
import time
import os
from datetime import datetime

# ===== تنظیمات =====
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "YOUR_TOKEN_HERE")
CHAT_ID = os.environ.get("CHAT_ID", "YOUR_CHAT_ID_HERE")

# ===== تنظیمات WEEX =====
WEEX_API_KEY = os.environ.get("WEEX_API_KEY", "YOUR_API_KEY_HERE")
WEEX_SECRET_KEY = os.environ.get("WEEX_SECRET_KEY", "YOUR_SECRET_KEY_HERE")
WEEX_PASSPHRASE = os.environ.get("WEEX_PASSPHRASE", "YOUR_PASSPHRASE_HERE")

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]

TAKE_PROFIT = 10
STOP_LOSS = 5
MAX_OPEN_TRADES = 2
MAX_TRADE_HOURS = 48

# ===== توابع =====

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
        return {
            "price": float(data["lastPrice"]),
            "change": float(data["priceChangePercent"]),
            "high": float(data["highPrice"]),
            "low": float(data["lowPrice"]),
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
    
    distance_from_low = ((price - low) / low) * 100
    
    if distance_from_low < 2 and change < 0:
        entry = price
        tp = entry * (1 + TAKE_PROFIT / 100)
        sl = entry * (1 - STOP_LOSS / 100)
        return {
            "symbol": symbol,
            "entry": entry,
            "tp": tp,
            "sl": sl,
            "change": change,
        }
    return None

def main():
    send_telegram("🤖 ربات تحلیل بازار روشن شد!\n\nدر حال رصد ارزها...")
    
    while True:
        try:
            now = datetime.now().strftime("%H:%M")
            signals = []
            
            for symbol in SYMBOLS:
                result = analyze(symbol)
                if result:
                    signals.append(result)
            
            if signals:
                msg = f"🔔 <b>سیگنال جدید - {now}</b>\n\n"
                for s in signals:
                    msg += f"🟢 <b>{s['symbol']}</b>\n"
                    msg += f"💰 ورود: {s['entry']:.4f}\n"
                    msg += f"🎯 حد سود: {s['tp']:.4f}\n"
                    msg += f"🛑 حد ضرر: {s['sl']:.4f}\n"
                    msg += f"📉 تغییر ۲۴س: {s['change']:.2f}%\n\n"
                send_telegram(msg)
            
            time.sleep(300)
            
        except Exception as e:
            print(f"خطا: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
