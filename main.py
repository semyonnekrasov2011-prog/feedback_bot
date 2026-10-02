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


# =========================
# НАСТРОЙКИ
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Telegram ID администратора
MY_ID = 7507779053

# Карта для оплаты в рублях
CARD_NUMBER = "2202208888777241"

# Цены
CHANNEL_1_STARS = 250
CHANNEL_1_RUB = 330

CHANNEL_2_STARS = 400
CHANNEL_2_RUB = 450


# =========================
# BOT / DISPATCHER
# =========================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ID сообщения администратора -> ID покупателя
#
# Используется для Stars:
# администратор отвечает Reply на сообщение
# с оплатой и отправляет одноразовую ссылку.
payment_map = {}


# ID пересланного сообщения администратора -> ID пользователя
#
# Используется для обычной переписки:
# пользователь пишет боту -> сообщение приходит админу ->
# админ отвечает Reply -> ответ уходит пользователю.
message_map = {}


# =========================
# КЛАВИАТУРЫ
# =========================

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


def payment_keyboard(channel):
    if channel == 1:
        stars = CHANNEL_1_STARS
        rub = CHANNEL_1_RUB
    else:
        stars = CHANNEL_2_STARS
        rub = CHANNEL_2_RUB

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"⭐ Оплатить — {stars} Stars",
                    callback_data=f"pay_stars_{channel}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"💳 Оплатить — {rub} ₽",
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


# =========================
# /START
# =========================

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "👋 Добро пожаловать!\n\n"
        "Выберите канал, который хотите приобрести:",
        reply_markup=channels_keyboard()
    )


# =========================
# ВЫБОР КАНАЛА
# =========================

@dp.callback_query(F.data == "channel_1")
async def channel_1_handler(callback: CallbackQuery):
    await callback.message.edit_text(
    "📢 Канал 1 — фембои\n\n"
    "Канал с фембоями.\n\n"
    f"⭐ Стоимость: {CHANNEL_1_STARS} Stars\n"
    f"💳 Стоимость: {CHANNEL_1_RUB} ₽\n\n"
    "Выберите способ оплаты:",
    reply_markup=payment_keyboard(1)
)

    await callback.answer()


@dp.callback_query(F.data == "channel_2")
async def channel_2_handler(callback: CallbackQuery):
    await callback.message.edit_text(
    "📢 Канал 2 — твинк-контент\n\n"
    "Канал с "взрослым".\n\n"
    "Если непонятна тема, уточните.\n\n"
    f"⭐ Стоимость: {CHANNEL_2_STARS} Stars\n"
    f"💳 Стоимость: {CHANNEL_2_RUB} ₽\n\n"
    "Выберите способ оплаты:",
    reply_markup=payment_keyboard(2)
)

    await callback.answer()


# =========================
# НАЗАД К КАНАЛАМ
# =========================

@dp.callback_query(F.data == "back_channels")
async def back_channels_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "👋 Выберите канал, который хотите приобрести:",
        reply_markup=channels_keyboard()
    )

    await callback.answer()


# =========================
# ОПЛАТА STARS — КАНАЛ 1
# =========================

@dp.callback_query(F.data == "pay_stars_1")
async def pay_stars_1_handler(callback: CallbackQuery):

    await bot.send_invoice(
        chat_id=callback.from_user.id,

        title="Канал 1",

        description="Доступ к каналу 1",

        payload=f"channel_1:{callback.from_user.id}",

        currency="XTR",

        prices=[
            LabeledPrice(
                label="Доступ к каналу 1",
                amount=CHANNEL_1_STARS
            )
        ]
    )

    await callback.answer()


# =========================
# ОПЛАТА STARS — КАНАЛ 2
# =========================

@dp.callback_query(F.data == "pay_stars_2")
async def pay_stars_2_handler(callback: CallbackQuery):

    await bot.send_invoice(
        chat_id=callback.from_user.id,

        title="Канал 2",

        description="Доступ к каналу 2",

        payload=f"channel_2:{callback.from_user.id}",

        currency="XTR",

        prices=[
            LabeledPrice(
                label="Доступ к каналу 2",
                amount=CHANNEL_2_STARS
            )
        ]
    )

    await callback.answer()


# =========================
# PRE-CHECKOUT
# =========================

@dp.pre_checkout_query()
async def pre_checkout_handler(
    pre_checkout_query: PreCheckoutQuery
):

    payload = pre_checkout_query.invoice_payload

    if not (
        payload.startswith("channel_1:")
        or payload.startswith("channel_2:")
    ):
        await pre_checkout_query.answer(
            ok=False,
            error_message="Неизвестный заказ."
        )
        return

    await pre_checkout_query.answer(ok=True)


# =========================
# УСПЕШНАЯ ОПЛАТА STARS
# =========================

@dp.message(F.successful_payment)
async def successful_payment_handler(message: Message):

    payment = message.successful_payment

    # Нас интересуют только Telegram Stars
    if payment.currency != "XTR":
        return

    payload = payment.invoice_payload

    # Определяем канал
    if payload.startswith("channel_1:"):

        channel_name = "Канал 1"
        expected_price = CHANNEL_1_STARS

    elif payload.startswith("channel_2:"):

        channel_name = "Канал 2"
        expected_price = CHANNEL_2_STARS

    else:

        await message.answer(
            "❌ Не удалось определить товар."
        )

        return

    # Проверяем сумму
    if payment.total_amount != expected_price:

        await bot.send_message(
            MY_ID,

            "⚠️ ВНИМАНИЕ: получена оплата "
            "с неожиданной суммой!\n\n"

            f"👤 Пользователь: "
            f"{message.from_user.full_name}\n"

            f"🆔 ID: "
            f"{message.from_user.id}\n"

            f"📢 Товар: "
            f"{channel_name}\n"

            f"⭐ Получено: "
            f"{payment.total_amount}\n"

            f"⭐ Ожидалось: "
            f"{expected_price}"
        )

        await message.answer(
            "⚠️ Платёж получен, но возникла проблема "
            "с проверкой суммы.\n\n"
            "Администратор проверит оплату."
        )

        return

    # Отправляем админу уведомление
    admin_message = await bot.send_message(

        MY_ID,

        "💰 НОВАЯ ОПЛАТА STARS!\n\n"

        f"👤 Пользователь: "
        f"{message.from_user.full_name}\n"

        f"🆔 ID: "
        f"{message.from_user.id}\n"

        f"📢 Канал: "
        f"{channel_name}\n"

        f"⭐ Сумма: "
        f"{payment.total_amount} Stars\n"

        f"🧾 Charge ID: "
        f"{payment.telegram_payment_charge_id}\n\n"

        "✅ Оплата подтверждена Telegram.\n\n"

        "Чтобы выдать доступ, ответьте "
        "REPLY на это сообщение "
        "одноразовой ссылкой-приглашением "
        "на нужный канал."
    )

    # Запоминаем, кому принадлежит эта оплата
    payment_map[
        admin_message.message_id
    ] = message.from_user.id

    # Сообщение покупателю
    await message.answer(
        "✅ Оплата успешно получена!\n\n"

        "Спасибо за покупку.\n"

        "Администратор сейчас выдаст вам "
        "одноразовую ссылку на канал."
    )


# =========================
# ОПЛАТА РУБЛЯМИ — КАНАЛ 1
# =========================

@dp.callback_query(F.data == "pay_rub_1")
async def pay_rub_1_handler(callback: CallbackQuery):

    await callback.message.answer(

        "💳 Оплата канала 1\n\n"

        f"Номер карты:\n"
        f"{CARD_NUMBER}\n\n"

        f"Сумма: {CHANNEL_1_RUB} ₽\n\n"

        "После оплаты отправьте чек "
        "прямо в этот бот."
    )

    await callback.answer()


# =========================
# ОПЛАТА РУБЛЯМИ — КАНАЛ 2
# =========================

@dp.callback_query(F.data == "pay_rub_2")
async def pay_rub_2_handler(callback: CallbackQuery):

    await callback.message.answer(

        "💳 Оплата канала 2\n\n"

        f"Номер карты:\n"
        f"{CARD_NUMBER}\n\n"

        f"Сумма: {CHANNEL_2_RUB} ₽\n\n"

        "После оплаты отправьте чек "
        "прямо в этот бот."
    )

    await callback.answer()


# =========================
# СООБЩЕНИЯ АДМИНИСТРАТОРА
# =========================

@dp.message(F.from_user.id == MY_ID)
async def admin_message_handler(message: Message):

    # Работаем только если админ отвечает
    # на сообщение через Reply
    if not message.reply_to_message:
        return

    replied_message_id = (
        message.reply_to_message.message_id
    )

    # ---------------------------------
    # 1. ВЫДАЧА ССЫЛКИ ПОСЛЕ STARS
    # ---------------------------------

    user_id = payment_map.get(
        replied_message_id
    )

    if user_id:

        # Ссылка должна быть отправлена
        # именно текстовым сообщением
        if not message.text:

            await message.answer(
                "❌ Отправь одноразовую ссылку "
                "текстом через Reply."
            )

            return

        try:

            await bot.send_message(

                user_id,

                "🎉 Оплата подтверждена!\n\n"

                "🔗 Ваша одноразовая "
                "ссылка для входа:\n"

                f"{message.text}"
            )

            await message.answer(
                "✅ Ссылка отправлена пользователю."
            )

            # После успешной отправки удаляем
            # связь, чтобы повторно её использовать
            # через этот платёж было нельзя.
            del payment_map[
                replied_message_id
            ]

        except Exception as e:

            await message.answer(
                "❌ Не удалось отправить ссылку:\n"
                f"{e}"
            )

        return

    # ---------------------------------
    # 2. ОБЫЧНЫЙ ОТВЕТ ПОЛЬЗОВАТЕЛЮ
    # ---------------------------------

    user_id = message_map.get(
        replied_message_id
    )

    if not user_id:

        await message.answer(
            "❌ Не удалось определить пользователя."
        )

        return

    try:

        # Копируем сообщение админа
        # пользователю: текст, фото, видео и т.д.
        await bot.copy_message(

            chat_id=user_id,

            from_chat_id=MY_ID,

            message_id=message.message_id
        )

    except Exception as e:

        await message.answer(
            "❌ Ошибка отправки:\n"
            f"{e}"
        )


# =========================
# СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЕЙ
# =========================

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

        # Запоминаем пользователя
        message_map[
            forwarded.message_id
        ] = message.from_user.id

    except Exception as e:

        print(
            f"Ошибка пересылки сообщения: {e}"
        )


# =========================
# МЕДИА ОТ ПОЛЬЗОВАТЕЛЯ
# =========================

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

        # Запоминаем пользователя
        message_map[
            forwarded.message_id
        ] = message.from_user.id

    except Exception as e:

        print(
            f"Ошибка пересылки сообщения: {e}"
        )


# =========================
# ЗАПУСК
# =========================

async def main():

    if not BOT_TOKEN:

        raise ValueError(
            "BOT_TOKEN не найден!\n"
            "Добавь BOT_TOKEN в Railway Variables."
        )

    print(
        "========================================"
    )

    print(
        "🤖 БОТ УСПЕШНО ЗАПУЩЕН!"
    )

    print(
        "========================================"
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())