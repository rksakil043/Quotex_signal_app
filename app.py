
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

st.set_page_config(page_title="Quotex Signal App (Advanced)", layout="wide")
st.title("📊 Quotex Signal App — Advanced (EMA + RSI + MACD)")
st.caption("শুধুমাত্র শিক্ষা/রিসার্চের উদ্দেশ্যে। কোনো গ্যারান্টি নেই।")

def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()

def rsi(series, period=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    gain = up.rolling(period).mean()
    loss = down.rolling(period).mean()
    rs = gain / (loss + 1e-12)
    return 100 - (100/(1+rs))

def macd(series, fast=12, slow=26, signal=9):
    macd_line = ema(series, fast) - ema(series, slow)
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def build_signals(df):
    d = df.copy()
    d["EMA20"] = ema(d["Close"], 20)
    d["EMA50"] = ema(d["Close"], 50)
    d["RSI14"] = rsi(d["Close"], 14)
    macd_line, sig_line, hist = macd(d["Close"], 12, 26, 9)
    d["MACD"] = macd_line
    d["MACDsig"] = sig_line

    cond_buy = (d["EMA20"] > d["EMA50"]) & (d["MACD"] > d["MACDsig"]) & (d["RSI14"].between(40, 70))
    cond_sell = (d["EMA20"] < d["EMA50"]) & (d["MACD"] < d["MACDsig"]) & (d["RSI14"].between(30, 60))

    d["signal"] = "HOLD"
    d.loc[cond_buy, "signal"] = "BUY"
    d.loc[cond_sell, "signal"] = "SELL"

    d["Close_fwd"] = d["Close"].shift(-1)
    d["result"] = "SKIP"
    d.loc[d["signal"] == "BUY", "result"] = np.where(d["Close_fwd"] > d["Close"], "WIN", "LOSS")
    d.loc[d["signal"] == "SELL", "result"] = np.where(d["Close_fwd"] < d["Close"], "WIN", "LOSS")
    return d

def metrics(bt):
    traded = bt["signal"].isin(["BUY","SELL"])
    total = int(traded.sum())
    wins = int((bt.loc[traded, "result"] == "WIN").sum())
    losses = int((bt.loc[traded, "result"] == "LOSS").sum())
    winrate = round(100 * (wins/total), 2) if total>0 else 0.0
    return {"trades": total, "wins": wins, "losses": losses, "winrate": winrate}

markets = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "EUR/JPY": "EURJPY=X",
    "Gold (Futures)": "GC=F",
    "Silver (Futures)": "SI=F",
    "Bitcoin (USD)": "BTC-USD",
    "Ethereum (USD)": "ETH-USD"
}
st.sidebar.header("Settings")
choice = st.sidebar.selectbox("মার্কেট নির্বাচন করুন:", list(markets.keys()), index=0)
interval = st.sidebar.selectbox("টাইমফ্রেম", ["1m","5m","15m","30m","60m","1d"], index=2)
period_map = {"1m":"1d","5m":"5d","15m":"5d","30m":"1mo","60m":"3mo","1d":"6mo"}
period = period_map[interval]

ticker = markets[choice]
st.write(f"**টিকার:** `{ticker}`  |  **টাইমফ্রেম:** `{interval}`  |  **পিরিয়ড:** `{period}`")

data = yf.download(ticker, period=period, interval=interval)
if data.empty:
    st.error("ডাটা পাওয়া যায়নি। একটু পর চেষ্টা করুন বা অন্য টাইমফ্রেম বেছে নিন।")
else:
    bt = build_signals(data)
    m = metrics(bt)
    last_sig = bt.dropna().iloc[-1]["signal"]
    last_close = float(bt.dropna().iloc[-1]["Close"])

    st.success(f"মার্কেট: {choice}  |  সর্বশেষ সিগন্যাল: **{last_sig}**  |  লাস্ট প্রাইস: {last_close:.5f}")
    st.info(f"Backtest (simple 1-bar ahead): Trades: {m['trades']} | Wins: {m['wins']} | Losses: {m['losses']} | Winrate: {m['winrate']}%")

    st.subheader("Recent Signals")
    st.dataframe(bt[["Close","EMA20","EMA50","RSI14","MACD","MACDsig","signal","result"]].tail(30), use_container_width=True)

    fig1 = plt.figure(figsize=(10,4))
    plt.plot(bt.index, bt["Close"], label="Close")
    plt.plot(bt.index, bt["EMA20"], label="EMA20")
    plt.plot(bt.index, bt["EMA50"], label="EMA50")
    plt.legend(); plt.tight_layout()
    st.pyplot(fig1)

    fig2 = plt.figure(figsize=(10,2.8))
    plt.plot(bt.index, bt["RSI14"], label="RSI14")
    plt.axhline(70, linestyle="--"); plt.axhline(30, linestyle="--")
    plt.legend(); plt.tight_layout()
    st.pyplot(fig2)
