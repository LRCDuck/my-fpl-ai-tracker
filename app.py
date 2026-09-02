import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="AI FPL Mini-League Scouting Hub",
    layout="wide"
)

# --------------------------------------------------
# STYLING
# --------------------------------------------------

st.markdown("""
<style>
.main {
    background-color: #0d1117;
}

.card {
    background-color: #161b22;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #30363d;
    margin-bottom: 15px;
}

.title-header {
    text-align: center;
    color: white;
    font-weight: bold;
}

.stButton > button {
    background-color: #238636;
    color: white;
    border-radius: 8px;
    font-weight: bold;
    width: 100%;
}

div[data-testid="metric-container"] {
    background-color: #161b22;
    border: 1px solid #30363d;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    "<h1 class='title-header'>⚽ AI FPL Mini-League Scouting Hub</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;color:#8b949e;'>League Analytics • Live Standings • AI Scouting Insights</p>",
    unsafe_allow_html=True
)

st.markdown("---")

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("⚙️ Settings")

league_id = st.sidebar.text_input(
    "Mini-League ID",
    value="1116047"
)

your_name = st.sidebar.text_input(
    "Your Name",
    value=""
)

# --------------------------------------------------
# FETCH DATA
# --------------------------------------------------

@st.cache_data(ttl=3600)
def fetch_league_data(l_id):

    try:

        url = f"https://fantasy.premierleague.com/api/leagues-classic/{l_id}/standings/"

        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        league_name = data["league"]["name"]

        standings = []

        for manager in data["standings"]["results"]:

            movement = "➖"

            if manager["rank_sort"] < manager["last_rank"]:
                movement = "🔺"
            elif manager["rank_sort"] > manager["last_rank"]:
                movement = "🔻"

            standings.append({
                "Rank": manager["rank"],
                "Trend": movement,
                "Manager Name": manager["player_name"],
                "Team Name": manager["entry_name"],
                "GW Score": manager["event_total"],
                "Total Points": manager["total"]
            })

        return league_name, pd.DataFrame(standings), None

    except Exception as e:
        return "Unknown League", pd.DataFrame(), str(e)

# --------------------------------------------------
# REFRESH BUTTON
# --------------------------------------------------

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🔄 Refresh Scores"):
        st.cache_data.clear()
        st.rerun()

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

league_name, standings_df, error = fetch_league_data(league_id)

if error:
    st.error(error)

# --------------------------------------------------
# LEAGUE CARD
# --------------------------------------------------

st.markdown(
    f"""
    <div class="card">
        <h3>🏆 {league_name}</h3>
        <p>Live data powered by the Fantasy Premier League API.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# MAIN CONTENT
# --------------------------------------------------

if not standings_df.empty:

    # --------------------------------------------------
    # PODIUM
    # --------------------------------------------------

    st.subheader("🏆 League Leaders")

    podium = standings_df.head(3)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "🥇 First",
            podium.iloc[0]["Manager Name"],
            f"{podium.iloc[0]['Total Points']} pts"
        )

    with c2:
        if len(podium) > 1:
            st.metric(
                "🥈 Second",
                podium.iloc[1]["Manager Name"],
                f"{podium.iloc[1]['Total Points']} pts"
            )

    with c3:
        if len(podium) > 2:
            st.metric(
                "🥉 Third",
                podium.iloc[2]["Manager Name"],
                f"{podium.iloc[2]['Total Points']} pts"
            )

    # --------------------------------------------------
    # USER STATS
    # --------------------------------------------------

    if your_name:

        my_team = standings_df[
            standings_df["Manager Name"].str.contains(
                your_name,
                case=False,
                na=False
            )
        ]

        if not my_team.empty:

            leader_points = standings_df.iloc[0]["Total Points"]

            your_points = my_team.iloc[0]["Total Points"]

            gap = leader_points - your_points

            rank = my_team.iloc[0]["Rank"]

            c1, c2 = st.columns(2)

            with c1:
                st.metric(
                    "📍 Your Position",
                    rank
                )

            with c2:
                st.metric(
                    "🎯 Gap To 1st",
                    f"{gap} pts"
                )

    st.markdown("---")

    # --------------------------------------------------
    # TABLE HIGHLIGHTING
    # --------------------------------------------------

    def highlight_user_row(row):

        if (
            your_name
            and your_name.lower() in row["Manager Name"].lower()
        ):
            return [
                "background-color:#238636;color:white;font-weight:bold;"
            ] * len(row)

        return [""] * len(row)

    styled_df = standings_df.style.apply(
        highlight_user_row,
        axis=1
    )

    st.subheader("📋 Full Standings")

    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------
    # CHART
    # --------------------------------------------------

    st.markdown("---")

    st.subheader("📈 League Points Chart")

    chart_df = standings_df.set_index(
        "Manager Name"
    )["Total Points"]

    st.bar_chart(chart_df)

    # --------------------------------------------------
    # TOP GW SCORES
    # --------------------------------------------------

    st.markdown("---")

    st.subheader("🔥 Highest Gameweek Scores")

    top_gw = standings_df.sort_values(
        "GW Score",
        ascending=False
    ).head(5)

    st.dataframe(
        top_gw,
        hide_index=True,
        use_container_width=True
    )

    # --------------------------------------------------
    # RISERS & FALLERS
    # --------------------------------------------------

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🚀 Risers")

        risers = standings_df[
            standings_df["Trend"] == "🔺"
        ]

        if risers.empty:
            st.info("No risers this week.")
        else:
            st.dataframe(
                risers,
                hide_index=True,
                use_container_width=True
            )

    with col2:

        st.subheader("📉 Fallers")

        fallers = standings_df[
            standings_df["Trend"] == "🔻"
        ]

        if fallers.empty:
            st.info("No fallers this week.")
        else:
            st.dataframe(
                fallers,
                hide_index=True,
                use_container_width=True
            )

    # --------------------------------------------------
    # AI INSIGHTS
    # --------------------------------------------------

    st.markdown("---")

    st.subheader("🤖 AI Scouting Report")

    leader = standings_df.iloc[0]

    bottom = standings_df.iloc[-1]

    gap = (
        leader["Total Points"]
        - bottom["Total Points"]
    )

    st.info(
        f"""
🏆 **League Leader:** {leader['Manager Name']} ({leader['Total Points']} pts)

🔥 **Best Current GW Score:** {standings_df['GW Score'].max()} pts

📈 **League Spread:** {gap} pts from first to last place

⚠️ **Bottom Manager:** {bottom['Manager Name']}

📊 The league remains competitive, with movement still possible as additional gameweek points arrive.
"""
    )

else:

    st.warning(
        "No standings available. Check your league ID and try again."
    )
