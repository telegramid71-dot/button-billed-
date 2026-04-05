import os
import json
import logging
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

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TOKEN = "8661328825:AAFPMOEVhvIRbQrVbFbaZJ9M6UD1s37OCZA"
# Admin configurations
ADMIN1_ID = 5944842058
ADMIN2_ID = 6947301796

# Database / Settings File
SETTINGS_FILE = "settings.json"

# Default Settings
DEFAULT_SETTINGS = {
    "button1_url": "https://t.me/+dbZUQYaW0Is0OWY1",
    "button2_preset": 1  # 1 for Erawat, 2 for Khula Akash
}

# Button 2 Configurations
PRESET_1 = {
    "text": "💎BUY PAID GROUO💎",
    "url": "https://t.me/Erawat"
}
PRESET_2 = {
    "text": "🏆VIP GROUP MEMBERSHIP🏆",
    "url": "https://t.me/Monir1dj"
}

def load_settings():
    """Load settings from JSON file. Create if it doesn't exist."""
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)
        return DEFAULT_SETTINGS
    
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS

def save_settings(settings):
    """Save current settings to JSON file."""
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command for Admins."""
    user_id = update.effective_user.id

    if user_id == ADMIN1_ID:
        # Admin 1: Select Button 2 preset
        keyboard = [
            [InlineKeyboardButton("Erawat Khan", callback_data="preset_1")],
            [InlineKeyboardButton("খুলা আকাশ", callback_data="preset_2")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("আপনি কোন বাটান সেট করতে চান?", reply_markup=reply_markup)

    elif user_id == ADMIN2_ID:
        # Admin 2: Ask for new dynamic link
        context.user_data["waiting_for_url"] = True
        await update.message.reply_text("এখন আপনি কোন লিংক সেট করতে চান দয়া করে লিংক দিন!")
    
    else:
        # Unauthorized users
        await update.message.reply_text("You are not authorized to use this bot.")


async def handle_admin2_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Admin 2 sending a new URL."""
    user_id = update.effective_user.id
    
    if user_id == ADMIN2_ID and context.user_data.get("waiting_for_url"):
        new_url = update.message.text.strip()
        
        # Save to settings
        settings = load_settings()
        settings["button1_url"] = new_url
        save_settings(settings)
        
        # Reset state and confirm
        context.user_data["waiting_for_url"] = False
        await update.message.reply_text("আপনার লিংক পরিবর্তন সম্পন্ন হয়েছে ✅")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button clicks from Admin 1."""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN1_ID:
        await query.answer("Unauthorized!", show_alert=True)
        return

    await query.answer()
    
    settings = load_settings()
    
    if query.data == "preset_1":
        settings["button2_preset"] = 1
        save_settings(settings)
        await query.edit_message_text("সেট এরাওয়াত খান বাটান ✅")
        
    elif query.data == "preset_2":
        settings["button2_preset"] = 2
        save_settings(settings)
        await query.edit_message_text("সেট খুলা আকাশ বাটান ✅")


async def process_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Automatically attach buttons to every new channel post."""
    post = update.channel_post
    if not post:
        return

    settings = load_settings()
    
    # Button 1 Construction (Dynamic URL)
    btn1 = InlineKeyboardButton(
        text="👀 See Full Info 👀", 
        url=settings["button1_url"]
    )
    
    # Button 2 Construction (Preset based on Admin 1)
    if settings["button2_preset"] == 1:
        btn2 = InlineKeyboardButton(text=PRESET_1["text"], url=PRESET_1["url"])
    else:
        btn2 = InlineKeyboardButton(text=PRESET_2["text"], url=PRESET_2["url"])

    # Separate lines for buttons
    reply_markup = InlineKeyboardMarkup([[btn1], [btn2]])

    try:
        await context.bot.edit_message_reply_markup(
            chat_id=post.chat_id,
            message_id=post.message_id,
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Failed to add buttons to channel post: {e}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log the error and notify Admin 1."""
    logger.error(f"Update {update} caused error {context.error}")
    
    error_msg = f"⚠️ Bot Error Occurred:\n\n`{context.error}`"
    try:
        # Notify Admin 1
        await context.bot.send_message(chat_id=ADMIN1_ID, text=error_msg, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Failed to send error message to Admin 1: {e}")


def main():
    """Start the bot."""
    if not TOKEN:
        logger.error("BOT_TOKEN is missing! Check your .env file.")
        return

    # Initialize Bot Application
    application = Application.builder().token(TOKEN).build()

    # Admin Handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin2_url))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Channel Post Handler (Triggers on any new post type: text, photo, video, etc.)
    application.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, process_channel_post))

    # Error Handler
    application.add_error_handler(error_handler)

    # Start Polling
    logger.info("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
