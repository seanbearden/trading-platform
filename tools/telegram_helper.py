from telegram import Bot
from telegram.error import NetworkError


async def send_alert(bot_token, chat_id, message):
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=message)


async def send_png(bot_token, chat_id, image_path):
    try:
        bot = Bot(token=bot_token)
        with open(image_path, 'rb') as image_file:
            await bot.send_photo(chat_id=chat_id, photo=image_file)
        return None
    except NetworkError as e:
        return f"An error occurred: {e}"
