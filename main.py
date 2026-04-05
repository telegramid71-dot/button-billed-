import os
import json
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from telegram.error import RetryAfter, TelegramError

# Logging setup
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = "8661328825:AAFrlTkK3T1G925EYnTzjmtSdM5itGUDEXc"

ADMIN1_ID = 5944842058
ADMIN2_ID = 6947301796
SETTINGS_FILE = "settings.json"

# Default values
DEFAULT_SETTINGS = {"button1_url": "https://t.me/+dbZUQYaW0Is0OWY1", "button2_preset": 1}
PRESETS = {
    1: {"text": "💎BUY PAID GROUO💎", "url": "https://t.me/Erawat"},
    2: {"text": "🏆VIP GROUP MEMBERSHIP🏆", "url": "https://t.me/Monir1dj"}
}

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS
    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid == ADMIN1_ID:
        kb = [[InlineKeyboardButton("Erawat Khan", callback_data="p1")], [InlineKeyboardButton("খুলা আকাশ", callback_data="p2")]]
        await update.message.reply_text("কোন বাটন সেট করবেন?", reply_markup=InlineKeyboardMarkup(kb))
    elif uid == ADMIN2_ID:
        context.user_data["ask_url"] = True
        await update.message.reply_text("নতুন লিংকটি দিন:")

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN2_ID and context.user_data.get("ask_url"):
        s = load_settings()
        s["button1_url"] = update.message.text.strip()
        save_settings(s)
        context.user_data["ask_url"] = False
        await update.message.reply_text("লিংক সেভ হয়েছে ✅")

async def cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id == ADMIN1_ID:
        s = load_settings()
        s["button2_preset"] = 1 if query.data == "p1" else 2
        save_settings(s)
        await query.edit_message_text(f"বাটন {'এরাওয়াত' if query.data == 'p1' else 'খুলা আকাশ'} সেট হয়েছে ✅")

async def auto_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """এটি প্রতিটি পোস্টের জন্য আলাদা টাস্ক হিসেবে কাজ করবে (Fast Response)"""
    post = update.channel_post
    s = load_settings()
    
    # বাটন তৈরি
    b1 = InlineKeyboardButton("👀 See Full Info 👀", url=s["button1_url"])
    p = PRESETS[s["button2_preset"]]
    b2 = InlineKeyboardButton(p["text"], url=p["url"])
    markup = InlineKeyboardMarkup([[b1], [b2]])

    # চেষ্টা করবে বাটন লাগাতে, যদি ফ্ল্যাড কন্ট্রোল (Rate limit) থাকে তবে ওয়েট করবে
    for attempt in range(3): 
        try:
            await context.bot.edit_message_reply_markup(
                chat_id=post.chat_id,
                message_id=post.message_id,
                reply_markup=markup
            )
            break 
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except TelegramError as e:
            logger.error(f"Error: {e}")
            break

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(cb))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
    # সকল চ্যানেলের পোস্ট ধরার জন্য ফিল্টার
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL, auto_button), group=1)
    
    print("Bot started...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
