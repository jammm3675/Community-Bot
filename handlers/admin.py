import logging
import asyncio
from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from loader import db, ADMIN_IDS
from states.admin_states import SupplyCreation
from utils import safe_edit_text, safe_answer
from keyboards.menu import get_admin_supply_kb, get_main_menu_keyboard
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

DEFAULT_GIF = "CgACAgIAAxkBAAEbt3NpqAn2obJdHyFVZbi_JOspLX96KAAC7pQAAkCBQEk_A-aRj7qxNToE"

def get_cancel_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data="admin_supply_panel")
    return builder.as_markup()

def get_preview_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Опубликовать", callback_data="admin_publish_supply")
    builder.button(text="✏️ Изменить текст", callback_data="admin_edit_text")
    builder.button(text="💰 Изменить цену", callback_data="admin_edit_price")
    builder.button(text="❌ Отмена", callback_data="admin_supply_panel")
    builder.adjust(1, 2, 1)
    return builder.as_markup()

async def update_admin_msg(chat_id: int, state: FSMContext, bot: Bot, text: str, reply_markup=None):
    data = await state.get_data()
    msg_id = data.get('admin_msg_id')

    gif_id = await db.get_setting("main_gif", DEFAULT_GIF)

    if msg_id:
        try:
            await bot.edit_message_caption(
                chat_id=chat_id,
                message_id=msg_id,
                caption=text,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
            return
        except Exception:
            pass

    # Fallback to new message
    msg = await bot.send_animation(
        chat_id=chat_id,
        animation=gif_id,
        caption=text,
        reply_markup=reply_markup
    )
    await state.update_data(admin_msg_id=msg.message_id)

async def show_preview(chat_id: int, state: FSMContext, bot: Bot):
    data = await state.get_data()
    title = data.get('title', '...')
    description = data.get('description', '...')
    xp_cost = data.get('xp_cost', 0)
    limit = data.get('limit', 0)

    text = (
        "<tg-emoji emoji-id=\"5258096772776991776\">⚙️</tg-emoji> <b>ПРЕДПРОСМОТР SUPPLY</b>\n\n"
        f"<blockquote><b>Название:</b> {title}\n"
        f"<b>Описание:</b> {description}\n"
        f"<b>Цена:</b> {xp_cost} XP\n"
        f"<b>Лимит:</b> {limit}</blockquote>"
    )

    await update_admin_msg(chat_id, state, bot, text, get_preview_kb())

@router.callback_query(F.data == "admin_create_supply")
async def start_supply_creation(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if callback.from_user.id not in ADMIN_IDS:
        return

    await state.clear()
    text = (
        "<tg-emoji emoji-id=\"5258096772776991776\">⚙️</tg-emoji> <b>СОЗДАНИЕ SUPPLY</b>\n\n"
        "<blockquote>Введите название предложения.</blockquote>"
    )

    try:
        await callback.message.delete()
    except Exception:
        pass

    gif_id = await db.get_setting("main_gif", DEFAULT_GIF)

    msg = await bot.send_animation(
        chat_id=callback.message.chat.id,
        animation=gif_id,
        caption=text,
        reply_markup=get_cancel_kb()
    )
    await state.update_data(admin_msg_id=msg.message_id)
    await state.set_state(SupplyCreation.entering_name)
    await safe_answer(callback)

# Редактирование из превью
@router.callback_query(F.data == "admin_edit_text")
async def edit_text(callback: CallbackQuery, state: FSMContext, bot: Bot):
    text = "<blockquote><tg-emoji emoji-id='5258096772776991776'>⚙️</tg-emoji> <b>Настройка:</b>\nВведите название (описание введете следующим шагом)...</blockquote>"
    await update_admin_msg(callback.message.chat.id, state, bot, text, get_cancel_kb())
    await state.set_state(SupplyCreation.entering_name)
    await safe_answer(callback)

@router.callback_query(F.data == "admin_edit_price")
async def edit_price_cb(callback: CallbackQuery, state: FSMContext, bot: Bot):
    text = "<blockquote><tg-emoji emoji-id='5258096772776991776'>⚙️</tg-emoji> <b>Настройка:</b>\nВведите новую цену в XP...</blockquote>"
    await update_admin_msg(callback.message.chat.id, state, bot, text, get_cancel_kb())
    await state.set_state(SupplyCreation.entering_price)
    await safe_answer(callback)

# Обработчики ввода сообщений
@router.message(SupplyCreation.entering_name)
async def supply_name_entered(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(title=message.text)
    await message.delete()

    text = (
        "<tg-emoji emoji-id=\"5258096772776991776\">⚙️</tg-emoji> <b>СОЗДАНИЕ SUPPLY</b>\n\n"
        "<blockquote>Введите подробное описание предложения.</blockquote>"
    )
    await update_admin_msg(message.chat.id, state, bot, text, get_cancel_kb())
    await state.set_state(SupplyCreation.entering_description)

@router.message(SupplyCreation.entering_description)
async def supply_desc_entered(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(description=message.text)
    await message.delete()

    text = (
        "<tg-emoji emoji-id=\"5258096772776991776\">⚙️</tg-emoji> <b>СОЗДАНИЕ SUPPLY</b>\n\n"
        "<blockquote>Введите стоимость в XP (целое число).</blockquote>"
    )
    await update_admin_msg(message.chat.id, state, bot, text, get_cancel_kb())
    await state.set_state(SupplyCreation.entering_price)

@router.message(SupplyCreation.entering_price)
async def supply_price_entered(message: Message, state: FSMContext, bot: Bot):
    if not message.text.isdigit():
        msg = await message.answer("<blockquote>❌ Пожалуйста, введите корректное число для стоимости XP.</blockquote>")
        await message.delete()
        await asyncio.sleep(3)
        try: await msg.delete()
        except: pass
        return

    await state.update_data(xp_cost=int(message.text))
    await message.delete()

    text = (
        "<tg-emoji emoji-id=\"5258096772776991776\">⚙️</tg-emoji> <b>СОЗДАНИЕ SUPPLY</b>\n\n"
        "<blockquote>Введите лимит активаций (количество).</blockquote>"
    )
    await update_admin_msg(message.chat.id, state, bot, text, get_cancel_kb())
    await state.set_state(SupplyCreation.entering_limit)

@router.message(SupplyCreation.entering_limit)
async def supply_limit_entered(message: Message, state: FSMContext, bot: Bot):
    if not message.text.isdigit():
        msg = await message.answer("<blockquote>❌ Пожалуйста, введите корректное число для лимита.</blockquote>")
        await message.delete()
        await asyncio.sleep(3)
        try: await msg.delete()
        except: pass
        return

    await state.update_data(limit=int(message.text))
    await message.delete()
    await show_preview(message.chat.id, state, bot)

@router.callback_query(F.data == "admin_publish_supply")
async def publish_supply(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    title = data['title']
    description = data['description']
    xp_cost = data['xp_cost']
    limit = data['limit']

    try:
        # Используем правильные колонки для Supabase: title, description, xp_cost, max_activations
        await db.create_secret_lot(title, description, xp_cost, limit)

        text = (
            f"✅ <b>Supply успешно создан!</b>\n\n"
            f"<blockquote><b>Название:</b> {title}\n"
            f"<b>Стоимость:</b> {xp_cost} XP\n"
            f"<b>Лимит:</b> {limit}</blockquote>"
        )
        await update_admin_msg(callback.message.chat.id, state, bot, text, get_main_menu_keyboard(callback.from_user.id))
    except Exception as e:
        logging.error(f"Database error: {e}")
        text = (
            "<blockquote>❌ <b>Ошибка: колонка в БД не найдена</b>\n\n"
            "Проверьте схему таблицы secret_lots и соответствие ключей.</blockquote>"
        )
        await update_admin_msg(callback.message.chat.id, state, bot, text, get_main_menu_keyboard(callback.from_user.id))

    await state.clear()
    await safe_answer(callback)

@router.callback_query(F.data == "admin_view_lots")
async def admin_view_lots(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return

    lots = await db.get_secret_lots()
    if not lots.data:
        await safe_answer(callback, "Активные лоты не найдены.", show_alert=True)
        return

    text = "📜 <b>СПИСОК АКТИВНЫХ SUPPLY</b>\n\n"
    for lot in lots.data:
        text += (
            f"🔹 <b>{lot['title']}</b>\n"
            f"<blockquote>Цена: {lot['xp_cost']} XP\n"
            f"Остаток: {lot['activations_count']}/{lot['max_activations']}</blockquote>\n\n"
        )

    await safe_edit_text(callback.message, text, reply_markup=get_admin_supply_kb())
    await safe_answer(callback)

@router.message(F.animation, F.from_user.id.in_(ADMIN_IDS))
async def update_gif_via_bot(message: Message):
    new_gif_id = message.animation.file_id
    await db.update_setting("main_gif", new_gif_id)
    await message.answer(f"✅ <b>GIF обновлен в базе данных!</b>\nID: <code>{new_gif_id}</code>")
