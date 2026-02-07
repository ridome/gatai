import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import auth
from xueqiu_api import XueqiuAPI, format_post

# Page Configuration
st.set_page_config(
    page_title="Xueqiu Market Dashboard",
    page_icon="📈",
    layout="wide"
)

# Initialize API
if 'api' not in st.session_state:
    st.session_state.api = XueqiuAPI()

api = st.session_state.api

def render_feed(feed_type, symbol=None):
    raw_posts = []
    if feed_type == "hot":
        raw_posts = api.get_hot_discussions()
    elif feed_type == "following":
        raw_posts = api.get_following_feed()
    elif feed_type == "stock" and symbol:
        raw_posts = api.get_stock_comments(symbol)

    if not raw_posts:
        st.info("No posts found or API error.")
        return

    for post in raw_posts:
        # Handle different response structures
        if isinstance(post, dict):
            if 'data' in post:
                p = post['data']
            else:
                p = post
        else:
            p = {}

        formatted = format_post(p)

        with st.container():
            col1, col2 = st.columns([1, 10])
            with col1:
                # Placeholder for avatar if available
                st.write("👤")
            with col2:
                # Time
                ts = formatted.get('created_at', 0)
                time_str = datetime.fromtimestamp(ts/1000).strftime('%Y-%m-%d %H:%M') if ts else ""
                st.markdown(f"**{formatted.get('user_name', 'Unknown')}** · *{time_str}*")

                if formatted.get('title'):
                    st.markdown(f"### {formatted['title']}")

                if formatted.get('text'):
                    st.markdown(formatted['text'], unsafe_allow_html=True)

                if formatted.get('retweeted_status'):
                    rt = formatted['retweeted_status']
                    rt_user = rt.get('user', {}).get('screen_name', 'Unknown')
                    rt_text = rt.get('text', '')
                    st.info(f"Retweeted {rt_user}: {rt_text}")

            st.divider()

# --- Sidebar ---
st.sidebar.title("Controls")

# Login Section
st.sidebar.header("Authentication")
if auth.is_logged_in():
    st.sidebar.success("✅ Logged In")
    if st.sidebar.button("Refresh Session"):
        auth.login_with_browser()
        api.refresh_cookies()
        st.rerun()
else:
    st.sidebar.warning("⚠️ Not Logged In")
    if st.sidebar.button("Login to Xueqiu"):
        auth.login_with_browser()
        api.refresh_cookies()
        st.rerun()

# Symbol Input
st.sidebar.header("Market Data")

# Initialize symbol in session state
if 'symbol' not in st.session_state:
    st.session_state.symbol = "SH000001"

# Function to update symbol from watchlist
def update_symbol_from_list():
    selected = st.session_state.watchlist_select
    if selected and selected != "Select...":
        # Extract symbol (assumes format "SYMBOL Name")
        st.session_state.symbol = selected.split(" ")[0]

# Watchlist Selection
if auth.is_logged_in():
    try:
        watchlist = api.get_watchlist()
        if watchlist:
            options = ["Select..."] + [f"{item['symbol']} {item.get('name', '')}" for item in watchlist]
            st.sidebar.selectbox("Your Watchlist", options, key="watchlist_select", on_change=update_symbol_from_list)
    except Exception as e:
        st.sidebar.error(f"Error loading watchlist: {e}")

# Manual Input (bind to session state)
symbol_input = st.sidebar.text_input("Stock Symbol", key="symbol", help="e.g., SH000001, SZ000001, SH600519").upper()

# Period Selection for Chart
period_map = {
    "Day": "day",
    "Week": "week",
    "Month": "month",
    "60 Min": "60m",
    "30 Min": "30m",
    "15 Min": "15m",
    "5 Min": "5m",
    "1 Min": "1m"
}
selected_period_label = st.sidebar.selectbox("Chart Period", options=list(period_map.keys()), index=0)
selected_period = period_map[selected_period_label]

# --- Main Content ---
st.title("Xueqiu Market Dashboard (雪球行情看板)")

tab1, tab2 = st.tabs(["📈 Market Data", "💬 Discussions"])

# --- Tab 1: Market Data ---
with tab1:
    if not auth.is_logged_in():
        st.info("Please log in to view real-time market data.")
    else:
        # 1. Real-time Quote
        try:
            quote = api.get_quote(symbol_input)
            if quote:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Price", quote.get('current'), quote.get('chg'))
                with col2:
                    st.metric("Percent", f"{quote.get('percent')}%")
                with col3:
                    st.metric("High", quote.get('high'))
                with col4:
                    st.metric("Low", quote.get('low'))

                ts = quote.get('timestamp', 0)
                st.caption(f"Last Updated: {datetime.fromtimestamp(ts/1000).strftime('%Y-%m-%d %H:%M:%S') if ts else 'Unknown'}")
            else:
                st.error(f"Could not fetch quote for {symbol_input}. Check the symbol or your login status.")
        except Exception as e:
            st.error(f"Error fetching quote: {e}")

        # 2. K-Line Chart
        st.subheader(f"{symbol_input} - {selected_period_label} K-Line")
        try:
            kline_data = api.get_kline(symbol_input, period=selected_period)

            if kline_data and kline_data.get('items'):
                # Check column length vs item length
                cols = kline_data['columns']
                items = kline_data['items']

                if items and len(items[0]) == len(cols):
                    df = pd.DataFrame(items, columns=cols)
                    # Convert timestamp
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

                    fig = go.Figure(data=[go.Candlestick(
                        x=df['timestamp'],
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close']
                    )])

                    fig.update_layout(xaxis_rangeslider_visible=False, height=600)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Data format mismatch from API.")
            else:
                st.warning("No K-line data available.")
        except Exception as e:
            st.error(f"Error plotting chart: {e}")

# --- Tab 2: Discussions ---
with tab2:
    if not auth.is_logged_in():
        st.info("Please log in to view discussions.")
    else:
        feed_tab1, feed_tab2, feed_tab3 = st.tabs(["🔥 Hot / Recommended", "👀 Following", f"📊 {symbol_input} Discussion"])

        with feed_tab1:
            if st.button("Refresh Hot Feed"):
                st.rerun()
            render_feed("hot")

        with feed_tab2:
            if st.button("Refresh Following Feed"):
                st.rerun()
            render_feed("following")

        with feed_tab3:
            if st.button(f"Refresh {symbol_input} Feed"):
                st.rerun()
            render_feed("stock", symbol=symbol_input)
