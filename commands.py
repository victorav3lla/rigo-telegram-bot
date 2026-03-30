# commands.py — Handles Telegram bot commands (admin-only)

import os

# Bot state — shared with bot.py
bot_state = {
    "running": True,
    "min_roi": float(os.getenv("MIN_ROI", "1.0")),
    "alerts_sent": 0,
    "cycles_completed": 0,
}


def is_admin(user_id):
    """Check if the user is the admin."""
    admin_id = os.getenv("ADMIN_ID")
    if not admin_id:
        return False
    return str(user_id) == admin_id


async def start_command(update, context):
    """Anyone can use /start — just a welcome message."""
    await update.message.reply_text(
        "🍔 RigoBet Alert Bot\n\n"
        "This bot sends surebet alerts to a channel.\n"
        "It's not meant for direct interaction."
    )


async def status_command(update, context):
    """Admin only — shows bot status."""
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("⛔ Admin only.")
        return

    status = "▶️ Running" if bot_state["running"] else "⏸ Paused"
    msg = (
        f"📊 <b>Bot Status</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"State: {status}\n"
        f"Min ROI: {bot_state['min_roi']}%\n"
        f"Alerts sent: {bot_state['alerts_sent']}\n"
        f"Cycles completed: {bot_state['cycles_completed']}"
    )
    await update.message.reply_text(msg, parse_mode="HTML")


async def setroi_command(update, context):
    """Admin only — change minimum ROI. Usage: /setroi 2.5"""
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("⛔ Admin only.")
        return

    # context.args is a list of words after the command
    # "/setroi 2.5" → context.args = ["2.5"]
    if not context.args:
        await update.message.reply_text(
            f"Current min ROI: {bot_state['min_roi']}%\n"
            f"Usage: /setroi 2.5"
        )
        return

    try:
        new_roi = float(context.args[0])
        bot_state["min_roi"] = new_roi
        await update.message.reply_text(f"✅ Min ROI set to {new_roi}%")
    except ValueError:
        await update.message.reply_text("❌ Invalid number. Usage: /setroi 2.5")


async def pause_command(update, context):
    """Admin only — pause alerts."""
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("⛔ Admin only.")
        return

    bot_state["running"] = False
    await update.message.reply_text("⏸ Bot paused. Use /resume to restart.")


async def resume_command(update, context):
    """Admin only — resume alerts."""
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("⛔ Admin only.")
        return

    bot_state["running"] = True
    await update.message.reply_text("▶️ Bot resumed!")
