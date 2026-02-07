import requests
import auth
import time

class XueqiuAPI:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://xueqiu.com/",
            "Origin": "https://xueqiu.com"
        }
        self.refresh_cookies()

    def refresh_cookies(self):
        self.cookies = auth.get_cookies_dict()

    def _get(self, url, params=None):
        if not self.cookies:
            # Try reloading in case they were just saved
            self.refresh_cookies()
            if not self.cookies:
                print("Warning: No cookies found. Some APIs might fail.")

        try:
            response = requests.get(url, headers=self.headers, cookies=self.cookies, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API Request Failed: {e}")
            return None

    def get_quote(self, symbol):
        """
        Fetches real-time quote for a symbol.
        URL: https://stock.xueqiu.com/v5/stock/quote.json
        """
        url = "https://stock.xueqiu.com/v5/stock/quote.json"
        params = {
            "symbol": symbol,
            "extend": "detail"
        }
        data = self._get(url, params)
        if data and 'data' in data and 'quote' in data['data']:
            return data['data']['quote']
        return None

    def get_kline(self, symbol, period="day", count=-100):
        """
        Fetches K-line data.
        period: day, week, month, 1m, 5m, 15m, 30m, 60m
        count: negative number usually implies 'last N points' from 'begin' time.
        """
        url = "https://stock.xueqiu.com/v5/stock/chart/kline.json"
        # Current time in milliseconds
        begin = int(time.time() * 1000)

        params = {
            "symbol": symbol,
            "begin": begin,
            "period": period,
            "type": "before",
            "count": count,
            "indicator": "kline"
        }
        data = self._get(url, params)
        if data and 'data' in data and 'item' in data['data']:
            # data['data']['item'] is a list of lists: [timestamp, volume, open, high, low, close, chg, percent, turnover]
            # Column mapping usually: timestamp, volume, open, high, low, close...
            return {
                "columns": data['data']['column'],
                "items": data['data']['item']
            }
        return None

    def get_hot_discussions(self):
        """
        Fetches trending/hot discussions.
        Using public timeline category -1 (Hot)
        """
        url = "https://xueqiu.com/v4/statuses/public_timeline_by_category.json"
        params = {
            "category": -1,
            "count": 20
        }
        # This API mimics main page feed
        data = self._get(url, params)
        # Structure usually: list of statuses directly or inside a key?
        # Often it returns a list directly or {"list": [...]}
        # Based on v4/public_timeline, it might be a list directly.
        # Let's handle both.
        if isinstance(data, list):
            return data
        if data and 'list' in data:
            return data['list']
        return []

    def get_following_feed(self):
        """
        Fetches user's home timeline (following).
        """
        url = "https://xueqiu.com/v4/statuses/home_timeline.json"
        params = {
            "count": 20,
            "type": 0
        }
        data = self._get(url, params)
        if data and 'statuses' in data:
            return data['statuses']
        return []

    def get_stock_comments(self, symbol):
        """
        Fetches discussions specific to a stock.
        """
        url = "https://xueqiu.com/statuses/search.json"
        params = {
            "count": 20,
            "comment": 0,
            "symbol": symbol,
            "source": "all",
            "sort": "time",
            "page": 1,
            "q": symbol
        }
        data = self._get(url, params)
        if data and 'list' in data:
            return data['list']
        return []

    def get_watchlist(self):
        """
        Fetches user's watchlist/portfolio.
        """
        url = "https://stock.xueqiu.com/v5/stock/portfolio/stock/list.json"
        params = {
            "category": 1,
            "pid": -1,
            "size": 1000,
            "x": 1.2,
            "page": 1
        }
        data = self._get(url, params)
        if data and 'data' in data and 'list' in data['data']:
            return data['data']['list']
        return []

# Helper to format display data
def format_post(post):
    """Parses relevant fields from a post object."""
    try:
        user = post.get('user', {})
        return {
            "id": post.get('id'),
            "user_name": user.get('screen_name', 'Unknown'),
            "title": post.get('title', ''),
            "text": post.get('text', ''), # often html
            "description": post.get('description', ''),
            "created_at": post.get('created_at', 0), # timestamp
            "retweeted_status": post.get('retweeted_status', None)
        }
    except:
        return {}
