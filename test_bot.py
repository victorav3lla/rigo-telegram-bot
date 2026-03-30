# test_bot.py — Test sending a real message to Telegram

import os
import asyncio
from dotenv import load_dotenv
from notifier import format_surebet, send_alert

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Simulated surebet
fake_arb = {
    "id": 99999,
    "percent": 3.45,
    "event_name": "Arsenal vs Chelsea",
    "sport_name": "Football",
    "league": "Premier League",
    "is_live": False,
    "created_at": "2026-03-30 18:25:00",
    "event_start": "2026-03-30 20:00:00",
    "bets": [
        {
            "bookmaker_name": "Bet365",
            "bet_name": "Home Win",
            "odd": 2.10,
            "stake_percent": 52.3
        },
        {
            "bookmaker_name": "Pinnacle",
            "bet_name": "Draw or Away",
            "odd": 1.95,
            "stake_percent": 47.7
        }
    ]
}
# Send it to your channel
asyncio.run(send_alert(BOT_TOKEN, CHAT_ID, fake_arb))
