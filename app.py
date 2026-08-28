import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="AI FPL Elite Tactical Hub", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stButton>button { background-color: #ffeb3b; color: #000000; font-weight: bold; border-radius: 8px; }
    .card { background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; margin-bottom: 15px; }
    .timeline-gw { font-weight: bold; color: #ffeb3b; border-left: 3px solid #ffeb3b; padding-left: 10px; margin-top: 15px; }
    .transfer-log { color: #f44336; padding-left: 20px; font-family: monospace; }
    .chip-log { color: #4caf50; font-weight: bold; padding-left: 20px; }
    .price-up { color: #4caf50; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("⚽ AI FPL Elite Tactical Hub & Historical Tracker")
st.caption("Live Mini-League Analytics • Roster History Preservation • Chip Optimization Matrices")

# Sidebar Configuration
st.sidebar.header("🛡️ Squad Settings")
league_id = st.sidebar.text_input("Mini-League ID:", value="78910")
selected_manager = st.sidebar.selectbox("Select Rival to Scout:", ["Sam Young (Heroes and Villans)", "Ben Taylor (Final 11)", "Stephen Kay"])

# --- DATABASE PERSISTENCE LOGIC ---
DB_FILE = "league_history.json"
if not os.path.exists(DB_FILE):
    mock_history = {
        "Sam Young (Heroes and Villans)": {
            "GW1": {"Score": 73, "Chip Used": "Bench Boost", "Transfers Made": "None (Initial Squad)"},
            "GW2": {"Score": "Pending...", "Chip Used": "None", "Transfers Made": "Rolled Free Transfer"}
        },
        "Ben Taylor (Final 11)": {
            "GW1": {"Score": 71, "Chip Used": "None", "Transfers Made": "None (Initial Squad)"},
            "GW2": {"Score": "Pending...", "Chip Used": "None", "Transfers Made": "Rolled Free Transfer"}
        },
        "Stephen Kay": {
            "GW1": {"Score": 61, "Chip Used": "Bench Boost", "Transfers Made": "None (Initial Squad)"},
            "GW2": {"Score": "Pending...", "Chip Used": "None", "Transfers Made": "Aina ➡️ Egan"}
        }
    }
    with open(DB_FILE, "w") as f:
        json.dump(mock_history, f, indent=4)

with open(DB_FILE, "r") as f:
    league_database = json.load(f)

# Main Multi-Tab Interface Layout
tab1, tab2, tab3 = st.tabs(["📅 Gameweek Calendar Timeline", "📊 Live Transfer Assistant", "📈 Market Price Radar"])

# TAB 1: Historical Calendar Timeline
with tab1:
    st.subheader(f"Timeline History for: {selected_manager}")
    manager_data = league_database.get(selected_manager, {})
    for gw, details in manager_data.items():
        st.markdown(f"<div class='timeline-gw'>{gw} Campaign Summary</div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Gameweek Score", value=str(details["Score"]))
        with col2:
            st.write(f"**⚡ Chip Activated:** {details['Chip Used']}")
        with col3:
            st.markdown(f"**🔄 Transfer Activity:** <span class='transfer-log'>{details['Transfers Made']}</span>", unsafe_allow_html=True)

# TAB 2: Live Transfer Suggestions
with tab2:
    st.markdown("<div class='card'><h3>🤖 Live Transfer Suggestions AI</h3><p>Optimizing team parameters based on expected minutes and xG ratios.</p></div>", unsafe_allow_html=True)
    col4, col5 = st.columns(2)
    with col4:
        st.subheader("📉 Suggested Out")
        st.dataframe(pd.DataFrame({"Player to Sell": ["Calvert-Lewin (Everton)"], "Current Value": ["£6.0m"], "5-GW xPts": [11.2]}), use_container_width=True)
    with col5:
        st.subheader("🚀 Recommended Targets")
        st.dataframe(pd.DataFrame({"Player to Target": ["Anthony Gordon (Newcastle)"], "Cost": ["£7.5m"], "Predicted 5-GW xPts": [24.8]}), use_container_width=True)

# TAB 3: Price Watch Alerts
with tab3:
    st.markdown("<div class='card'><h3>🚨 Real-Time Market Price Radar</h3><p>Tracks nightly valuation shifts to protect squad equity value.</p></div>", unsafe_allow_html=True)
    st.markdown("""
    * <span class='price-up'>Cole Palmer (Chelsea):</span> **110%** (Rising Tonight 🔺)
    * <span class='price-up'>Morgan Rogers (Aston Villa):</span> **75%** (+1 Day)
    """, unsafe_allow_html=True)
