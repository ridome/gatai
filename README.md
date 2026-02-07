# Xueqiu Market Dashboard (雪球行情看板)

A local web dashboard to view China A-share market data and Xueqiu discussions, featuring a simulated browser login to bypass captcha verification.

## Features

- **Simulated Login:** Uses Playwright to launch a real browser for secure QR code login.
- **Market Data:** View Real-time quotes and Interactive K-Line charts (Candlestick) for A-shares.
- **Discussions:** Read "Trending", "Following", and "Stock Specific" posts from Xueqiu.
- **Persistent Session:** Saves cookies locally so you don't have to log in every time.

## Prerequisites

- Python 3.8+
- Chrome/Chromium browser (managed by Playwright)

## Installation

1.  **Clone the repository or download the files.**

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install Playwright browsers:**
    ```bash
    playwright install
    ```

## Usage

1.  **Run the dashboard:**
    ```bash
    streamlit run dashboard.py
    ```

2.  **Login:**
    - On the sidebar, click the **"Login to Xueqiu"** button.
    - A browser window will pop up opening `xueqiu.com`.
    - **Manually log in** (e.g., scan the QR code with your Xueqiu app).
    - Once logged in, the browser window will close automatically, and the dashboard will refresh.

3.  **Browse Data:**
    - Enter a stock symbol (e.g., `SH000001` for SSE Index, `SZ000001` for Ping An Bank) in the sidebar.
    - Switch tabs to view Market Data or Discussions.

## Note

- The tool saves your session cookies to `xueqiu_cookies.json` in the local directory. Keep this file safe.
- If data stops loading, your session might have expired. Simply click "Login" again to refresh your session.
