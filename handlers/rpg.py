from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from loader import db, ADMIN_IDS
from utils import safe_edit_text, safe_answer, get_progress_bar, calculate_level_stats
from keyboards.menu import get_main_menu, get_lot_kb, get_admin_supply_kb

router = Router()

@router.message(Command("start"))
@router.message(Command("menu"))
async def show_menu(message: Message):
    await message.answer("Welcome to NOTAPES Ecosystem!", reply_markup=get_main_menu(message.from_user.id))

@router.callback_query(F.data == "menu_main")
async def show_menu_cb(callback: CallbackQuery):
    await safe_edit_text(
        callback.message, "Welcome to NOTAPES Ecosystem!", reply_markup=get_main_menu(callback.from_user.id)
    )
    await safe_answer(callback)

@router.callback_query(F.data == "rpg_stats")
async def show_stats(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    if not user:
        await safe_answer(callback, "You need to send some messages first!", show_alert=True)
        return

    level, xp_in_lvl, percent = calculate_level_stats(user["xp"])
    progress_bar = get_progress_bar(percent)

    text = (
        f"👤 <b>Profile: {callback.from_user.first_name}</b>\n\n"
        f"<blockquote>"
        f"<b>Level {level}</b>\n"
        f"{progress_bar} {int(percent)}%\n\n"
        f"🔥 <b>XP:</b> {user['xp']}\n"
        f"⭐ <b>REP:</b> {user['rep']}\n"
        f"⚡ <b>Streak:</b> {user['streak']} days"
        f"</blockquote>"
    )

    await safe_edit_text(callback.message, text, reply_markup=get_main_menu(callback.from_user.id))
    await safe_answer(callback)

@router.callback_query(F.data == "rpg_top")
async def show_top(callback: CallbackQuery):
    top_users = await db.get_leaderboard(10)

    text = "🏆 <b>Leaderboard</b>\n\n"
    for i, user in enumerate(top_users.data, 1):
        text += f"{i}. {user['first_name']} — {user['xp']} XP 🔥{user['streak']}\n"

    await safe_edit_text(callback.message, text, reply_markup=get_main_menu(callback.from_user.id))
    await safe_answer(callback)

@router.callback_query(F.data == "rpg_tags")
async def show_tags(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    level = user.get("level", 1) if user else 1

    tag = "Новичок"
    if 5 <= level < 20:
        tag = "Ветеран"
    elif level >= 20:
        tag = "VIP"

    text = (
        f"🏷 <b>Your Current Tag Status</b>\n\n"
        f"<blockquote>"
        f"<b>Current Tag:</b> {tag}\n"
        f"<b>Level:</b> {level}\n\n"
        f"<i>Tags are automatically updated when you level up.</i>"
        f"</blockquote>"
    )

    await safe_edit_text(callback.message, text, reply_markup=get_main_menu(callback.from_user.id))
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

@router.callback_query(F.data == "admin_supply_menu")
async def admin_supply_menu(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await safe_answer(callback, "Access denied!", show_alert=True)
        return

    await safe_edit_text(
        callback.message,
        "🛠 <b>Supply Management</b>\n\nManage limited offers and secret lots here.",
        reply_markup=get_admin_supply_kb()
    )
    await safe_answer(callback)
