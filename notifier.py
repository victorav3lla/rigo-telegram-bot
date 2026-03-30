# notifier.py — Sends surebet alerts to Telegram

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
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

# Map bookmaker names to their URLs
# Add more as you discover which bookmakers your filter returns
BOOKMAKER_URLS = {
    "bet365": "https://www.bet365.com",
    "pinnacle": "https://www.pinnacle.com",
    "1xbet": "https://1xbet.com",
    "22bet": "https://22bet.com",
    "betfair": "https://www.betfair.com",
    "unibet": "https://www.unibet.com",
    "bwin": "https://www.bwin.com",
    "williamhill": "https://www.williamhill.com",
    "william hill": "https://www.williamhill.com",
    "betway": "https://www.betway.com",
    "marathon": "https://www.marathonbet.com",
    "marathonbet": "https://www.marathonbet.com",
    "sisal": "https://www.sisal.it",
    "pokerstars": "https://www.pokerstars.com",
    "888sport": "https://www.888sport.com",
    "betsson": "https://www.betsson.com",
    "cloudbet": "https://www.cloudbet.com",
    "sbobet": "https://www.sbobet.com",
    "dafabet": "https://www.dafabet.com",
    "betclic": "https://www.betclic.com",
    "parimatch": "https://www.parimatch.com",
    "stake": "https://stake.com",
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


def get_bookmaker_url(bookmaker_name):
    """Look up the URL for a bookmaker. Returns None if not found."""
    if not bookmaker_name:
        return None
    return BOOKMAKER_URLS.get(bookmaker_name.lower(), None)


def build_buttons(bets):
    """
    Builds an InlineKeyboardMarkup with a button for each bookmaker.
    Buttons link to the bookmaker's website.
    """
    buttons = []

    for bet in bets:
        bookie = bet.get("bookmaker_name", "")
        url = get_bookmaker_url(bookie)

        if url:
            buttons.append(
                InlineKeyboardButton(text=f"🔗 {bookie}", url=url)
            )

    if not buttons:
        return None

    # Arrange buttons in rows of 2 (like the screenshot)
    rows = []
    for i in range(0, len(buttons), 2):
        rows.append(buttons[i:i + 2])

    return InlineKeyboardMarkup(rows)


def format_surebet(arb):
    """
    Takes a single surebet dict and returns a formatted string.
    """

    roi = arb.get("percent", 0)
    event = arb.get("event_name", "Unknown Event")
    sport = arb.get("sport_name", "")
    league = arb.get("league", "")
    is_live = arb.get("is_live", False)
    created_at = arb.get("created_at", "")
    event_start = arb.get("started_at") or arb.get("event_start", "")
    bets = arb.get("bets", [])

    emoji = get_sport_emoji(sport)

    status = "🔴 LIVE" if is_live else "📋 PRE"
    message = f"🔥 <b>SUREBET FOUND</b> {status}\n"
    message += "━━━━━━━━━━━━━━━━━━━━\n"

    message += f"{emoji} <b>{sport}</b>"
    if league:
        message += f" — {league}"
    message += "\n"
    message += f"📌 {event}\n"
    message += f"💰 ROI: <b>{roi:.2f}%</b>\n"

    if event_start:
        message += f"🗓 Kick-off: {event_start}\n"

    age = get_arb_age(created_at)
    if age:
        message += f"⏱ Found: {age}\n"
    elif created_at:
        message += f"🕐 Found: {created_at}\n"

    message += "━━━━━━━━━━━━━━━━━━━━\n"

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
    Formats a surebet and sends it to Telegram with bookmaker buttons.
    """

    message = format_surebet(arb)
    buttons = build_buttons(arb.get("bets", []))

    bot = telegram.Bot(token=bot_token)

    try:
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode="HTML",
            reply_markup=buttons  # This adds the clickable buttons
        )
        print(f"[Telegram] Alert sent: {arb.get('id', '?')}")
    except telegram.error.TelegramError as e:
        print(f"[Telegram] Failed to send: {e}")
