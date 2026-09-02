import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="AI FPL Mini-League Tracker",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------
st.markdown("""
<style>
.main {
    background-color: #0d1117;
    color: #c9d1d9;
}

.card {
    background-color: #161b22;
    padding: 20px;
    border-radius: 10px;
    border: 1px solid #30363d;
    margin-bottom: 20px;
}

.title-header {
    text-align: center;
    color: #ffffff;
    font-weight: bold;
    margin-bottom: 10px;
}

.stButton > button {
    background-color: #238636;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------
st.markdown(
    "<h1 class='title-header'>⚽ AI FPL Mini-League Scouting Hub</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;color:#8b949e;'>Elite League Tracking • Smart Caching • Live FPL Data</p>",
    unsafe_allow_html=True
)

st.markdown("---")

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.header("⚙️ League Settings")

league_id = st.sidebar.text_input(
    "Enter FPL Mini-League ID:",
    value="1116047"
)

your_name = st.sidebar.text_input(
    "Enter Your Name (Optional Highlight):",
    value=""
)

# --------------------------------------------------
# HEADERS
# --------------------------------------------------
user_headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Referer": "https://fantasy.premierleague.com/",
    "Origin": "https://fantasy.premierleague.com"
}

# --------------------------------------------------
# DATA FETCH
# --------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_league_standings_direct(l_id):

    if not l_id:
        return "No League Selected", pd.DataFrame(), "Please enter a Mini-League ID."

    try:
        fpl_url = (
            f"https://fantasy.premierleague.com/api/"
            f"leagues-classic/{l_id}/standings/"
        )

        response = requests.get(
            fpl_url,
            headers=user_headers,
            timeout=15
        )

        if response.status_code == 200:

            data = response.json()

            league_name = data["league"]["name"]
            raw_results = data["standings"]["results"]

            league_rows = []

            for manager in raw_results:

                movement = "➖"

                if manager["rank_sort"] < manager["last_rank"]:
                    movement = "🔺"
                elif manager["rank_sort"] > manager["last_rank"]:
                    movement = "🔻"

                league_rows.append({
                    "Rank": manager["rank"],
                    "Trend": movement,
                    "Manager Name": manager["player_name"],
                    "Team Name": manager["entry_name"],
                    "GW Score": manager["event_total"],
                    "Total Points": manager["total"]
                })

            return league_name, pd.DataFrame(league_rows), None

        return (
            "Server Error",
            pd.DataFrame(),
            f"FPL returned status code {response.status_code}."
        )

    except Exception as e:

        return (
            "Connection Failed",
            pd.DataFrame(),
            str(e)
        )

# --------------------------------------------------
# REFRESH BUTTON
# --------------------------------------------------
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🔄 Refresh Live Scores"):
        st.cache_data.clear()
        st.toast("Cache cleared. Pulling fresh data...")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
league_name, standings_df, error_msg = fetch_league_standings_direct(
    league_id
)

# --------------------------------------------------
# ERROR MESSAGE
# --------------------------------------------------
if error_msg:
    st.warning(error_msg)

# --------------------------------------------------
# LEAGUE CARD
# --------------------------------------------------
st.markdown(
    f"""
    <div class="card">
        <h3>🏆 Active League: {league_name}</h3>
        <p>
            Live standings sourced directly from the Fantasy Premier League API.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# TABLE DISPLAY
# --------------------------------------------------
if not standings_df.empty:

    def highlight_user_row(row):

        if (
            your_name
            and your_name.lower()
            in row["Manager Name"].lower()
        ):
            return [
                "background-color:#238636;color:white;font-weight:bold;"
            ] * len(row)

        return [""] * len(row)

    styled_df = standings_df.style.apply(
        highlight_user_row,
        axis=1
    )

    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------
    # AI SUMMARY
    # --------------------------------------------------
    st.markdown("---")
    st.subheader("🤖 AI Scouting Summary")

    leader_name = standings_df.iloc[0]["Manager Name"]
    leader_points = standings_df.iloc[0]["Total Points"]

    st.info(
        f"""
        📊 **Current League Leader:** **{leader_name}**
        
        🏆 Total Points: **{leader_points}**
        
        The live league table is updating from the official
        Fantasy Premier League API and your tracking dashboard
        is fully operational.
        """
    )

else:
    st.warning(
        "No standings available. Check your Mini-League ID and try again."
    )
