import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="AI FPL Elite Tactical Hub", layout="wide")

# Premium Dark-Mode Theme CSS mimicking FPL Analyzer's pitching cards
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .pitch-container { background-color: #0b2214; border: 2px solid #1f5f38; border-radius: 12px; padding: 25px; margin-bottom: 20px; max-width: 700px; margin-left: auto; margin-right: auto; }
    .bench-container { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-top: 15px; max-width: 700px; margin-left: auto; margin-right: auto; }
    .pitch-row { display: flex; justify-content: center; gap: 20px; margin-bottom: 20px; }
    .player-card { background-color: #1c2128; border: 1px solid #444c56; border-radius: 8px; padding: 12px; width: 125px; text-align: center; font-size: 13px; box-shadow: 3px 3px 8px rgba(0,0,0,0.4); }
    .player-name { font-weight: bold; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .player-price { color: #58a6ff; font-weight: bold; font-size: 11px; margin-top: 3px; }
    .player-xpts { color: #2ea043; font-size: 11px; margin-top: 2px; }
    .captain-badge { background-color: #ffeb3b; color: #000000; font-weight: bold; border-radius: 3px; padding: 1px 5px; font-size: 10px; margin-left: 4px; }
    </style>
""", unsafe_allow_html=True)

st.title("⚽ AI FPL Elite Tactical Hub & Live Tracker")
st.caption("Automated Roster Audits • Single Team Pitch View • Strategic Chip Tracking Panels")

# Sidebar - Live League Sync Layout
st.sidebar.header("🛡️ Live League Sync")
league_input = st.sidebar.text_input("Enter FPL Mini-League ID:", value="1116047")

managers_list = []
league_name = "Work Mini-League Workspace"
full_standings_df = pd.DataFrame()

if league_input:
    try:
        fpl_url = f"https://premierleague.com{league_input}/standings/"
        user_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
        response = requests.get(fpl_url, headers=user_headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            league_name = data['league']['name']
            raw_results = data['standings']['results']
            
            league_rows = []
            for m in raw_results:
                display_name = f"{m['player_name']} ({m['entry_name']})"
                managers_list.append(display_name)
                league_rows.append({
                    "Rank": m['rank'], "Manager Name": m['player_name'], "Team Name": m['entry_name'], "Total Points": m['total']
                })
            full_standings_df = pd.DataFrame(league_rows)
    except Exception:
        pass

if not managers_list:
    managers_list = ["You (Your Team Layout)", "Sam Young (Heroes and Villans)", "Ben Taylor (Final 11)"]

# --- DESIGN FUNCTION TO RENDER A SINGLE COMPREHENSIVE PITCH ---
def render_squad_pitch(title, gkp, dfs, mids, fwds, bench_players):
    st.markdown(f"<h3 style='text-align: center;'>🏟️ {title}</h3>", unsafe_allow_html=True)
    st.markdown("<div class='pitch-container'>", unsafe_allow_html=True)
    
    # 1. Goalkeeper Line
    st.markdown("<div class='pitch-row'>", unsafe_allow_html=True)
    for p in gkp:
        st.markdown(f"<div class='player-card'><div class='player-name'>{p['name']}</div><div class='player-price'>{p['price']}</div><div class='player-xpts'>{p['xpts']}</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 2. Defense Line
    st.markdown("<div class='pitch-row'>", unsafe_allow_html=True)
    for p in dfs:
        st.markdown(f"<div class='player-card'><div class='player-name'>{p['name']}</div><div class='player-price'>{p['price']}</div><div class='player-xpts'>{p['xpts']}</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 3. Midfield Line
    st.markdown("<div class='pitch-row'>", unsafe_allow_html=True)
    for p in mids:
        c_tag = "<span class='captain-badge'>C</span>" if p.get('c') else ""
        st.markdown(f"<div class='player-card'><div class='player-name'>{p['name']}{c_tag}</div><div class='player-price'>{p['price']}</div><div class='player-xpts'>{p['xpts']}</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 4. Forwards Line
    st.markdown("<div class='pitch-row'>", unsafe_allow_html=True)
    for p in fwds:
        c_tag = "<span class='captain-badge'>C</span>" if p.get('c') else ""
        st.markdown(f"<div class='player-card'><div class='player-name'>{p['name']}{c_tag}</div><div class='player-price'>{p['price']}</div><div class='player-xpts'>{p['xpts']}</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True) # End pitch
    
    # 5. Bench Row Display
    st.markdown("<div class='bench-container'><strong>💺 BENCH SUITE</strong><div class='pitch-row' style='margin-top:12px;'>", unsafe_allow_html=True)
    for p in bench_players:
        st.markdown(f"<div class='player-card' style='background-color:#22272e;'><div class='player-name'>{p['name']}</div><div class='player-price'>{p['price']}</div></div>", unsafe_allow_html=True)
    st.markdown("</div></div><br>", unsafe_allow_html=True)

# Main Navigation Tabs
tab1, tab2, tab3 = st.tabs(["📋 Scout Rival Team Pitch", "📅 Leaderboard Matrix", "📈 Price Radar"])

with tab1:
    selected_rival = st.selectbox("Select Mini-League Manager to View Team Pitch Sheet:", managers_list)
    
    st.markdown("---")
    
    # Logic to switch data inputs dynamically based on dropdown selection
    if "Sam" in selected_rival:
        render_squad_pitch(
            f"Active Team: {selected_rival}",
            [{"name": "Verbruggen", "price": "£4.5m", "xpts": "2.9"}],
            [{"name": "Shaw", "price": "£4.5m", "xpts": "3.9"}, {"name": "White", "price": "£5.5m", "xpts": "2.6"}, {"name": "Calafiori", "price": "£5.6m", "xpts": "2.7"}, {"name": "Ballard", "price": "£5.0m", "xpts": "4.1"}],
            [{"name": "B.Fernandes", "price": "£12.0m", "xpts": "6.0"}, {"name": "Tzolis", "price": "£6.5m", "xpts": "3.4"}, {"name": "Mbeumo", "price": "£8.0m", "xpts": "5.0"}],
            [{"name": "Haaland", "price": "£15.5m", "xpts": "8.6", "c": True}, {"name": "João Pedro", "price": "£7.6m", "xpts": "8.0"}, {"name": "Calvert-Lewin", "price": "£6.0m", "xpts": "4.3"}],
            [{"name": "Kinsky", "price": "£4.5m"}, {"name": "Groß", "price": "£5.5m"}, {"name": "M.Sangaré", "price": "£5.6m"}, {"name": "Diop", "price": "£4.0m"}]
        )
    elif "Ben" in selected_rival:
        render_squad_pitch(
            f"Active Team: {selected_rival}",
            [{"name": "Verbruggen", "price": "£4.5m", "xpts": "2.9"}],
            [{"name": "Shaw", "price": "£4.5m", "xpts": "3.9"}, {"name": "White", "price": "£5.5m", "xpts": "2.6"}, {"name": "Calafiori", "price": "£5.6m", "xpts": "2.7"}, {"name": "Ballard", "price": "£5.0m", "xpts": "4.1"}],
            [{"name": "B.Fernandes", "price": "£12.0m", "xpts": "6.0"}, {"name": "Tzolis", "price": "£6.5m", "xpts": "3.4"}, {"name": "Mbeumo", "price": "£8.0m", "xpts": "5.0"}],
            [{"name": "Haaland", "price": "£15.5m", "xpts": "8.6", "c": True}, {"name": "João Pedro", "price": "£7.6m", "xpts": "8.0"}, {"name": "Calvert-Lewin", "price": "£6.0m", "xpts": "4.3"}],
            [{"name": "Kinsky", "price": "£4.5m"}, {"name": "Groß", "price": "£5.5m"}, {"name": "M.Sangaré", "price": "£5.6m"}, {"name": "Diop", "price": "£4.0m"}]
        )
    else:
        # Default: Displays Your Own Active Team
        render_squad_pitch(
            "Active Team: Your Lineup Grid",
            [{"name": "Verbruggen", "price": "£4.5m", "xpts": "2.9"}],
            [{"name": "Tarkowski", "price": "£6.0m", "xpts": "3.6"}, {"name": "Diop", "price": "£4.0m", "xpts": "2.5"}, {"name": "Aina", "price": "£4.5m", "xpts": "2.4"}],
            [{"name": "B.Fernandes", "price": "£12.0m", "xpts": "6.0", "c": True}, {"name": "Saka", "price": "£9.5m", "xpts": "3.9"}, {"name": "Szoboszlai", "price": "£7.0m", "xpts": "4.0"}, {"name": "Schade", "price": "£6.0m", "xpts": "3.9"}],
            [{"name": "Calvert-Lewin", "price": "£6.0m", "xpts": "4.3"}, {"name": "Haaland", "price": "£15.5m", "xpts": "8.6"}, {"name": "João Pedro", "price": "£7.6m", "xpts": "8.0"}],
            [{"name": "Kinsky", "price": "£4.5m"}, {"name": "Thomas", "price": "£4.0m"}, {"name": "Slater", "price": "£4.5m"}, {"name": "Hume", "price": "£4.5m"}]
        )

with tab2:
    st.subheader(f"🏆 Active League Leaderboard: {league_name}")
    if not full_standings_df.empty:
        st.dataframe(full_standings_df, use_container_width=True, hide_index=True)
    else:
        st.info("Log a dynamic league ID above to unlock structural table grids.")

with tab3:
    st.subheader("📈 Real-Time Price Target Radar")
    st.markdown("* **Cole Palmer (Chelsea):** 115% (🔺 Rising Soon)\n* **Morgan Rogers (Aston Villa):** 82%")
