import streamlit as st
import random

st.title("Quotex Signal App")
st.write("এটি একটি ডেমো সিগন্যাল জেনারেটর টুল (শুধুমাত্র শেখার উদ্দেশ্যে)।")

# মার্কেট সিলেক্ট করার অপশন
market = st.selectbox(
    "মার্কেট নির্বাচন করুন:",
    ["EUR/USD", "GBP/JPY", "EUR/CAD", "OTC", "Gold", "Crypto"]
)

# সিগন্যাল জেনারেটর
if st.button("Generate Signal"):
    signal = random.choice(["Buy", "Sell"])
    accuracy = random.randint(70, 95)  # ডেমো Accuracy %
    st.success(f"মার্কেট: {market} | সিগন্যাল: {signal} | Accuracy: {accuracy}%")
