import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler

from betburger import fetch_surebets
from notifier import send_alert
from commands import (
    bot_state,
    start_command,
    status_command,
    setroi_command,
    pause_command,
    resume_command,
)

load_dotenv()

# Config
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ACCESS_TOKEN = os.getenv("BETBURGER_ACCESS_TOKEN")
SEARCH_FILTER = os.getenv("BETBURGER_SEARCH_FILTER")
MODE = os.getenv("BETBURGER_MODE", "prematch")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "30"))
MAX_ALERTS = int(os.getenv("MAX_ALERTS_PER_CYCLE", "5"))

# Track seen arb IDs
seen_ids = set()


async def poll_betburger(context):
    """Called automatically every POLL_INTERVAL seconds by the JobQueue."""

    # If paused, skip this cycle
    if not bot_state["running"]:
        return

    # 1. Fetch
    arbs = fetch_surebets(ACCESS_TOKEN, SEARCH_FILTER, MODE)

    # 2. Filter
    min_roi = bot_state["min_roi"]
    new_arbs = []
    for arb in arbs:
        arb_id = arb.get("id")
        roi = arb.get("percent", 0)
        if arb_id not in seen_ids and roi >= min_roi:
            new_arbs.append(arb)

    # 3. Sort by ROI (highest first), take top N
    new_arbs.sort(key=lambda a: a.get("percent", 0), reverse=True)
    top_arbs = new_arbs[:MAX_ALERTS]

    # 4. Send alerts
    for arb in top_arbs:
        await send_alert(BOT_TOKEN, CHAT_ID, arb)
        seen_ids.add(arb.get("id"))
        bot_state["alerts_sent"] += 1

    # 5. Keep seen_ids from growing forever
    if len(seen_ids) > 500:
        excess = len(seen_ids) - 500
        for _ in range(excess):
            seen_ids.pop()

    bot_state["cycles_completed"] += 1


def main():
    """Build the app, register commands, start the polling job."""

    # Check required config
    required = {
        "TELEGRAM_BOT_TOKEN": BOT_TOKEN,
        "TELEGRAM_CHAT_ID": CHAT_ID,
        "BETBURGER_ACCESS_TOKEN": ACCESS_TOKEN,
        "BETBURGER_SEARCH_FILTER": SEARCH_FILTER,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        print(f"[Error] Missing env vars: {', '.join(missing)}")
        print("Copy .env.example to .env and fill in your values.")
        return

    # 1. Create the Application
    app = Application.builder().token(BOT_TOKEN).build()

    # 2. Register commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("setroi", setroi_command))
    app.add_handler(CommandHandler("pause", pause_command))
    app.add_handler(CommandHandler("resume", resume_command))

    # 3. Schedule the BetBurger polling job
    app.job_queue.run_repeating(
        poll_betburger,
        interval=POLL_INTERVAL,
        first=5,  # Wait 5 seconds before the first poll
    )

    # 4. Start the bot
    print("[Bot] Starting...")
    print(f"  Mode: {MODE}")
    print(f"  Poll interval: {POLL_INTERVAL}s")
    print(f"  Min ROI: {bot_state['min_roi']}%")
    print(f"  Max alerts/cycle: {MAX_ALERTS}")
    print(f"  Commands: /start /status /setroi /pause /resume")
    print()
    app.run_polling()


if __name__ == "__main__":
    main()
