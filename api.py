import requests

API_URL = "https://www.cbr-xml-daily.ru/daily_json.js"


def fetch_rates() -> dict:
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching rates: {e}")
        return {}