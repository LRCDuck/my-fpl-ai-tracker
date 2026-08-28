import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="AI FPL Mini-League Tracker", layout="wide")

# Custom Dark Mode styling to look like a premium analytics tool
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .card { background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; margin-bottom: 20px; }
    .title-header { text-align: center; color: #ffffff; font-weight: bold; margin-bottom: 10px; }
    .stButton>button { background-color: #238636; color: white; font-weight: bold; border-radius: 8px; width: 100%; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='title-header'>⚽ AI FPL Mini-League Scouting Hub</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e;'>Proxy Tunnel Mode • Smart-Caching • Direct Database Feed</p>", unsafe_allow_html=True)
st.markdown("---")

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header("⚙️ Server Data Sync")
league_id = st.sidebar.text_input("Enter FPL Mini-League ID:", value="1116047")
your_name = st.sidebar.text_input("Enter Your Name (To Highlight Your Team):", value="")

user_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# --- SMART CACHING STORAGE ENGINE WITH UNBLOCKING PROXY ---
@st.cache_data(ttl=86400)
def fetch_league_standings_cached(l_id):
    if not l_id:
        return "No League ID", pd.DataFrame(), "Please enter a valid Mini-League ID."
        
    try:
        # CRITICAL FIX: Tunneling the URL through the AllOrigins proxy to smash past cloud blocks
        target_fpl_url = f"https://premierleague.com{l_id}/standings/"
        proxy_url = f"https://allorigins.win{requests.utils.quote(target_fpl_url)}"
        
        response = requests.get(proxy_url, headers=user_headers, timeout=20)
        
        if response.status_code == 200:
            wrapper = response.json()
            data = json.loads(wrapper['contents']) # Parse the clean proxy bundle contents
            
            league_name = data['league']['name']
            raw_results = data['standings']['results']
            
            league_rows = []
            for m in raw_results:
                movement = "➖"
                if m['rank_sort'] < m['last_rank']: movement = "🔺"
                elif m['rank_sort'] > m['last_rank']: movement = "🔻"
                
                league_rows.append({
                    "Rank": m['rank'],
                    "Trend": movement,
                    "Manager Name": m['player_name'],
                    "Team Name": m['entry_name'],
                    "GW Score": m['event_total'],
                    "Total Points": m['total']
                })
            return league_name, pd.DataFrame(league_rows), None
        else:
            return "Server Offline", pd.DataFrame(), f"Proxy connection error (Code: {response.status_code})"
    except Exception as e:
        return "Server Error", pd.DataFrame(), "Proxy tunnel busy. Click manual pull to retry."

# --- MANUAL REFRESH BUTTON TRIGGER ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🔄 Manually Pull Fresh Data (Clear Memory Cache)"):
        st.cache_data.clear()
        st.toast("🧹 Local cache cleared! Fetching fresh live scores via proxy tunnel...")

league_name, full_standings_df, error_msg = fetch_league_standings_cached(league_id)

# --- MAIN INTERFACE DISPLAY ---
if error_msg:
    st.error(f"⚠️ {error_msg}")

st.markdown(f"<div class='card'><h3>🏆 Active League: {league_name}</h3>"
            f"<p>🔒 Loading from secure proxy tunnel memory cache. Zero server lag.</p></div>", unsafe_allow_html=True)

if not full_standings_df.empty:
    def highlight_user_row(row):
        if your_name and your_name.lower() in row['Manager Name'].lower():
            return ['background-color: #238636; color: white; font-weight: bold'] * len(row)
        return [''] * len(row)
    
    styled_df = full_standings_df.style.apply(highlight_user_row, axis=1)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    # AI Tactical Breakdown Panel
    st.markdown("---")
    st.subheader("🤖 AI Scouting Summary")
    leader_name = full_standings_df.iloc[0]['Manager Name']
    leader_points = full_standings_df.iloc[0]['Total Points']
    st.info(f"📊 **Scouting Report:** The mini-league is being led by **{leader_name}** with **{leader_points} points**. "
            f"Your proxy unblocker channel is active. Click the green button above any time during matches to update scores!")
else:
    st.warning("🔄 Awaiting proxy handshake. Enter your Mini-League ID inside the sidebar config panel.")
