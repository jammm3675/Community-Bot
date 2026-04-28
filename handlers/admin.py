from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from loader import db, ADMIN_IDS
from states.admin_states import SupplyCreation
from utils import safe_edit_text, safe_answer
from keyboards.menu import get_admin_supply_kb, get_main_menu

router = Router()

@router.callback_query(F.data == "admin_create_supply")
async def start_supply_creation(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return

    await safe_edit_text(callback.message, "📝 Enter supply title:")
    await state.set_state(SupplyCreation.entering_name)
    await safe_answer(callback)

@router.message(SupplyCreation.entering_name)
async def supply_name_entered(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("📝 Enter supply description (use blockquotes in final):")
    await state.set_state(SupplyCreation.entering_description)

@router.message(SupplyCreation.entering_description)
async def supply_desc_entered(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("💰 Enter XP cost (integer):")
    await state.set_state(SupplyCreation.entering_price)

@router.message(SupplyCreation.entering_price)
async def supply_price_entered(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Please enter a valid number for XP cost.")
        return
    await state.update_data(xp_cost=int(message.text))
    await message.answer("📦 Enter max activations (limit):")
    await state.set_state(SupplyCreation.entering_limit)

@router.message(SupplyCreation.entering_limit)
async def supply_limit_entered(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Please enter a valid number for limit.")
        return

    data = await state.get_data()
    title = data['title']
    description = data['description']
    xp_cost = data['xp_cost']
    limit = int(message.text)

    await db.create_secret_lot(title, description, xp_cost, limit)

    await message.answer(
        f"✅ <b>Supply Created Successfully!</b>\n\n"
        f"<b>Title:</b> {title}\n"
        f"<b>Cost:</b> {xp_cost} XP\n"
        f"<b>Limit:</b> {limit}",
        reply_markup=get_main_menu(message.from_user.id)
    )
    await state.clear()

@router.callback_query(F.data == "admin_view_lots")
async def admin_view_lots(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return

    lots = await db.get_secret_lots()
    if not lots.data:
        await safe_answer(callback, "No active lots found.", show_alert=True)
        return

    text = "📜 <b>Active Secret Lots</b>\n\n"
    for lot in lots.data:
        text += (
            f"🔹 <b>{lot['title']}</b>\n"
            f"Price: {lot['xp_cost']} XP | {lot['activations_count']}/{lot['max_activations']}\n\n"
        )

    await safe_edit_text(callback.message, text, reply_markup=get_admin_supply_kb())
    await safe_answer(callback)
