import os
import json
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, 
    ContextTypes, filters
)
from telegram.error import RetryAfter, BadRequest

# Logging setup
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Railway.app এর Variables থেকে ডেটা লোড করা হচ্ছে
TOKEN = os.getenv("BOT_TOKEN")
ADMIN1_ID = int(os.getenv("ADMIN1_ID", 0))
ADMIN2_ID = int(os.getenv("ADMIN2_ID", 0))

SETTINGS_FILE = "settings.json"

# বটের স্ট্যাটাস ট্র্যাক করার জন্য
is_active = True

DEFAULT_SETTINGS = {"button1_url": "https://t.me/+dbZUQYaW0Is0OWY1", "button2_preset": 1}
PRESETS = {
    1: {"text": "💎BUY PAID GROUO💎", "url": "https://t.me/Erawat"},
    2: {"text": "🏆VIP GROUP MEMBERSHIP🏆", "url": "https://t.me/Monir1dj"}
}

def load_settings():
    if not os.path.exists(SETTINGS_FILE): return DEFAULT_SETTINGS
    with open(SETTINGS_FILE, "r") as f: return json.load(f)

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f: json.dump(settings, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_active
    uid = update.effective_user.id
    if uid in [ADMIN1_ID, ADMIN2_ID]:
        is_active = True
        if uid == ADMIN1_ID:
            kb = [[InlineKeyboardButton("Erawat Khan", callback_data="p1")], [InlineKeyboardButton("খুলা আকাশ", callback_data="p2")]]
            await update.message.reply_text("✅ বট চালু হয়েছে! কোন বাটন সেট করবেন?", reply_markup=InlineKeyboardMarkup(kb))
        else:
            context.user_data["ask_url"] = True
            await update.message.reply_text("✅ বট চালু হয়েছে! নতুন লিংকটি দিন:")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_active
    if update.effective_user.id in [ADMIN1_ID, ADMIN2_ID]:
        is_active = False
        await update.message.reply_text("🛑 বট থামানো হয়েছে!")

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN2_ID and context.user_data.get("ask_url"):
        s = load_settings()
        s["button1_url"] = update.message.text.strip()
        save_settings(s)
        context.user_data["ask_url"] = False
        await update.message.reply_text("লিংক সেভ হয়েছে ✅")

async def cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id == ADMIN1_ID:
        s = load_settings()
        s["button2_preset"] = 1 if query.data == "p1" else 2
        save_settings(s)
        await query.edit_message_text(f"বাটন {'এরাওয়াত' if query.data == 'p1' else 'খুলা আকাশ'} সেট হয়েছে ✅")

async def auto_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_active: return
    post = update.channel_post
    if not post: return

    # ১. একাধিক মিডিয়া (Album) স্কিপ করা
    if post.media_group_id: return

    # ২. ফরোয়ার্ড করা পোস্টের জন্য রেট লিমিট এড়ানো
    await asyncio.sleep(1)

    s = load_settings()
    b1 = InlineKeyboardButton("👀 See Full Info 👀", url=s["button1_url"])
    p = PRESETS[s["button2_preset"]]
    b2 = InlineKeyboardButton(p["text"], url=p["url"])
    markup = InlineKeyboardMarkup([[b1], [b2]])

    try:
        await context.bot.edit_message_reply_markup(
            chat_id=post.chat_id, message_id=post.message_id, reply_markup=markup
        )
    except RetryAfter as e:
        await asyncio.sleep(e.retry_after)
    except BadRequest as e:
        logger.info(f"Skipping: {e}")

def main():
    # টোকেন না থাকলে বট রান হবে না
    if not TOKEN:
        logger.error("BOT_TOKEN is missing in environment variables!")
        return

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CallbackQueryHandler(cb))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL & ~filters.COMMAND, auto_button))
    
    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
