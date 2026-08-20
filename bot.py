import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    logger.error("BOT_TOKEN not set!")
    exit(1)

# ==================== MAIN MENU BUTTONS ====================
def get_main_menu():
    """Main menu with 6 buttons - exactly like you want"""
    keyboard = [
        [InlineKeyboardButton("📋 Task", callback_data="task")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance")],
        [InlineKeyboardButton("💳 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("👤 Profile", callback_data="profile")],
        [InlineKeyboardButton("🔗 Refer", callback_data="refer")],
        [InlineKeyboardButton("🌐 Language", callback_data="language")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ==================== TASK MENU ====================
def get_task_menu():
    """Task selection menu"""
    keyboard = [
        [InlineKeyboardButton("📱 Instagram 2FA", callback_data="insta")],
        [InlineKeyboardButton("📘 Facebook", callback_data="fb")],
        [InlineKeyboardButton("❌ Cancel", callback_data="main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ==================== START COMMAND ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Welcome {user.first_name}!\n\n"
        "📌 This bot helps you earn money by doing simple tasks.\n"
        "✅ Click the button below to start:",
        reply_markup=get_main_menu()
    )

# ==================== BUTTON HANDLER ====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # === Main Menu ===
    if data == "main":
        await query.edit_message_text(
            "🏠 Main Menu\n\nWhat would you like to do?",
            reply_markup=get_main_menu()
        )
        return

    # === Task Menu ===
    if data == "task":
        await query.edit_message_text(
            "📋 Select Task Type:\n\nWhich task would you like to do?",
            reply_markup=get_task_menu()
        )
        return

    # === Instagram Task ===
    if data == "insta":
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
            [InlineKeyboardButton("❌ Cancel", callback_data="main")]
        ]
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # === Start Task - Generate Credentials ===
    if data == "start_task":
        keyboard = [
            [InlineKeyboardButton("🔐 Set 2FA", callback_data="set_2fa")],
            [InlineKeyboardButton("❌ Cancel", callback_data="main")]
        ]
        await query.edit_message_text(
            "✅ Account Created!\n\n"
            "👤 Username: insta_user_5829\n"
            "🔑 Password: P@ssW0rd#2024\n\n"
            "📌 Please login with these credentials and complete the registration.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # === Set 2FA ===
    if data == "set_2fa":
        await query.edit_message_text(
            "📱 Please enter your 2FA code from Google Authenticator:\n\n"
            "Example: 123456",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Done", callback_data="done_2fa")],
                [InlineKeyboardButton("❌ Cancel", callback_data="main")]
            ])
        )
        return

    # === Done 2FA ===
    if data == "done_2fa":
        await query.edit_message_text(
            "✅ Task Completed Successfully!\n\n"
            "⏳ Your task is under review. You will receive reward within 24 hours.\n\n"
            "💰 Reward: 50.00 BDT (Pending)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main")]
            ])
        )
        return

    # === Video Tutorial ===
    if data == "video":
        await query.edit_message_text(
            "🎥 Tutorial Video:\n\n"
            "https://www.youtube.com/watch?v=VIDEO_ID",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="insta")]
            ])
        )
        return

    # === Facebook Task (Coming Soon) ===
    if data == "fb":
        await query.edit_message_text(
            "📘 Facebook Task\n\n"
            "⏳ Coming soon! Stay tuned.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="task")]
            ])
        )
        return

    # === Balance ===
    if data == "balance":
        await query.edit_message_text(
            "💰 Your Balance\n\n"
            "📊 Total Balance: 150.00 BDT\n"
            "📈 Total Earned: 200.00 BDT\n"
            "⏳ Pending: 50.00 BDT",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main")]
            ])
        )
        return

    # === Withdraw ===
    if data == "withdraw":
        keyboard = [
            [InlineKeyboardButton("📱 Bkash", callback_data="bkash")],
            [InlineKeyboardButton("📱 Nagad", callback_data="nagad")],
            [InlineKeyboardButton("❌ Cancel", callback_data="main")]
        ]
        await query.edit_message_text(
            "💳 Withdraw Money\n\n"
            "💰 Your Balance: 150.00 BDT\n"
            "⚠️ Minimum Withdrawal: 50.00 BDT\n\n"
            "Select withdrawal method:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # === Bkash / Nagad ===
    if data in ["bkash", "nagad"]:
        method = "Bkash" if data == "bkash" else "Nagad"
        await query.edit_message_text(
            f"✅ Withdrawal Request Submitted!\n\n"
            f"📱 Method: {method}\n"
            f"📞 Number: 01XXXXXXXXX\n"
            f"💰 Amount: 100.00 BDT\n\n"
            f"⏳ Your request is pending. You will receive payment within 24 hours.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main")]
            ])
        )
        return

    # === Profile ===
    if data == "profile":
        await query.edit_message_text(
            "👤 Your Profile\n\n"
            "🆔 User ID: 123456789\n"
            "👤 Username: @yourusername\n"
            "📅 Joined: 2024-01-15\n"
            "💰 Balance: 150.00 BDT\n"
            "🏆 Total Tasks: 5\n"
            "✅ Completed: 3\n"
            "⏳ Pending: 2",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main")]
            ])
        )
        return

    # === Refer ===
    if data == "refer":
        await query.edit_message_text(
            "🔗 Referral Program\n\n"
            "💰 Earn 10% commission for life!\n\n"
            "Your referral link:\n"
            "`https://t.me/YourBot?start=ref_ABC123`\n\n"
            "📊 Your Stats:\n"
            "👥 Total Referrals: 5\n"
            "💰 Commission Earned: 75.00 BDT",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main")]
            ]),
            parse_mode="Markdown"
        )
        return

    # === Language ===
    if data == "language":
        keyboard = [
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
            [InlineKeyboardButton("🇧🇩 বাংলা", callback_data="lang_bn")]
        ]
        await query.edit_message_text(
            "🌐 Select Language / ভাষা নির্বাচন করুন:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # === Language Change ===
    if data in ["lang_en", "lang_bn"]:
        lang = "English" if data == "lang_en" else "বাংলা"
        await query.edit_message_text(
            f"✅ Language changed to {lang}!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main")]
            ])
        )
        return

# ==================== PERSISTENT MENU ====================
async def set_persistent_menu(app):
    commands = [
        BotCommand("start", "🚀 Start"),
        BotCommand("menu", "📋 Menu"),
        BotCommand("balance", "💰 Balance"),
        BotCommand("withdraw", "💳 Withdraw"),
        BotCommand("profile", "👤 Profile"),
        BotCommand("refer", "🔗 Refer"),
        BotCommand("language", "🌐 Language"),
    ]
    await app.bot.set_my_commands(commands)
    logger.info("✅ Persistent menu set!")

# ==================== COMMANDS ====================
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏠 Main Menu\n\nWhat would you like to do?",
        reply_markup=get_main_menu()
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 Your Balance\n\n📊 Total Balance: 150.00 BDT",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main")]
        ])
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
    app.add_handler(CommandHandler("balance", balance))
    
    # Button handler
    app.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
