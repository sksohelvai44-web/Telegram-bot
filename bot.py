import os
import logging
import sqlite3
import random
import string
import pyotp
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS = [123456789]  # 👈 আপনার টেলিগ্রাম আইডি দিন

if not TOKEN:
    logger.error("BOT_TOKEN not set!")
    exit(1)

# ==================== DATABASE ====================
class Database:
    def __init__(self):
        self.conn = sqlite3.connect("taskly.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        # Users Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                balance REAL DEFAULT 0,
                total_earned REAL DEFAULT 0,
                referral_code TEXT UNIQUE,
                referred_by INTEGER,
                referral_earnings REAL DEFAULT 0,
                language TEXT DEFAULT 'bn',
                is_banned INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0
            )
        ''')
        
        # Instagram Tasks Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS instagram_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                password TEXT,
                twofa_key TEXT,
                authenticator_code TEXT,
                status TEXT DEFAULT 'pending',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                reward REAL DEFAULT 4.00,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Withdrawals Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS withdrawals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                method TEXT,
                account_number TEXT,
                status TEXT DEFAULT 'pending',
                requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Referrals Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER,
                commission REAL DEFAULT 0,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referrer_id) REFERENCES users (id),
                FOREIGN KEY (referred_id) REFERENCES users (id)
            )
        ''')
        
        self.conn.commit()
    
    def get_user(self, telegram_id):
        self.cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        return self.cursor.fetchone()
    
    def create_user(self, telegram_id, username, first_name, referred_by=None):
        referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        is_admin = 1 if telegram_id in ADMIN_IDS else 0
        self.cursor.execute('''
            INSERT INTO users (telegram_id, username, first_name, referral_code, referred_by, is_admin)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (telegram_id, username, first_name, referral_code, referred_by, is_admin))
        self.conn.commit()
        return self.get_user(telegram_id)
    
    def get_user_by_referral(self, referral_code):
        self.cursor.execute("SELECT telegram_id FROM users WHERE referral_code = ?", (referral_code,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def add_balance(self, user_id, amount):
        self.cursor.execute('''
            UPDATE users SET balance = balance + ?, total_earned = total_earned + ?
            WHERE id = ?
        ''', (amount, amount, user_id))
        self.conn.commit()
    
    def deduct_balance(self, user_id, amount):
        self.cursor.execute('''
            UPDATE users SET balance = balance - ?
            WHERE id = ? AND balance >= ?
        ''', (amount, user_id, amount))
        self.conn.commit()
    
    def create_instagram_task(self, user_id, username, password):
        self.cursor.execute('''
            INSERT INTO instagram_tasks (user_id, username, password, status, reward)
            VALUES (?, ?, ?, 'pending', 4.00)
        ''', (user_id, username, password))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_instagram_task(self, task_id, status, twofa_key=None, authenticator_code=None):
        self.cursor.execute('''
            UPDATE instagram_tasks 
            SET status = ?, twofa_key = ?, authenticator_code = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, twofa_key, authenticator_code, task_id))
        self.conn.commit()
    
    def create_withdrawal(self, user_id, amount, method, account_number):
        self.cursor.execute('''
            INSERT INTO withdrawals (user_id, amount, method, account_number, status)
            VALUES (?, ?, ?, ?, 'pending')
        ''', (user_id, amount, method, account_number))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_pending_withdrawals(self):
        self.cursor.execute('''
            SELECT w.*, u.username, u.first_name 
            FROM withdrawals w
            JOIN users u ON w.user_id = u.id
            WHERE w.status = 'pending'
            ORDER BY w.requested_at ASC
        ''')
        return self.cursor.fetchall()
    
    def update_withdrawal_status(self, withdrawal_id, status):
        self.cursor.execute('''
            UPDATE withdrawals SET status = ?, approved_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, withdrawal_id))
        self.conn.commit()
    
    def get_all_users(self):
        self.cursor.execute("SELECT * FROM users ORDER BY id DESC")
        return self.cursor.fetchall()
    
    def get_all_tasks(self):
        self.cursor.execute('''
            SELECT t.*, u.username, u.first_name 
            FROM instagram_tasks t
            JOIN users u ON t.user_id = u.id
            ORDER BY t.id DESC
        ''')
        return self.cursor.fetchall()
    
    def get_user_tasks(self, user_id):
        self.cursor.execute("SELECT * FROM instagram_tasks WHERE user_id = ? ORDER BY id DESC", (user_id,))
        return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()

db = Database()

# ==================== KEYBOARDS ====================

def get_main_keyboard():
    keyboard = [
        [KeyboardButton("📋 Task"), KeyboardButton("💰 Balance")],
        [KeyboardButton("💳 Withdraw"), KeyboardButton("👤 Profile")],
        [KeyboardButton("🔗 Refer"), KeyboardButton("🌐 Language")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_task_keyboard():
    keyboard = [
        [KeyboardButton("📱 Insta 2FA 4 BDT"), KeyboardButton("📘 Facebook")],
        [KeyboardButton("❌ Cancel")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_instagram_keyboard():
    keyboard = [
        [KeyboardButton("✅ Start"), KeyboardButton("🎥 Video")],
        [KeyboardButton("❌ Cancel")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_instagram_actions():
    keyboard = [
        [KeyboardButton("🔐 Set 2FA")],
        [KeyboardButton("❌ Cancel")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_done_keyboard():
    keyboard = [
        [KeyboardButton("✅ Done")],
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
    keyboard = [[KeyboardButton("❌ Cancel")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_admin_keyboard():
    keyboard = [
        [KeyboardButton("👥 All Users"), KeyboardButton("📋 All Tasks")],
        [KeyboardButton("💳 Pending Withdrawals"), KeyboardButton("📊 Stats")],
        [KeyboardButton("❌ Cancel")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

# ==================== GENERATE CREDENTIALS ====================

def generate_credentials():
    username = "insta_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    password = "P@ss" + ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return username, password

def generate_authenticator_code(key):
    try:
        totp = pyotp.TOTP(key)
        return totp.now()
    except:
        return None

# ==================== USER STATES ====================

user_states = {}
withdraw_states = {}

# ==================== COMMAND HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    telegram_id = user.id
    username = user.username or "NoUsername"
    first_name = user.first_name or "User"
    
    db_user = db.get_user(telegram_id)
    
    # Check if referred by someone
    referred_by = None
    if context.args and context.args[0].startswith('ref_'):
        ref_code = context.args[0]
        referrer_id = db.get_user_by_referral(ref_code)
        if referrer_id and referrer_id != telegram_id:
            referred_by = referrer_id
    
    if not db_user:
        db.create_user(telegram_id, username, first_name, referred_by)
    
    db_user = db.get_user(telegram_id)
    
    # Show admin menu if admin
    if db_user and db_user[10] == 1:
        await update.message.reply_text(
            f"👋 Welcome Admin {first_name}!",
            reply_markup=get_admin_keyboard()
        )
    else:
        await update.message.reply_text(
            f"👋 Welcome {first_name}!\n\n"
            "📌 This bot helps you earn money by doing simple tasks.",
            reply_markup=get_main_keyboard()
        )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_user = db.get_user(update.effective_user.id)
    if db_user and db_user[10] == 1:
        await update.message.reply_text("🏠 Admin Panel", reply_markup=get_admin_keyboard())
    else:
        await update.message.reply_text("🏠 Main Menu", reply_markup=get_main_keyboard())

# ==================== MESSAGE HANDLER ====================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    db_user = db.get_user(user_id)
    
    if not db_user:
        await start(update, context)
        return
    
    # ========== CANCEL ==========
    if text == "❌ Cancel":
        user_states.pop(user_id, None)
        withdraw_states.pop(user_id, None)
        if db_user[10] == 1:
            await update.message.reply_text("❌ Cancelled!", reply_markup=get_admin_keyboard())
        else:
            await update.message.reply_text("❌ Cancelled!", reply_markup=get_main_keyboard())
        return
    
    # ========== ADMIN PANEL ==========
    if db_user and db_user[10] == 1:
        if text == "👥 All Users":
            users = db.get_all_users()
            msg = "👥 **All Users:**\n\n"
            for u in users[:30]:
                msg += f"🆔 `{u[1]}` | @{u[2] or 'N/A'} | Balance: {u[3]:.2f} BDT\n"
            if len(users) > 30:
                msg += f"\n... and {len(users)-30} more"
            await update.message.reply_text(msg, reply_markup=get_admin_keyboard(), parse_mode="Markdown")
            return
        
        elif text == "📋 All Tasks":
            tasks = db.get_all_tasks()
            if tasks:
                msg = "📋 **All Tasks:**\n\n"
                for t in tasks[:20]:
                    msg += f"ID: {t[0]} | User: @{t[9]} | Status: {t[6]} | Reward: {t[7]:.2f} BDT\n"
                if len(tasks) > 20:
                    msg += f"\n... and {len(tasks)-20} more"
                await update.message.reply_text(msg, reply_markup=get_admin_keyboard(), parse_mode="Markdown")
            else:
                await update.message.reply_text("No tasks found.", reply_markup=get_admin_keyboard())
            return
        
        elif text == "💳 Pending Withdrawals":
            pending = db.get_pending_withdrawals()
            if pending:
                msg = "💳 **Pending Withdrawals:**\n\n"
                for w in pending:
                    msg += f"ID: {w[0]} | User: @{w[8]} | Amount: {w[2]:.2f} BDT | Method: {w[3]}\n"
                await update.message.reply_text(msg, reply_markup=get_admin_keyboard(), parse_mode="Markdown")
            else:
                await update.message.reply_text("No pending withdrawals.", reply_markup=get_admin_keyboard())
            return
        
        elif text == "📊 Stats":
            db.cursor.execute("SELECT COUNT(*) FROM users")
            total_users = db.cursor.fetchone()[0]
            db.cursor.execute("SELECT SUM(balance) FROM users")
            total_balance = db.cursor.fetchone()[0] or 0
            db.cursor.execute("SELECT COUNT(*) FROM withdrawals WHERE status = 'pending'")
            pending_withdraw = db.cursor.fetchone()[0]
            db.cursor.execute("SELECT COUNT(*) FROM instagram_tasks WHERE status = 'pending'")
            pending_tasks = db.cursor.fetchone()[0]
            
            await update.message.reply_text(
                f"📊 **Bot Statistics:**\n\n"
                f"👥 Total Users: {total_users}\n"
                f"💰 Total Balance: {total_balance:.2f} BDT\n"
                f"⏳ Pending Tasks: {pending_tasks}\n"
                f"⏳ Pending Withdrawals: {pending_withdraw}",
                reply_markup=get_admin_keyboard(),
                parse_mode="Markdown"
            )
            return
    
    # ========== MAIN MENU (All Users) ==========
    
    # === TASK ===
    if text == "📋 Task":
        await update.message.reply_text("📋 Select Task Type:", reply_markup=get_task_keyboard())
        return
    
    # === BALANCE ===
    elif text == "💰 Balance":
        await update.message.reply_text(
            f"💰 **Your Balance**\n\n"
            f"📊 Total Balance: {db_user[3]:.2f} BDT\n"
            f"📈 Total Earned: {db_user[4]:.2f} BDT\n"
            f"🔗 Referral Earnings: {db_user[8]:.2f} BDT",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    # === WITHDRAW ===
    elif text == "💳 Withdraw":
        if db_user[3] < 50:
            await update.message.reply_text(
                f"❌ Insufficient balance!\n\n💰 Your Balance: {db_user[3]:.2f} BDT\n⚠️ Minimum: 50.00 BDT",
                reply_markup=get_main_keyboard()
            )
            return
        await update.message.reply_text(
            f"💳 **Withdraw Money**\n\n💰 Your Balance: {db_user[3]:.2f} BDT\n⚠️ Minimum: 50.00 BDT",
            reply_markup=get_withdraw_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    # === PROFILE ===
    elif text == "👤 Profile":
        await update.message.reply_text(
            f"👤 **Your Profile**\n\n"
            f"🆔 ID: `{user_id}`\n"
            f"👤 Username: @{db_user[1] or 'N/A'}\n"
            f"📅 Joined: {db_user[2][:10] if db_user[2] else 'N/A'}\n"
            f"💰 Balance: {db_user[3]:.2f} BDT\n"
            f"🏆 Total Earned: {db_user[4]:.2f} BDT\n"
            f"🔗 Referral Code: `{db_user[6]}`",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    # === REFER ===
    elif text == "🔗 Refer":
        await update.message.reply_text(
            f"🔗 **Referral Program**\n\n"
            "💰 Earn 10% commission for life!\n\n"
            f"Your referral link:\n"
            f"`https://t.me/{context.bot.username}?start=ref_{db_user[6]}`\n\n"
            f"📊 Commission Earned: {db_user[8]:.2f} BDT",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    # === LANGUAGE ===
    elif text == "🌐 Language":
        await update.message.reply_text("🌐 Select Language:", reply_markup=get_language_keyboard())
        return
    
    # ========== TASK MENU ==========
    
    # === INSTA 2FA (নতুন নাম) ===
    elif text == "📱 Insta 2FA 4 BDT":
        user_states[user_id] = {'task': 'instagram'}
        await update.message.reply_text(
            "⏳ Review time: 24 h\n\n"
            "📋 Task: 📱 Create Inst (2FA)\n\n"
            "📄 Description: In this task, you must create a new Inst acc using only a real mobile device.\n"
            "🔐 REQUIRED!\n"
            "You must use the information provided by the Telegram bot to register.\n\n"
            "❗If you use your own information, your application will be REJECTED without verification.\n\n"
            "💰 **Reward: 4.00 BDT**\n\n"
            "After registration:\n"
            "👉 No need to send any info\n"
            "✅ Just click the 'Account Registered' button\n\n"
            "⏳ Review time: 24 h",
            reply_markup=get_instagram_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    # === FACEBOOK ===
    elif text == "📘 Facebook":
        await update.message.reply_text("📘 Facebook Task\n\n⏳ Coming soon!", reply_markup=get_task_keyboard())
        return
    
    # ========== INSTAGRAM TASK FLOW ==========
    
    # === START ===
    elif text == "✅ Start" and user_id in user_states and user_states[user_id].get('task') == 'instagram':
        username, password = generate_credentials()
        task_id = db.create_instagram_task(db_user[0], username, password)
        user_states[user_id]['task_id'] = task_id
        user_states[user_id]['username'] = username
        user_states[user_id]['step'] = 'credentials'
        
        await update.message.reply_text(
            f"✅ **Account Created!**\n\n"
            f"👤 Username: `{username}`\n"
            f"🔑 Password: `{password}`\n\n"
            "📌 Please login with these credentials and complete the registration.",
            reply_markup=get_instagram_actions(),
            parse_mode="Markdown"
        )
        return
    
    # === VIDEO ===
    elif text == "🎥 Video" and user_id in user_states and user_states[user_id].get('task') == 'instagram':
        await update.message.reply_text(
            "🎥 Tutorial Video:\n\nhttps://www.youtube.com/watch?v=dQw4w9WgXcQ",
            reply_markup=get_instagram_keyboard()
        )
        return
    
    # === SET 2FA ===
    elif text == "🔐 Set 2FA":
        if user_id in user_states and user_states[user_id].get('step') == 'credentials':
            user_states[user_id]['step'] = 'waiting_2fa_key'
            await update.message.reply_text(
                "📱 **Enter your 2FA Secret Key:**\n\n"
                "This is the key you get when setting up 2FA in Instagram.\n"
                "Example: `JBSWY3DPEHPK3PXP`\n\n"
                "_(Send the key)_",
                reply_markup=get_cancel_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ No active task!", reply_markup=get_main_keyboard())
        return
    
    # === HANDLE 2FA KEY ===
    elif user_id in user_states and user_states[user_id].get('step') == 'waiting_2fa_key':
        user_2fa_key = text.strip().upper()
        
        try:
            authenticator_code = generate_authenticator_code(user_2fa_key)
            if authenticator_code:
                task_id = user_states[user_id]['task_id']
                db.update_instagram_task(task_id, 'pending', user_2fa_key, authenticator_code)
                user_states[user_id]['step'] = 'done'
                
                await update.message.reply_text(
                    f"✅ **2FA Key Received!**\n\n"
                    f"🔄 Generating verification code...\n\n"
                    f"✅ **Your Instagram 2FA verification code is:**\n"
                    f"`{authenticator_code}`\n\n"
                    "📌 Please enter this code in your Instagram app.\n\n"
                    "Click **Done** when finished:",
                    reply_markup=get_done_keyboard(),
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    "❌ Invalid 2FA Key! Please check and try again.",
                    reply_markup=get_cancel_keyboard()
                )
        except Exception as e:
            await update.message.reply_text(
                f"❌ Error: {str(e)}\nPlease check your 2FA key.",
                reply_markup=get_cancel_keyboard()
            )
        return
    
    # === DONE ===
    elif text == "✅ Done":
        if user_id in user_states and user_states[user_id].get('step') == 'done':
            task_id = user_states[user_id]['task_id']
            db.update_instagram_task(task_id, 'completed')
            db.add_balance(db_user[0], 4.00)
            
            if db_user[5]:
                db.add_balance(db_user[5], 0.40)
            
            user_states.pop(user_id, None)
            
            await update.message.reply_text(
                "✅ **Task Completed Successfully!**\n\n"
                "⏳ Your task is under review. You will receive reward within 24 hours.\n\n"
                "💰 Reward: 4.00 BDT",
                reply_markup=get_main_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ No active task!", reply_markup=get_main_keyboard())
        return
    
    # ========== WITHDRAW ==========
    
    # === BKASH ===
    elif text == "📱 Bkash":
        withdraw_states[user_id] = {'method': 'Bkash', 'step': 'number'}
        await update.message.reply_text(
            "📱 Enter your Bkash number:\nExample: 01XXXXXXXXX",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    # === NAGAD ===
    elif text == "📱 Nagad":
        withdraw_states[user_id] = {'method': 'Nagad', 'step': 'number'}
        await update.message.reply_text(
            "📱 Enter your Nagad number:\nExample: 01XXXXXXXXX",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    # === HANDLE WITHDRAW NUMBER ===
    elif user_id in withdraw_states and withdraw_states[user_id].get('step') == 'number':
        if text.isdigit() and len(text) == 11:
            withdraw_states[user_id]['number'] = text
            withdraw_states[user_id]['step'] = 'amount'
            await update.message.reply_text(
                f"💰 **How much to withdraw?**\n\n"
                f"📱 Method: {withdraw_states[user_id]['method']}\n"
                f"📞 Number: {text}\n\n"
                f"⚠️ Minimum: 50.00 BDT\n"
                f"💰 Your Balance: {db_user[3]:.2f} BDT",
                reply_markup=get_cancel_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "❌ Invalid number! Enter 11 digits.\nExample: 01XXXXXXXXX",
                reply_markup=get_cancel_keyboard()
            )
        return
    
    # === HANDLE WITHDRAW AMOUNT ===
    elif user_id in withdraw_states and withdraw_states[user_id].get('step') == 'amount':
        try:
            amount = float(text)
            if amount < 50:
                await update.message.reply_text(f"❌ Minimum 50.00 BDT!", reply_markup=get_cancel_keyboard())
                return
            if amount > db_user[3]:
                await update.message.reply_text(f"❌ Insufficient balance!", reply_markup=get_cancel_keyboard())
                return
            
            method = withdraw_states[user_id]['method']
            number = withdraw_states[user_id]['number']
            db.create_withdrawal(db_user[0], amount, method, number)
            db.deduct_balance(db_user[0], amount)
            withdraw_states.pop(user_id, None)
            
            await update.message.reply_text(
                f"✅ **Withdrawal Request Submitted!**\n\n"
                f"📱 Method: {method}\n"
                f"📞 Number: {number}\n"
                f"💰 Amount: {amount:.2f} BDT\n\n"
                f"⏳ Pending approval.",
                reply_markup=get_main_keyboard(),
                parse_mode="Markdown"
            )
        except ValueError:
            await update.message.reply_text("❌ Enter a valid number!", reply_markup=get_cancel_keyboard())
        return
    
    # ========== LANGUAGE ==========
    elif text == "🇬🇧 English":
        db.cursor.execute("UPDATE users SET language = 'en' WHERE telegram_id = ?", (user_id,))
        db.conn.commit()
        await update.message.reply_text("✅ Language changed to English!", reply_markup=get_main_keyboard())
        return
    
    elif text == "🇧🇩 বাংলা":
        db.cursor.execute("UPDATE users SET language = 'bn' WHERE telegram_id = ?", (user_id,))
        db.conn.commit()
        await update.message.reply_text("✅ ভাষা পরিবর্তন করে বাংলা করা হয়েছে!", reply_markup=get_main_keyboard())
        return
    
    # ========== UNKNOWN ==========
    else:
        await update.message.reply_text("❌ Unknown command! Please use the buttons below.", reply_markup=get_main_keyboard())

# ==================== PERSISTENT MENU ====================

async def set_persistent_menu(app):
    commands = [
        BotCommand("start", "🚀 Start"),
        BotCommand("menu", "📋 Menu"),
    ]
    await app.bot.set_my_commands(commands)
    logger.info("✅ Persistent menu set!")

# ==================== MAIN ====================

def main():
    logger.info("Starting bot...")
    
    app = Application.builder().token(TOKEN).build()
    
    app.post_init = set_persistent_menu
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
