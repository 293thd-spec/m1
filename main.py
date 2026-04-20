import ccxt
import pandas as pd
import pandas_ta as ta
import telebot
import time
import os
import traceback

# =====================
# TELEGRAM
# =====================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telebot.TeleBot(TOKEN)

# =====================
# EXCHANGE
# =====================
exchange = ccxt.okx({
    "enableRateLimit": True
})

symbol = "BTC/USDT"
timeframes = ["1m", "5m", "15m"]


# =====================
# SWING DETECT
# =====================
def find_pivots(df, window=3):
    highs = df["high"]
    lows = df["low"]

    swing_highs = []
    swing_lows = []

    for i in range(window, len(df) - window):
        if highs[i] == max(highs[i-window:i+window+1]):
            swing_highs.append(i)

        if lows[i] == min(lows[i-window:i+window+1]):
            swing_lows.append(i)

    return swing_highs, swing_lows


# =====================
# DIVERGENCE
# =====================
def check_divergence(df, tf):

    macd = df.ta.macd(fast=12, slow=26, signal=9)
    macd_line = macd.iloc[:, 0]

    swing_highs, swing_lows = find_pivots(df)

    # ===== BULLISH =====
    if len(swing_lows) >= 2:
        l1, l2 = swing_lows[-2], swing_lows[-1]

        if df["low"].iloc[l2] < df["low"].iloc[l1] and macd_line.iloc[l2] > macd_line.iloc[l1]:
            msg = f"""
🟢 PHÂN KỲ TĂNG
⏱ {tf}
📉 {df['low'].iloc[l1]:.2f} → {df['low'].iloc[l2]:.2f}
"""
            bot.send_message(CHAT_ID, msg)

    # ===== BEARISH =====
    if len(swing_highs) >= 2:
        h1, h2 = swing_highs[-2], swing_highs[-1]

        if df["high"].iloc[h2] > df["high"].iloc[h1] and macd_line.iloc[h2] < macd_line.iloc[h1]:
            msg = f"""
🔴 PHÂN KỲ GIẢM
⏱ {tf}
📈 {df['high'].iloc[h1]:.2f} → {df['high'].iloc[h2]:.2f}
"""
            bot.send_message(CHAT_ID, msg)


# =====================
# MAIN LOOP (ANTI CRASH)
# =====================
def run_bot():
    print("🚀 BOT STARTED 24/7")

    # test Telegram
    try:
        bot.send_message(CHAT_ID, "🔥 Bot Railway đã chạy 24/7 thành công")
    except Exception as e:
        print("Telegram error:", e)

    while True:
        try:
            for tf in timeframes:
                print(f"📊 Scanning {tf}")

                bars = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=200)
                df = pd.DataFrame(bars, columns=["ts","open","high","low","close","vol"])

                check_divergence(df, tf)

                time.sleep(1)

            print("⏳ Next cycle...\n")
            time.sleep(20)

        except Exception as e:
            print("❌ ERROR LOOP:", e)
            traceback.print_exc()
            time.sleep(5)


# =====================
# PROTECTION WRAPPER (QUAN TRỌNG)
# =====================
if __name__ == "__main__":
    while True:
        try:
            run_bot()
        except Exception as e:
            print("🔥 CRASH RECOVERED:", e)
            time.sleep(5)
