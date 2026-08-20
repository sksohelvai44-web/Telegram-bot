import os
import logging
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    logger.error("BOT_TOKEN not set!")
    exit(1)

# ==================== COMMAND HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Welcome {user.first_name}!\n\n"
        "📌 This bot helps you earn money by doing simple tasks.\n\n"
        "Use the menu below to navigate:"
    )

async def task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Available Tasks:\n\n"
        "1. 📱 Instagram 2FA - 50 BDT\n"
        "2. 📘 Facebook - Coming Soon\n\n"
        "Type /start to go back to main menu."
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 Your Balance\n\n"
        "📊 Total Balance: 150.00 BDT\n"
        "📈 Total Earned: 200.00 BDT\n"
        "⏳ Pending: 50.00 BDT"
    )

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💳 Withdraw Money\n\n"
        "💰 Your Balance: 150.00 BDT\n"
        "⚠️ Minimum Withdrawal: 50.00 BDT\n\n"
        "Send /withdraw_bkash for Bkash\n"
        "Send /withdraw_nagad for Nagad"
    )

async def withdraw_bkash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Withdrawal Request Submitted!\n\n"
        "📱 Method: Bkash\n"
        "📞 Number: 01XXXXXXXXX\n"
        "💰 Amount: 100.00 BDT\n\n"
        "⏳ Your request is pending. You will receive payment within 24 hours."
    )

async def withdraw_nagad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Withdrawal Request Submitted!\n\n"
        "📱 Method: Nagad\n"
        "📞 Number: 01XXXXXXXXX\n"
        "💰 Amount: 100.00 BDT\n\n"
        "⏳ Your request is pending. You will receive payment within 24 hours."
    )

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👤 Your Profile\n\n"
        "🆔 User ID: 123456789\n"
        "👤 Username: @yourusername\n"
        "📅 Joined: 2024-01-15\n"
        "💰 Balance: 150.00 BDT\n"
        "🏆 Total Tasks: 5\n"
        "✅ Completed: 3\n"
        "⏳ Pending: 2"
    )

async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔗 Referral Program\n\n"
        "💰 Earn 10% commission for life!\n\n"
        "Your referral link:\n"
        "https://t.me/YourBot?start=ref_ABC123\n\n"
        "📊 Your Stats:\n"
        "👥 Total Referrals: 5\n"
        "💰 Commission Earned: 75.00 BDT"
    )

async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌐 Select Language:\n\n"
        "Send /lang_en for English\n"
        "Send /lang_bn for বাংলা"
    )

async def lang_en(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Language changed to English!")

async def lang_bn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ ভাষা পরিবর্তন করে বাংলা করা হয়েছে!")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏠 Main Menu\n\n"
        "Use the commands below to navigate:"
    )

# ==================== PERSISTENT MENU (নিচের মেনু) ====================

async def set_persistent_menu(app):
    commands = [
        BotCommand("start", "🚀 Start"),
        BotCommand("menu", "📋 Menu"),
        BotCommand("task", "📋 Task"),
        BotCommand("balance", "💰 Balance"),
        BotCommand("withdraw", "💳 Withdraw"),
        BotCommand("profile", "👤 Profile"),
        BotCommand("refer", "🔗 Refer"),
        BotCommand("language", "🌐 Language"),
    ]
    await app.bot.set_my_commands(commands)
    logger.info("✅ Persistent menu set!")

# ==================== MAIN ====================

def main():
    logger.info("Starting bot...")

    app = Application.builder().token(TOKEN).build()

    # Set persistent menu
    app.post_init = set_persistent_menu

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("task", task))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("withdraw", withdraw))
    app.add_handler(CommandHandler("withdraw_bkash", withdraw_bkash))
    app.add_handler(CommandHandler("withdraw_nagad", withdraw_nagad))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("refer", refer))
    app.add_handler(CommandHandler("language", language))
    app.add_handler(CommandHandler("lang_en", lang_en))
    app.add_handler(CommandHandler("lang_bn", lang_bn))

    logger.info("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
