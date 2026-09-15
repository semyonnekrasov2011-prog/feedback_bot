
import os
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


# ==========================================
# НАСТРОЙКИ
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Твой Telegram ID
MY_ID = 7507779053

# Специальная ссылка Telegram для оплаты Stars
STARS_PAYMENT_LINK = "https://t.me/+iRWfFkCKvqI3NWQy"

# Оплата рублями через Tribute
RUB_PAYMENT_LINK = "https://t.me/tribute/app?startapp=s15qD"


# ==========================================
# ЗАПУСК БОТА
# ==========================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# message_id сообщения бота админу -> user_id пользователя
message_map = {}


# ==========================================
# КНОПКИ ОПЛАТЫ
# ==========================================

def payment_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⭐ Оплатить Stars",
                    url=STARS_PAYMENT_LINK
                )
            ],
            [
                InlineKeyboardButton(
                    text="💳 Оплатить рублями",
                    url=RUB_PAYMENT_LINK
                )
            ]
        ]
    )


# ==========================================
# /START
# ==========================================

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 Добро пожаловать!\n\n"
        "Выберите удобный способ оплаты:\n\n"
        "⭐ Оплата через Telegram Stars\n"
        "💳 Оплата рублями через Tribute\n\n"
        "По каким-либо вопросам можете писать прямо в бота, "
        "вам ответят в ближайшее время.",
        reply_markup=payment_keyboard()
    )


# ==========================================
# ОТВЕТЫ АДМИНА ПОЛЬЗОВАТЕЛЯМ
# ==========================================

@dp.message(F.from_user.id == MY_ID)
async def admin_message(message: Message):

    if not message.reply_to_message:
        return

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
        await bot.copy_message(
            chat_id=user_id,
            from_chat_id=MY_ID,
            message_id=message.message_id
        )

    except Exception as e:
        await message.answer(
            f"❌ Ошибка отправки:\n{e}"
        )


# ==========================================
# СООБЩЕНИЯ ОТ ПОЛЬЗОВАТЕЛЕЙ
# ==========================================

@dp.message(F.from_user.id != MY_ID)
async def user_message(message: Message):

    try:
        forwarded = await bot.forward_message(
            chat_id=MY_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )

        message_map[forwarded.message_id] = message.from_user.id

    except Exception as e:
        print(
            f"Ошибка пересылки сообщения: {e}"
        )


# ==========================================
# ЗАПУСК
# ==========================================

async def main():

    if not BOT_TOKEN:
        raise ValueError(
            "BOT_TOKEN не найден! "
            "Добавь его в Railway Variables."
        )

    print("🤖 Бот успешно запущен!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())