import streamlit as st
from signal_engine import generate_signal

st.title("Quotex Signal App")
st.write("এটি একটি ডেমো সিগন্যাল জেনারেটর টুল (শুধুমাত্র শেখার উদ্দেশ্যে)।")

if st.button("Generate Signal"):
    signal = generate_signal()
    st.success(f"আজকের সিগন্যাল: {signal}")
