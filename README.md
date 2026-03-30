# RigoBet — Telegram Surebet Alert Bot

A Python bot that polls a betting API for arbitrage (surebet) opportunities and sends real-time alerts to a Telegram channel.

## Features

- **Automated polling** — Fetches surebets on a configurable interval (prematch or live)
- **Smart filtering** — Filters by minimum ROI and deduplicates to avoid repeat alerts
- **Formatted alerts** — Sport-specific emojis, ROI, bookmaker odds, stakes, arb age, and event start time
- **Admin commands** — Control the bot via Telegram DM:
  - `/start` — Welcome message
  - `/status` — View bot state, alerts sent, and cycles completed
  - `/setroi` — Change minimum ROI threshold on the fly
  - `/pause` / `/resume` — Toggle alert delivery
- **Admin-only access** — Commands are restricted to a single authorized user

## Tech Stack

- **Python 3.12**
- **python-telegram-bot** — Telegram Bot API wrapper with JobQueue scheduler
- **requests** — HTTP client for the betting API
- **python-dotenv** — Environment variable management

## Project Structure

```
rigo-telegram-bot/
├── bot.py              # Entry point — config, polling job, command registration
├── bet.py              # Betting API client
├── notifier.py         # Alert formatting and Telegram message delivery
├── commands.py         # Admin command handlers and shared bot state
├── test_bot.py         # Test script with simulated data
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
└── .gitignore
```

## Setup

```bash
# Clone the repo
git clone git@github.com:victorav3lla/rigo-telegram-bot.git
cd rigo-telegram-bot

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials
```

## Configuration

| Variable | Description | Default |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot token from [@BotFather](https://t.me/BotFather) | *required* |
| `TELEGRAM_CHAT_ID` | Target channel or group chat ID | *required* |
| `BET_ACCESS_TOKEN` | Betting API access token | *required* |
| `BET_SEARCH_FILTER` | Betting API filter ID | *required* |
| `ADMIN_ID` | Your Telegram user ID (for admin commands) | *required* |
| `BET_MODE` | `prematch` or `live` | `prematch` |
| `POLL_INTERVAL` | Seconds between API polls | `30` |
| `MIN_ROI` | Minimum ROI % to trigger an alert | `1.0` |
| `MAX_ALERTS_PER_CYCLE` | Max alerts sent per poll cycle | `5` |

## Usage

```bash
python bot.py
```

The bot will begin polling the betting API and sending alerts to your configured Telegram channel. Use `Ctrl+C` to stop.

## Alert Preview

```
🔥 SUREBET FOUND 📋 PRE
━━━━━━━━━━━━━━━━━━━━
⚽ Football — Premier League
📌 Arsenal vs Chelsea
💰 ROI: 3.45%
🗓 Kick-off: 2026-03-30 20:00:00
⏱ Found: 2m ago
━━━━━━━━━━━━━━━━━━━━
  1. Bet365
     Home Win @ 2.10 (52.3%)
  2. Pinnacle
     Draw or Away @ 1.95 (47.7%)
━━━━━━━━━━━━━━━━━━━━
```

## License

MIT
