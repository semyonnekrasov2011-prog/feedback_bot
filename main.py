import os
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

BOT_TOKEN = os.getenv("BOT_TOKEN")
MY_ID = 7507779053

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# message_id сообщения у админа -> Telegram ID пользователя
message_map = {}


# =========================
# ТВОИ СООБЩЕНИЯ
# =========================

@dp.message(F.from_user.id == MY_ID)
async def admin_message(message: Message):

    # Отвечаем только если это Reply
    if not message.reply_to_message:
        return

    # Ищем, кому принадлежит сообщение,
    # на которое ты отвечаешь
    user_id = message_map.get(
        message.reply_to_message.message_id
    )

    if not user_id:
        await message.answer(
            "❌ Не удалось определить пользователя.\n"
            "Возможно, бот был перезапущен."
        )
        return

    try:
        # Копируем твоё сообщение пользователю
        await bot.copy_message(
            chat_id=user_id,
            from_chat_id=MY_ID,
            message_id=message.message_id
        )

    except Exception as e:
        await message.answer(
            f"❌ Не удалось отправить сообщение:\n{e}"
        )


# =========================
# СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЕЙ
# =========================

@dp.message(F.from_user.id != MY_ID)
async def user_message(message: Message):

    try:
        # Пересылаем сообщение тебе
        forwarded = await bot.forward_message(
            chat_id=MY_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )

        # Запоминаем связь:
        #
        # сообщение у тебя
        #        ↓
        # Telegram ID пользователя
        #
        message_map[forwarded.message_id] = message.from_user.id

    except Exception as e:
        print(f"Ошибка пересылки: {e}")


# =========================
# ЗАПУСК
# =========================

async def main():
    print("🤖 Бот запущен!")
    print(f"👤 Администратор: {MY_ID}")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())