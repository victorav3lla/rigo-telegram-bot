# betburger.py — Talks to the BetBurger API

import requests


def fetch_surebets(access_token, search_filter, mode="prematch"):
    """
    Calls the BetBurger API and returns a list of surebets.
    Returns an empty list if anything goes wrong.
    """

    # 1. Pick the right URL based on mode
    if mode == "live":
        url = "https://rest-api-lv.betburger.com/api/v1/arbs/pro-search"
    else:
        url = "https://rest-api-pr.betburger.com/api/v1/arbs/pro-search"

    # 2. The data we send to BetBurger (like filling a form)
    payload = {
        "access_token": access_token,
        "search_filter": search_filter
    }

    # 3. Make the POST request
    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()  # Raises an error if status is 4xx or 5xx
    except requests.RequestException as e:
        print(f"[BetBurger] Request failed: {e}")
        return []

    # 4. Parse the JSON and return the arbs list
    data = response.json()
    arbs = data.get("arbs", [])

    print(f"[BetBurger] Received {len(arbs)} surebets")
    return arbs
