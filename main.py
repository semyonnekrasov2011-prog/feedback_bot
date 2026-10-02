import os
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)


# ==========================================
# НАСТРОЙКИ
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Telegram ID администратора
MY_ID = 7507779053

# Общая карта для оплаты рублями
CARD_NUMBER = "2202208888777241"


# ==========================================
# STARS-ССЫЛКИ
# ==========================================

CHANNEL_1_STARS = "https://t.me/+iRWfFkCKvqI3NWQy"
CHANNEL_2_STARS = "https://t.me/+S49c_NiM7p9jYzM6"


# ==========================================
# БОТ
# ==========================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ==========================================
# СООТВЕТСТВИЕ:
# сообщение администратора -> пользователь
# ==========================================

message_map = {}


# ==========================================
# СООТВЕТСТВИЕ:
# сообщение "Я оплатил" -> пользователь
# ==========================================

payment_map = {}


# ==========================================
# ВЫБОР КАНАЛА
# ==========================================

def channels_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Канал 1 — 330 ₽ / 250 ⭐",
                    callback_data="channel_1"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📢 Канал 2 — 450 ₽ / 400 ⭐",
                    callback_data="channel_2"
                )
            ]
        ]
    )


# ==========================================
# КНОПКИ ОПЛАТЫ
# ==========================================

def payment_keyboard(channel):

    if channel == 1:
        stars_text = "⭐ Оплатить — 250 Stars"
        rub_text = "💳 Оплатить — 330 ₽"

    else:
        stars_text = "⭐ Оплатить — 400 Stars"
        rub_text = "💳 Оплатить — 450 ₽"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=stars_text,
                    callback_data=f"pay_stars_{channel}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=rub_text,
                    callback_data=f"pay_rub_{channel}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="back_channels"
                )
            ]
        ]
    )


# ==========================================
# КНОПКА "Я ОПЛАТИЛ"
# ==========================================

def paid_keyboard(channel):

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Я оплатил",
                    callback_data=f"paid_{channel}"
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
        "Выберите канал, который хотите приобрести:",
        reply_markup=channels_keyboard()
    )


# ==========================================
# КАНАЛ 1
# ==========================================

@dp.callback_query(F.data == "channel_1")
async def channel_1_handler(callback: CallbackQuery):

    await callback.message.edit_text(
        "📢 Канал 1\n\n"
        "⭐ Стоимость: 250 Stars\n"
        "💳 Стоимость: 330 ₽\n\n"
        "Выберите способ оплаты:",
        reply_markup=payment_keyboard(1)
    )

    await callback.answer()


# ==========================================
# КАНАЛ 2
# ==========================================

@dp.callback_query(F.data == "channel_2")
async def channel_2_handler(callback: CallbackQuery):

    await callback.message.edit_text(
        "📢 Канал 2\n\n"
        "⭐ Стоимость: 400 Stars\n"
        "💳 Стоимость: 450 ₽\n\n"
        "Выберите способ оплаты:",
        reply_markup=payment_keyboard(2)
    )

    await callback.answer()


# ==========================================
# НАЗАД
# ==========================================

@dp.callback_query(F.data == "back_channels")
async def back_channels_handler(callback: CallbackQuery):

    await callback.message.edit_text(
        "👋 Выберите канал, который хотите приобрести:",
        reply_markup=channels_keyboard()
    )

    await callback.answer()


# ==========================================
# STARS — КАНАЛ 1
# ==========================================

@dp.callback_query(F.data == "pay_stars_1")
async def pay_stars_1_handler(callback: CallbackQuery):

    await callback.message.answer(
        "⭐ Оплата канала 1\n\n"
        "Откройте ссылку и произведите оплату:\n"
        f"{CHANNEL_1_STARS}\n\n"
        "После оплаты нажмите кнопку «✅ Я оплатил».",
        reply_markup=paid_keyboard(1)
    )

    await callback.answer()


# ==========================================
# STARS — КАНАЛ 2
# ==========================================

@dp.callback_query(F.data == "pay_stars_2")
async def pay_stars_2_handler(callback: CallbackQuery):

    await callback.message.answer(
        "⭐ Оплата канала 2\n\n"
        "Откройте ссылку и произведите оплату:\n"
        f"{CHANNEL_2_STARS}\n\n"
        "После оплаты нажмите кнопку «✅ Я оплатил».",
        reply_markup=paid_keyboard(2)
    )

    await callback.answer()


# ==========================================
# РУБЛИ — КАНАЛ 1
# ==========================================

@dp.callback_query(F.data == "pay_rub_1")
async def pay_rub_1_handler(callback: CallbackQuery):

    await callback.message.answer(
        "💳 Оплата канала 1\n\n"
        f"Номер карты:\n{CARD_NUMBER}\n\n"
        "Сумма: 330 ₽\n\n"
        "После оплаты отправьте чек прямо в этот бот."
    )

    await callback.answer()


# ==========================================
# РУБЛИ — КАНАЛ 2
# ==========================================

@dp.callback_query(F.data == "pay_rub_2")
async def pay_rub_2_handler(callback: CallbackQuery):

    await callback.message.answer(
        "💳 Оплата канала 2\n\n"
        f"Номер карты:\n{CARD_NUMBER}\n\n"
        "Сумма: 450 ₽\n\n"
        "После оплаты отправьте чек прямо в этот бот."
    )

    await callback.answer()


# ==========================================
# ПОЛЬЗОВАТЕЛЬ НАЖАЛ "Я ОПЛАТИЛ"
# ==========================================

@dp.callback_query(F.data.startswith("paid_"))
async def paid_handler(callback: CallbackQuery):

    channel = callback.data.split("_")[1]

    if channel == "1":
        channel_name = "Канал 1"
        price = "250 Stars"

    else:
        channel_name = "Канал 2"
        price = "400 Stars"

    user = callback.from_user

    # Сообщение админу
    admin_message = await bot.send_message(
        MY_ID,
        "🔔 Пользователь сообщил об оплате!\n\n"
        f"👤 Имя: {user.full_name}\n"
        f"🆔 ID: {user.id}\n"
        f"📢 Канал: {channel_name}\n"
        f"⭐ Сумма: {price}\n\n"
        "Если оплата подтверждена, ответьте Reply "
        "на это сообщение ссылкой на канал."
    )

    # Запоминаем, кому нужно отправить ссылку
    payment_map[admin_message.message_id] = user.id

    await callback.message.answer(
        "✅ Информация об оплате отправлена администратору.\n\n"
        "После проверки оплаты вам отправят ссылку на канал."
    )

    await callback.answer()


# ==========================================
# ОТВЕТ АДМИНА
# ==========================================

@dp.message(F.from_user.id == MY_ID)
async def admin_message_handler(message: Message):

    if not message.reply_to_message:
        return

    replied_message_id = message.reply_to_message.message_id

    # Проверяем, является ли это уведомлением об оплате
    user_id = payment_map.get(replied_message_id)

    if user_id:

        try:

            await bot.copy_message(
                chat_id=user_id,
                from_chat_id=MY_ID,
                message_id=message.message_id
            )

            await message.answer(
                "✅ Ссылка отправлена пользователю."
            )

        except Exception as e:

            await message.answer(
                f"❌ Ошибка отправки ссылки:\n{e}"
            )

        return

    # Обычный ответ пользователю
    user_id = message_map.get(replied_message_id)

    if not user_id:
        await message.answer(
            "❌ Не удалось определить пользователя."
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
# ТЕКСТОВЫЕ СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЕЙ
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

        message_map[forwarded.message_id] = message.from_user.id

    except Exception as e:

        print(
            f"Ошибка пересылки сообщения: {e}"
        )


# ==========================================
# ФОТО / ВИДЕО / ДОКУМЕНТЫ И ДРУГОЕ
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