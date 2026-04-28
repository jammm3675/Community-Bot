from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from loader import db, ADMIN_IDS
from utils import safe_edit_text, safe_answer, get_progress_bar, calculate_level_stats, safe_send_animation
from keyboards.menu import get_main_menu_keyboard, get_lot_kb, get_admin_supply_kb

router = Router()

# Обновленный ID/URL гифки
DEFAULT_GIF = "https://media.giphy.com/media/vFKqnCdLPNOKc/giphy.gif"

MENU_TEXT = (
    "<tg-emoji emoji-id=\"5273867703709361006\">👿</tg-emoji><b> NOTAPES | ECOSYSTEM </b><tg-emoji emoji-id=\"5273867703709361006\">👿</tg-emoji>\n\n"
    "<blockquote>Добро пожаловать в наш пиксельный мир.\n"
    "Управляй профилем, участвуй в сделках и следи за лидербордом ниже.</blockquote>"
)

@router.message(Command("start"))
@router.message(Command("menu"))
async def show_menu(message: Message):
    # Получаем GIF из базы. Если в базе пусто, используем старый ID как запасной
    gif_id = await db.get_setting("main_gif", DEFAULT_GIF)

    await safe_send_animation(
        target=message,
        animation=gif_id,
        caption=MENU_TEXT,
        reply_markup=get_main_menu_keyboard(message.from_user.id)
    )

@router.callback_query(F.data == "menu_main")
async def show_menu_cb(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except Exception:
        pass

    gif_id = await db.get_setting("main_gif", DEFAULT_GIF)

    await safe_send_animation(
        target=callback.message,
        animation=gif_id,
        caption=MENU_TEXT,
        reply_markup=get_main_menu_keyboard(callback.from_user.id)
    )
    await safe_answer(callback)

@router.callback_query(F.data == "rpg_stats")
async def show_stats(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    if not user:
        await safe_answer(callback, "You need to send some messages first!", show_alert=True)
        return

    # Прямой расчет уровня из XP (игнорируем колонку level в БД для отображения)
    level, xp_in_lvl, percent = calculate_level_stats(user['xp'])

    text = (
        "<tg-emoji emoji-id=\"5273741156792951269\">🏆</tg-emoji> <b>ИНФОРМАЦИЯ О ГЕРОЕ</b>\n\n"
        f"<blockquote>Имя: {callback.from_user.first_name}\n"
        f"Уровень: {level}\n"
        f"Опыт: {xp_in_lvl}/1000</blockquote>\n\n"
        f"<b>Прогресс:</b>\n{get_progress_bar(percent)} {int(percent)}%"
    )

    await safe_edit_text(callback.message, text, reply_markup=get_main_menu_keyboard(callback.from_user.id))
    await safe_answer(callback)

@router.callback_query(F.data == "rpg_top")
async def show_top(callback: CallbackQuery):
    top_users = await db.get_leaderboard(10)

    text = "🏆 <b>Leaderboard</b>\n\n"
    for i, user in enumerate(top_users.data, 1):
        text += f"{i}. {user['first_name']} — {user['xp']} XP 🔥{user['streak']}\n"

    await safe_edit_text(callback.message, text, reply_markup=get_main_menu_keyboard(callback.from_user.id))
    await safe_answer(callback)

@router.callback_query(F.data == "rpg_tags")
async def show_tags_info(callback: CallbackQuery):
    text = (
        "<tg-emoji emoji-id=\"5296348778012361146\">🏷</tg-emoji> <b>СИСТЕМА ТЕГОВ</b>\n\n"
        "<blockquote>Тег отображается рядом с твоим именем в чате.\n\n"
        "👶 Новичок: с 1 уровня\n"
        "🎖 Ветеран: с 5 уровня\n"
        "⚡️ VIP: с 20 уровня</blockquote>"
    )
    await safe_edit_text(callback.message, text, reply_markup=get_main_menu_keyboard(callback.from_user.id))
    await safe_answer(callback)

@router.callback_query(F.data == "rpg_burn")
async def show_burn(callback: CallbackQuery):
    lots = await db.get_secret_lots()
    if not lots.data:
        await safe_answer(callback, "No secret lots available right now!", show_alert=True)
        return

    lot = lots.data[0]  # Show the first active lot
    text = (
        f"🎁 <b>Secret Supply: {lot['title']}</b>\n\n"
        f"<blockquote>"
        f"{lot['description']}\n\n"
        f"💰 <b>Cost:</b> {lot['xp_cost']} XP\n"
        f"📦 <b>Remaining:</b> {lot['max_activations'] - lot['activations_count']}"
        f"</blockquote>"
    )

    await safe_edit_text(
        callback.message, text, reply_markup=get_lot_kb(lot["id"], lot["xp_cost"])
    )
    await safe_answer(callback)

@router.callback_query(F.data.startswith("burn_lot_"))
async def process_burn(callback: CallbackQuery):
    lot_id = int(callback.data.split("_")[-1])
    success, msg = await db.buy_secret_lot(callback.from_user.id, lot_id)

    if success:
        await safe_answer(
            callback, "🔥 XP Burned! You've claimed the secret lot!", show_alert=True
        )
        await show_stats(callback)
    else:
        await safe_answer(callback, f"❌ {msg}", show_alert=True)

@router.callback_query(F.data == "admin_supply_panel")
async def admin_supply_panel(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await safe_answer(callback, "Access denied!", show_alert=True)
        return

    await safe_edit_text(
        callback.message,
        "🛠 <b>Supply Management</b>\n\nManage limited offers and secret lots here.",
        reply_markup=get_admin_supply_kb()
    )
    await safe_answer(callback)
