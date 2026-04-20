import ccxt
import pandas as pd
import pandas_ta as ta
import telebot
import time
import os

# =====================
# TELEGRAM CONFIG
# =====================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telebot.TeleBot(TOKEN)

# =====================
# OKX CONFIG
# =====================
exchange = ccxt.okx()
symbol = 'BTC/USDT'
timeframes = ['1m', '5m', '15m']


# =====================
# SWING DETECTION
# =====================
def find_pivots(df, window=3):
    highs = df['high']
    lows = df['low']

    swing_highs = []
    swing_lows = []

    for i in range(window, len(df) - window):
        if highs[i] == max(highs[i-window:i+window+1]):
            swing_highs.append(i)

        if lows[i] == min(lows[i-window:i+window+1]):
            swing_lows.append(i)

    return swing_highs, swing_lows


# =====================
# DIVERGENCE LOGIC
# =====================
def check_divergence(df, tf):

    macd = df.ta.macd(fast=12, slow=26, signal=9)
    macd_line = macd.iloc[:, 0]

    swing_highs, swing_lows = find_pivots(df)

    # =====================
    # BULLISH DIVERGENCE
    # =====================
    if len(swing_lows) >= 2:
        l1, l2 = swing_lows[-2], swing_lows[-1]

        price_l1 = df['low'].iloc[l1]
        price_l2 = df['low'].iloc[l2]

        macd_l1 = macd_line.iloc[l1]
        macd_l2 = macd_line.iloc[l2]

        if price_l2 < price_l1 and macd_l2 > macd_l1:
            msg = f"""
🟢 PHÂN KỲ TĂNG (BULLISH)
⏱ Khung: {tf}

📉 Giá: {price_l1:.2f} → {price_l2:.2f}
📊 MACD: {macd_l1:.3f} → {macd_l2:.3f}

🚀 Có thể đảo chiều tăng
"""
            bot.send_message(CHAT_ID, msg)
            print("Bullish divergence detected")

    # =====================
    # BEARISH DIVERGENCE
    # =====================
    if len(swing_highs) >= 2:
        h1, h2 = swing_highs[-2], swing_highs[-1]

        price_h1 = df['high'].iloc[h1]
        price_h2 = df['high'].iloc[h2]

        macd_h1 = macd_line.iloc[h1]
        macd_h2 = macd_line.iloc[h2]

        if price_h2 > price_h1 and macd_h2 < macd_h1:
            msg = f"""
🔴 PHÂN KỲ GIẢM (BEARISH)
⏱ Khung: {tf}

📈 Giá: {price_h1:.2f} → {price_h2:.2f}
📊 MACD: {macd_h1:.3f} → {macd_h2:.3f}

⚠️ Có thể đảo chiều giảm
"""
            bot.send_message(CHAT_ID, msg)
            print("Bearish divergence detected")


# =====================
# MAIN LOOP
# =====================
def run():
    print("🚀 Bot đã khởi động trên Railway")

    # test Telegram khi start
    try:
        bot.send_message(CHAT_ID, "🔥 Bot đã khởi động thành công trên Railway")
    except Exception as e:
        print("Telegram error:", e)

    while True:
        try:
            for tf in timeframes:
                print(f"📊 Đang quét khung: {tf}")

                bars = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=200)
                df = pd.DataFrame(bars, columns=['ts','open','high','low','close','vol'])

                check_divergence(df, tf)
                time.sleep(1)

            print("⏳ Chờ vòng quét tiếp...")
            time.sleep(30)

        except Exception as e:
            print("❌ Lỗi:", e)
            time.sleep(10)


run()
