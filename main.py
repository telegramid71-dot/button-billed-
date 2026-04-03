import asyncio

try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from pyrogram import Client, filters
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# আপনার দেওয়া তথ্যগুলো এখানে সেট করা হয়েছে
api_id = 33825820
api_hash = "cb8b1916f13fc014feeefe4910ae68b7"
bot_token = "8662371998:AAG67pyPYp6S8nKj5CgSBPfuj3cOoQJAo5Q"

# লগিং সেটআপ
logging.basicConfig(level=logging.INFO)

app = Client("my_button_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.channel)
async def add_button_to_post(client, message):
    try:
        # বাটন তৈরি
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔴 👀See Full Video👀", url="https://y.hn/kfvvd")]
        ])

        # মেসেজে বাটন এডিট করে বসিয়ে দেওয়া
        await message.edit_reply_markup(reply_markup=keyboard)
        print(f"Button added to message: {message.id}")
        
    except Exception as e:
        print(f"Error adding button: {e}")
        # অনেক সময় বট অ্যাডমিন না হলে বা পারমিশন না থাকলে এরর আসতে পারে

print("Bot is starting...")
app.run()
