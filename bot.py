import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    logger.error("BOT_TOKEN not set!")
    exit(1)

# ==================== REPLY KEYBOARD (নিচের কিবোর্ড) ====================

def get_main_keyboard():
    """This creates the keyboard at the bottom"""
    keyboard = [
        [KeyboardButton("📋 Task"), KeyboardButton("💰 Balance")],
        [KeyboardButton("💳 Withdraw"), KeyboardButton("👤 Profile")],
        [KeyboardButton("🔗 Refer"), KeyboardButton("🌐 Language")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_task_keyboard():
    keyboard = [
        [KeyboardButton("📱 Instagram 2FA"), KeyboardButton("📘 Facebook")],
        [KeyboardButton("❌ Cancel")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_withdraw_keyboard():
    keyboard = [
        [KeyboardButton("📱 Bkash"), KeyboardButton("📱 Nagad")],
        [KeyboardButton("❌ Cancel")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_language_keyboard():
    keyboard = [
        [KeyboardButton("🇬🇧 English"), KeyboardButton("🇧🇩 বাংলা")],
        [KeyboardButton("❌ Cancel")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_cancel_keyboard():
    keyboard = [
        [KeyboardButton("🏠 Main Menu")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

# ==================== COMMAND HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Welcome {user.first_name}!\n\n"
        "📌 This bot helps you earn money by doing simple tasks.\n"
        "✅ Use the buttons below to navigate:",
        reply_markup=get_main_keyboard()
    )

# ==================== MESSAGE HANDLER ====================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # === Main Menu ===
    if text == "📋 Task":
        await update.message.reply_text(
            "📋 Select Task Type:",
            reply_markup=get_task_keyboard()
        )
        return

    elif text == "💰 Balance":
        await update.message.reply_text(
            "💰 Your Balance\n\n"
            "📊 Total Balance: 150.00 BDT\n"
            "📈 Total Earned: 200.00 BDT\n"
            "⏳ Pending: 50.00 BDT",
            reply_markup=get_main_keyboard()
        )
        return

    elif text == "💳 Withdraw":
        await update.message.reply_text(
            "💳 Withdraw Money\n\n"
            "💰 Your Balance: 150.00 BDT\n"
            "⚠️ Minimum Withdrawal: 50.00 BDT\n\n"
            "Select withdrawal method:",
            reply_markup=get_withdraw_keyboard()
        )
        return

    elif text == "👤 Profile":
        await update.message.reply_text(
            "👤 Your Profile\n\n"
            "🆔 User ID: 123456789\n"
            "👤 Username: @yourusername\n"
            "📅 Joined: 2024-01-15\n"
            "💰 Balance: 150.00 BDT\n"
            "🏆 Total Tasks: 5\n"
            "✅ Completed: 3\n"
            "⏳ Pending: 2",
            reply_markup=get_main_keyboard()
        )
        return

    elif text == "🔗 Refer":
        await update.message.reply_text(
            "🔗 Referral Program\n\n"
            "💰 Earn 10% commission for life!\n\n"
            "Your referral link:\n"
            "https://t.me/YourBot?start=ref_ABC123\n\n"
            "📊 Your Stats:\n"
            "👥 Total Referrals: 5\n"
            "💰 Commission Earned: 75.00 BDT",
            reply_markup=get_main_keyboard()
        )
        return

    elif text == "🌐 Language":
        await update.message.reply_text(
            "🌐 Select Language:",
            reply_markup=get_language_keyboard()
        )
        return

    # === Task Menu ===
    elif text == "📱 Instagram 2FA":
        await update.message.reply_text(
            "✅ Instagram 2FA Task\n\n"
            "⏳ Review time: 24 h\n"
            "💰 Reward: 50 BDT\n\n"
            "Type /start_instagram to begin the task.",
            reply_markup=get_cancel_keyboard()
        )
        return

    elif text == "📘 Facebook":
        await update.message.reply_text(
            "📘 Facebook Task\n\n"
            "⏳ Coming soon! Stay tuned.",
            reply_markup=get_task_keyboard()
        )
        return

    # === Withdraw Menu ===
    elif text == "📱 Bkash":
        await update.message.reply_text(
            "✅ Withdrawal Request Submitted!\n\n"
            "📱 Method: Bkash\n"
            "📞 Number: 01XXXXXXXXX\n"
            "💰 Amount: 100.00 BDT\n\n"
            "⏳ Your request is pending. You will receive payment within 24 hours.",
            reply_markup=get_main_keyboard()
        )
        return

    elif text == "📱 Nagad":
        await update.message.reply_text(
            "✅ Withdrawal Request Submitted!\n\n"
            "📱 Method: Nagad\n"
            "📞 Number: 01XXXXXXXXX\n"
            "💰 Amount: 100.00 BDT\n\n"
            "⏳ Your request is pending. You will receive payment within 24 hours.",
            reply_markup=get_main_keyboard()
        )
        return

    # === Language Menu ===
    elif text == "🇬🇧 English":
        await update.message.reply_text(
            "✅ Language changed to English!",
            reply_markup=get_main_keyboard()
        )
        return

    elif text == "🇧🇩 বাংলা":
        await update.message.reply_text(
            "✅ ভাষা পরিবর্তন করে বাংলা করা হয়েছে!",
            reply_markup=get_main_keyboard()
        )
        return

    # === Cancel / Main Menu ===
    elif text == "❌ Cancel":
        await update.message.reply_text(
            "❌ Cancelled!",
            reply_markup=get_main_keyboard()
        )
        return

    elif text == "🏠 Main Menu":
        await update.message.reply_text(
            "🏠 Main Menu",
            reply_markup=get_main_keyboard()
        )
        return

    # === Unknown ===
    else:
        await update.message.reply_text(
            "❌ Unknown command! Please use the buttons below.",
            reply_markup=get_main_keyboard()
        )

# ==================== START INSTAGRAM TASK ====================

async def start_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Account Created!\n\n"
        "👤 Username: insta_user_5829\n"
        "🔑 Password: P@ssW0rd#2024\n\n"
        "📌 Please login with these credentials and complete the registration.\n\n"
        "Type /done_instagram when finished.",
        reply_markup=get_cancel_keyboard()
    )

async def done_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Task Completed Successfully!\n\n"
        "⏳ Your task is under review. You will receive reward within 24 hours.\n\n"
        "💰 Reward: 50.00 BDT (Pending)",
        reply_markup=get_main_keyboard()
    )

# ==================== PERSISTENT MENU (Telegram-এর নিচের মেনু) ====================

async def set_persistent_menu(app):
    commands = [
        BotCommand("start", "🚀 Start"),
        BotCommand("menu", "📋 Menu"),
    ]
    await app.bot.set_my_commands(commands)
    logger.info("✅ Persistent menu set!")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏠 Main Menu",
        reply_markup=get_main_keyboard()
    )

# ==================== MAIN ====================

def main():
    logger.info("Starting bot...")
    
    app = Application.builder().token(TOKEN).build()
    
    # Set persistent menu
    app.post_init = set_persistent_menu
    
    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("start_instagram", start_instagram))
    app.add_handler(CommandHandler("done_instagram", done_instagram))
    
    # Message handler (for buttons)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
