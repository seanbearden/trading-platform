from telegram import Bot


async def send_alert(bot_token, user_id, message):
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=user_id, text=message)