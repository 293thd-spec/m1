
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
bot.send_message(CHAT_ID, "🔥 Bot Railway đã chạy OK")

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

    # ===== BULLISH =====
    if len(swing_lows) >= 2:
        l1, l2 = swing_lows[-2], swing_lows[-1]

        if df['low'].iloc[l2] < df['low'].iloc[l1] and macd_line.iloc[l2] > macd_line.iloc[l1]:
            msg = f"🟢 BULLISH DIVERGENCE {tf}\nPrice: {df['low'].iloc[l1]} → {df['low'].iloc[l2]}"
            bot.send_message(CHAT_ID, msg)

    # ===== BEARISH =====
    if len(swing_highs) >= 2:
        h1, h2 = swing_highs[-2], swing_highs[-1]

        if df['high'].iloc[h2] > df['high'].iloc[h1] and macd_line.iloc[h2] < macd_line.iloc[h1]:
            msg = f"🔴 BEARISH DIVERGENCE {tf}\nPrice: {df['high'].iloc[h1]} → {df['high'].iloc[h2]}"
            bot.send_message(CHAT_ID, msg)


# =====================
# MAIN LOOP
# =====================
def run():
    print("Bot started...")

    while True:
        try:
            for tf in timeframes:
                bars = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=200)
                df = pd.DataFrame(bars, columns=['ts','open','high','low','close','vol'])

                check_divergence(df, tf)
                time.sleep(1)

            time.sleep(30)

        except Exception as e:
            print("Error:", e)
            time.sleep(10)


run()
