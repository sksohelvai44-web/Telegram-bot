import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get token from environment variable
TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    logger.error("BOT_TOKEN environment variable not set!")
    exit(1)

# ==================== MENU ====================
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📋 Task", callback_data="task")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance")],
        [InlineKeyboardButton("💳 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("👤 Profile", callback_data="profile")],
        [InlineKeyboardButton("🔗 Refer", callback_data="refer")],
        [InlineKeyboardButton("🌐 Language", callback_data="language")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ==================== HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with main menu"""
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Welcome {user.first_name}!\n\n"
        "📌 This bot helps you earn money by doing simple tasks.\n"
        "✅ Click the button below to start:",
        reply_markup=get_main_menu()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "task":
        keyboard = [
            [InlineKeyboardButton("📱 Instagram 2FA", callback_data="insta")],
            [InlineKeyboardButton("📘 Facebook", callback_data="fb")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
        ]
        await query.edit_message_text(
            "📋 Select Task Type:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "insta":
        text = """⏳ Review time: 24 h

📋 Task: 📱 Create Inst (2FA)

📄 Description: In this task, you must create a new Inst acc using only a real mobile device.
🔐 REQUIRED!
You must use the information provided by the Telegram bot to register.

❗If you use your own information, your application will be REJECTED without verification.

⏳ Review time: 24 h"""
        
        keyboard = [
            [InlineKeyboardButton("✅ Start", callback_data="start_task")],
            [InlineKeyboardButton("🎥 Video", callback_data="video")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
        ]
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "start_task":
        keyboard = [
            [InlineKeyboardButton("🔐 Set 2FA", callback_data="set_2fa")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
        ]
        await query.edit_message_text(
            "✅ Account Created!\n\n👤 Username: insta_user_1234\n🔑 Password: P@ssW0rd#1234\n\n📌 Please login and complete registration.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "set_2fa":
        await query.edit_message_text(
            "📱 Please enter your 2FA code from Google Authenticator:\n\nExample: 123456",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Done", callback_data="done_2fa")]
            ])
        )

    elif data == "done_2fa":
        await query.edit_message_text(
            "✅ Task Completed Successfully!\n\n💰 Reward: 50.00 BDT (Pending)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main")]
            ])
        )

    elif data == "video":
        await query.edit_message_text(
            "🎥 Tutorial Video:\nhttps://www.youtube.com/watch?v=VIDEO_ID",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="insta")]
            ])
        )

    elif data == "balance":
        await query.edit_message_text(
            "💰 Your Balance\n\n📊 Total Balance: 0.00 BDT\n📈 Total Earned: 0.00 BDT\n⏳ Pending: 0.00 BDT",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main")]
            ])
        )

    elif data == "withdraw":
        keyboard = [
            [InlineKeyboardButton("📱 Bkash", callback_data="bkash")],
            [InlineKeyboardButton("📱 Nagad", callback_data="nagad")],
            [InlineKeyboardButton("❌ Cancel", callback_data="main")]
        ]
        await query.edit_message_text(
            "💳 Withdraw Money\n\n💰 Your Balance: 0.00 BDT\n⚠️ Minimum: 50.00 BDT",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "profile":
        await query.edit_message_text(
            "👤 Your Profile\n\n🆔 ID: 123456\n👤 Username: @user\n📅 Joined: 2024-01-01\n💰 Balance: 0.00 BDT",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main")]
            ])
        )

    elif data == "refer":
        await query.edit_message_text(
            "🔗 Referral Program\n\n💰 Earn 10% commission for life!\n\nYour referral link:\nhttps://t.me/YourBot?start=ref_ABC123",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main")]
            ])
        )

    elif data == "language":
        keyboard = [
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
            [InlineKeyboardButton("🇧🇩 বাংলা", callback_data="lang_bn")]
        ]
        await query.edit_message_text(
            "🌐 Select Language:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data in ["lang_en", "lang_bn"]:
        await query.edit_message_text(
            "✅ Language changed successfully!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main")]
            ])
        )

    elif data == "cancel":
        await query.edit_message_text(
            "❌ Cancelled!",
            reply_markup=get_main_menu()
        )

    else:
        # Default: Go to main menu
        await query.edit_message_text(
            "🏠 Main Menu",
            reply_markup=get_main_menu()
        )

# ==================== MAIN ====================
def main():
    """Start the bot"""
    logger.info("Starting bot...")
    
    # Create application
    app = Application.builder().token(TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Run the bot
    logger.info("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
