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

# Ссылка для оплаты рублями через Tribute
RUB_PAYMENT_LINK = "https://t.me/tribute/app?startapp=s15qD"

# Цена в Telegram Stars
# Можешь изменить число
STAR_PRICE = 250


# ==========================================
# ЗАПУСК БОТА
# ==========================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Сообщение, которое бот переслал админу:
# message_id -> user_id
message_map = {}


# ==========================================
# КНОПКИ
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
        "💳 Оплата рублями\n\n"
        "По каким-либо вопросам можете писать прямо в бота, "
        "вам ответят в ближайшее время.",
        reply_markup=payment_keyboard()
    )


# ==========================================
# ОПЛАТА TELEGRAM STARS
# ==========================================

@dp.callback_query(F.data == "pay_stars")
async def pay_stars(callback: CallbackQuery):

    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title="Оплата товара",
        description="Оплата товара через Telegram Stars",
        payload=f"order_{callback.from_user.id}",
        currency="XTR",
        prices=[
            LabeledPrice(
                label="Товар",
                amount=STAR_PRICE
            )
        ]
    )

    await callback.answer()


# ==========================================
# ПОДТВЕРЖДЕНИЕ ПЕРЕД ОПЛАТОЙ
# ==========================================

@dp.pre_checkout_query()
async def pre_checkout(
    pre_checkout_query: PreCheckoutQuery
):

    await bot.answer_pre_checkout_query(
        pre_checkout_query_id=pre_checkout_query.id,
        ok=True
    )


# ==========================================
# УСПЕШНАЯ ОПЛАТА STARS
# ==========================================

@dp.message(F.successful_payment)
async def successful_payment(message: Message):

    payment = message.successful_payment

    # Проверяем, что это Stars
    if payment.currency == "XTR":

        await message.answer(
            "✅ Оплата успешно получена!\n\n"
            "Спасибо за покупку."
        )

        # Сообщаем тебе об оплате
        await bot.send_message(
            MY_ID,
            "💰 Новая оплата Stars!\n\n"
            f"👤 Пользователь: {message.from_user.full_name}\n"
            f"🆔 ID: {message.from_user.id}\n"
            f"⭐ Сумма: {payment.total_amount} Stars"
        )


# ==========================================
# ТВОИ ОТВЕТЫ ПОЛЬЗОВАТЕЛЯМ
# ==========================================

@dp.message(F.from_user.id == MY_ID)
async def admin_message(message: Message):

    # Если сообщение не Reply — ничего не делаем
    if not message.reply_to_message:
        return

    # Находим пользователя по сообщению
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

        # Пересылаем сообщение тебе
        forwarded = await bot.forward_message(
            chat_id=MY_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )

        # Запоминаем пользователя
        message_map[
            forwarded.message_id
        ] = message.from_user.id

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