from telethon import TelegramClient, events, Button
import logging

# আপনার তথ্যগুলো এখানে সেট করা আছে
api_id = 33825820
api_hash = 'cb8b1916f13fc014feeefe4910ae68b7'
bot_token = '8662371998:AAG67pyPYp6S8nKj5CgSBPfuj3cOoQJAo5Q'

# লগিং সেটআপ
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.INFO)

# ক্লায়েন্ট শুরু করা
bot = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

print("বটটি সফলভাবে চালু হয়েছে...")

@bot.on(events.NewMessage(incoming=True))
async def add_button(event):
    # শুধুমাত্র চ্যানেল বা গ্রুপে কাজ করবে
    if event.is_private:
        return

    try:
        # বাটনের টেক্সট এবং লিংক
        button_text = "#r 👀See Full Video👀"
        button_link = "https://y.hn/kfvvd"

        # মেসেজটি কপি করে বাটনসহ পাঠানো
        await bot.send_message(
            event.chat_id,
            event.message,
            buttons=Button.url(button_text, button_link)
        )

        # আসল মেসেজটি ডিলিট করে দেওয়া (যাতে ডাবল পোস্ট না দেখায়)
        await event.delete()

    except Exception as e:
        print(f"Error: {e}")

# বট চালু রাখা
bot.run_until_disconnected()
