# notifier.py — Sends surebet alerts to Telegram

import telegram
from datetime import datetime, timezone


# Map sport names to emojis
SPORT_EMOJIS = {
    "football": "⚽",
    "soccer": "⚽",
    "tennis": "🎾",
    "basketball": "🏀",
    "ice hockey": "🏒",
    "volleyball": "🏐",
    "baseball": "⚾",
    "handball": "🤾",
    "cricket": "🏏",
    "rugby": "🏉",
    "boxing": "🥊",
    "mma": "🥊",
    "esports": "🎮",
    "table tennis": "🏓",
}


def get_sport_emoji(sport_name):
    """Returns the emoji for a sport, or 🏆 as default."""
    if not sport_name:
        return "🏆"
    return SPORT_EMOJIS.get(sport_name.lower(), "🏆")


def get_arb_age(created_at):
    """
    Calculates how old the arb is.
    Returns a string like '2m ago' or '45s ago'.
    """
    if not created_at:
        return None

    try:
        # BetBurger timestamps can vary in format
        # Try common formats
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
            try:
                created_time = datetime.strptime(created_at, fmt)
                created_time = created_time.replace(tzinfo=timezone.utc)
                break
            except ValueError:
                continue
        else:
            return None

        now = datetime.now(timezone.utc)
        diff = now - created_time
        seconds = int(diff.total_seconds())

        if seconds < 60:
            return f"{seconds}s ago"
        elif seconds < 3600:
            return f"{seconds // 60}m ago"
        else:
            return f"{seconds // 3600}h ago"

    except Exception:
        return None


def format_surebet(arb):
    """
    Takes a single surebet dict and returns a formatted string.
    """

    # Pull out the main info, with fallbacks if a field is missing
    roi = arb.get("percent", 0)
    event = arb.get("event_name", "Unknown Event")
    sport = arb.get("sport_name", "")
    league = arb.get("league", "")
    is_live = arb.get("is_live", False)
    created_at = arb.get("created_at", "")
    event_start = arb.get("started_at") or arb.get("event_start", "")
    bets = arb.get("bets", [])

    # Sport emoji
    emoji = get_sport_emoji(sport)

    # Header
    status = "🔴 LIVE" if is_live else "📋 PRE"
    message = f"🔥 <b>SUREBET FOUND</b> {status}\n"
    message += "━━━━━━━━━━━━━━━━━━━━\n"

    # Event info
    message += f"{emoji} <b>{sport}</b>"
    if league:
        message += f" — {league}"
    message += "\n"
    message += f"📌 {event}\n"
    message += f"💰 ROI: <b>{roi:.2f}%</b>\n"

    # Event start time
    if event_start:
        message += f"🗓 Kick-off: {event_start}\n"

    # Arb age
    age = get_arb_age(created_at)
    if age:
        message += f"⏱ Found: {age}\n"
    elif created_at:
        message += f"🕐 Found: {created_at}\n"

    message += "━━━━━━━━━━━━━━━━━━━━\n"

    # Each bet (each "side" of the arb)
    for i, bet in enumerate(bets, 1):
        bookie = bet.get("bookmaker_name", "Unknown")
        outcome = bet.get("bet_name", "—")
        odd = bet.get("odd", "—")
        stake = bet.get("stake_percent")

        message += f"  {i}. <b>{bookie}</b>\n"
        message += f"     {outcome} @ <b>{odd}</b>"
        if stake:
            message += f" ({stake:.1f}%)"
        message += "\n"

    message += "━━━━━━━━━━━━━━━━━━━━"
    return message


async def send_alert(bot_token, chat_id, arb):
    """
    Formats a surebet and sends it to the Telegram channel.
    """

    message = format_surebet(arb)

    bot = telegram.Bot(token=bot_token)

    try:
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode="HTML"
        )
        print(f"[Telegram] Alert sent: {arb.get('id', '?')}")
    except telegram.error.TelegramError as e:
        print(f"[Telegram] Failed to send: {e}")
