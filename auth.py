import json
import os
import time
from playwright.sync_api import sync_playwright

COOKIES_FILE = "xueqiu_cookies.json"

def login_with_browser():
    """
    Launches a browser window for the user to log in to Xueqiu.
    Waits for the 'xq_a_token' cookie to appear.
    """
    print("Launching browser for login...")
    with sync_playwright() as p:
        browser = None
        try:
            # Launch browser in headful mode so user can see it
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            page = context.new_page()

            page.goto("https://xueqiu.com/")
            print("Please log in via the browser window (e.g., scan QR code).")

            # Loop to check for the auth cookie
            logged_in = False
            start_time = time.time()
            timeout = 300  # 5 minutes timeout

            while time.time() - start_time < timeout:
                if page.is_closed():
                    print("Browser was closed by user.")
                    break

                cookies = context.cookies()
                # 'xq_a_token' is the key authentication cookie for Xueqiu
                auth_token = next((c for c in cookies if c['name'] == 'xq_a_token'), None)

                if auth_token:
                    print("Login detected!")
                    save_cookies(cookies)
                    logged_in = True
                    break

                time.sleep(1)

            if not logged_in:
                print("Login timed out or failed.")

        except Exception as e:
            print(f"An error occurred during login: {e}")
        finally:
            if browser:
                try:
                    browser.close()
                except:
                    pass

def save_cookies(cookies):
    """Saves cookies to a JSON file."""
    with open(COOKIES_FILE, 'w') as f:
        json.dump(cookies, f)
    print(f"Cookies saved to {COOKIES_FILE}")

def load_cookies():
    """Loads cookies from the JSON file."""
    if not os.path.exists(COOKIES_FILE):
        return None
    try:
        with open(COOKIES_FILE, 'r') as f:
            return json.load(f)
    except:
        return None

def is_logged_in():
    """Checks if valid cookies exist (basic check)."""
    cookies = load_cookies()
    if not cookies:
        return False
    # Check for xq_a_token
    token = next((c for c in cookies if c['name'] == 'xq_a_token'), None)
    return token is not None

def get_cookies_dict():
    """Returns cookies in a format suitable for requests library."""
    cookies_list = load_cookies()
    if not cookies_list:
        return {}
    return {c['name']: c['value'] for c in cookies_list}
