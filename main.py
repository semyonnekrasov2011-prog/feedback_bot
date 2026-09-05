import os
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CARD_NUMBER = os.getenv("CARD_NUMBER")

MY_ID = 7507779053

PAYMENT_LINK = "https://t.me/+QE_CXnNiHkE4OTMy"
PRICE_RUB = 350

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Сообщение у администратора -> ID пользователя
message_map = {}


def payment_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⭐ Перейти по ссылке",
                    url=PAYMENT_LINK
                )
            ],
            [
                InlineKeyboardButton(
                    text="💳 Оплатить рублями",
                    callback_data="rub_payment"
                )
            ]
        ]
    )


# =========================
# START
# =========================

@dp.message(CommandStart())
async def start(message: Message):

    await message.answer(
        "👋 Добро пожаловать!\n\n"
        "Выберите удобный способ оплаты:",
        reply_markup=payment_keyboard()
    )


# =========================
# ОПЛАТА РУБЛЯМИ
# =========================

@dp.callback_query(F.data == "rub_payment")
async def rub_payment(callback):

    if not CARD_NUMBER:
        await callback.answer(
            "Способ оплаты временно недоступен. Уточните как оплатить, вам ответят в ближайшее время",
            show_alert=True
        )
        return

    await callback.message.answer(
        f"💳 Оплата рублями\n\n"
        f"Стоимость: {PRICE_RUB} ₽\n\n"
        f"Переведите ровно {PRICE_RUB} ₽ по номеру карты:\n\n"
        f"<code>{CARD_NUMBER}</code>\n\n"
        "После оплаты отправьте чек прямо сюда.\n"
        "После проверки вам будет предоставлен оплаченный товар.",
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# ТВОИ СООБЩЕНИЯ
# =========================

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
            f"❌ Не удалось отправить сообщение:\n{e}"
        )


# =========================
# СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЕЙ
# =========================

@dp.message(F.from_user.id != MY_ID)
async def user_message(message: Message):

    try:
        forwarded = await bot.forward_message(
            chat_id=MY_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )

        message_map[forwarded.message_id] = (
            message.from_user.id
        )

    except Exception as e:
        print(f"Ошибка пересылки: {e}")


# =========================
# ЗАПУСК
# =========================

async def main():

    if not BOT_TOKEN:
        raise ValueError(
            "BOT_TOKEN не найден в Railway Variables"
        )

    print("🤖 Бот запущен!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())