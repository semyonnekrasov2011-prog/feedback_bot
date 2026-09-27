import os
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    LabeledPrice,
    PreCheckoutQuery,
)


# ==========================================
# НАСТРОЙКИ
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Твой Telegram ID
MY_ID = 7507779053

# Номер карты для оплаты рублями
CARD_NUMBER = "2202208888777241"

# Цена в Telegram Stars
STAR_PRICE = 250


# ==========================================
# БОТ
# ==========================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ==========================================
# КАРТА:
# сообщение админа -> ID пользователя
# ==========================================

message_map = {}


# ==========================================
# КНОПКИ ОПЛАТЫ
# ==========================================

def payment_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"⭐ Оплатить — {STAR_PRICE} Stars",
                    callback_data="pay_stars"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💳 Оплатить рублями",
                    callback_data="pay_rub"
                )
            ]
        ]
    )


# ==========================================
# /START
# ==========================================

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "👋 Добро пожаловать!\n\n"
        "Выберите удобный способ оплаты:\n\n"
        "⭐ Оплата через Telegram Stars\n"
        "💳 Оплата рублями\n\n"
        "По каким-либо вопросам можете писать прямо в бота, "
        "вам ответят в ближайшее время.",
        reply_markup=payment_keyboard()
    )


# ==========================================
# ОПЛАТА РУБЛЯМИ
# ==========================================

@dp.callback_query(F.data == "pay_rub")
async def pay_rub_handler(callback: CallbackQuery):

    await callback.message.answer(
        "💳 Оплата рублями\n\n"
        f"Номер карты:\n{CARD_NUMBER}\n\n"
        "После оплаты отправьте чек прямо в этот бот.\n\n"
        "После проверки оплаты вам пришлют ссылку в канал."
    )

    await callback.answer()


# ==========================================
# ОПЛАТА TELEGRAM STARS
# ==========================================

@dp.callback_query(F.data == "pay_stars")
async def pay_stars_handler(callback: CallbackQuery):

    await callback.message.answer(
        "https://t.me/+UgyCrJdF-wQzMmQy"
    )

    await callback.answer()
# ==========================================
# ПОДТВЕРЖДЕНИЕ ПЕРЕД ОПЛАТОЙ
# ==========================================

@dp.pre_checkout_query()
async def pre_checkout_handler(
    pre_checkout_query: PreCheckoutQuery
):

    await pre_checkout_query.answer(
        ok=True
    )


# ==========================================
# УСПЕШНАЯ ОПЛАТА STARS
# ==========================================

@dp.message(F.successful_payment)
async def successful_payment_handler(message: Message):

    payment = message.successful_payment

    if payment.currency != "XTR":
        return

    await message.answer(
        "✅ Оплата успешно получена!\n\n"
        "Спасибо за покупку."
    )

    await bot.send_message(
        MY_ID,
        "💰 Новая оплата Stars!\n\n"
        f"👤 Пользователь: {message.from_user.full_name}\n"
        f"🆔 ID: {message.from_user.id}\n"
        f"⭐ Сумма: {payment.total_amount} Stars"
    )


# ==========================================
# ОТВЕТ АДМИНА ПОЛЬЗОВАТЕЛЮ
# ==========================================

@dp.message(F.from_user.id == MY_ID)
async def admin_message_handler(message: Message):

    # Админ должен отвечать именно Reply
    if not message.reply_to_message:
        return

    # Ищем сообщение пользователя
    # по ID пересланного сообщения
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
# СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЕЙ
# ==========================================

@dp.message(
    F.from_user.id != MY_ID,
    F.text,
    ~F.text.startswith("/")
)
async def user_message_handler(message: Message):

    try:

        forwarded = await bot.forward_message(
            chat_id=MY_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )

        # Запоминаем:
        # сообщение админа -> пользователь
        message_map[forwarded.message_id] = message.from_user.id

    except Exception as e:

        print(
            f"Ошибка пересылки сообщения: {e}"
        )


# ==========================================
# СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЕЙ НЕ ТЕКСТОМ
# ==========================================

@dp.message(
    F.from_user.id != MY_ID,
    ~F.text
)
async def user_media_handler(message: Message):

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


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":
    asyncio.run(main())