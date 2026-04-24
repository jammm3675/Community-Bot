import os
from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states.otc_states import OTCStates
from keyboards.menu import get_otc_type_kb
from loader import db
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

OTC_TOPIC_ID = int(os.getenv("OTC_TOPIC_ID", 1166))
CHAT_ID = int(os.getenv("CHAT_ID", -1003405424179))


@router.callback_query(F.data == "otc_start")
async def otc_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Choose trade type:", reply_markup=get_otc_type_kb()
    )
    await state.set_state(OTCStates.choosing_type)
    await callback.answer()


@router.callback_query(OTCStates.choosing_type, F.data.startswith("otc_type_"))
async def otc_type_selected(callback: CallbackQuery, state: FSMContext):
    trade_type = callback.data.split("_")[-1]
    await state.update_data(trade_type=trade_type)
    await callback.message.edit_text(
        f"Selected: {trade_type}. What are you selling/buying?"
    )
    await state.set_state(OTCStates.entering_item)
    await callback.answer()


@router.message(OTCStates.entering_item)
async def otc_item_entered(message: Message, state: FSMContext):
    await state.update_data(item=message.text)
    await message.answer("Enter the price (e.g., 2 TON):")
    await state.set_state(OTCStates.entering_price)


@router.message(OTCStates.entering_price)
async def otc_price_entered(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    price = message.text
    item = data["item"]
    trade_type = data["trade_type"]
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"

    # Save to DB
    await db.create_otc_post(user_id, trade_type, item, price)

    # Send to channel/group topic
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Contact Seller", url=f"tg://user?id={user_id}"))

    text = (
        f"📦 <b>{trade_type}</b>\n\n"
        f"<b>Item:</b> {item}\n"
        f"<b>Price:</b> {price}\n\n"
        f"👤 <b>Seller:</b> @{username}"
    )

    await bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=OTC_TOPIC_ID,
        text=text,
        reply_markup=kb.as_markup(),
        parse_mode="HTML",
    )

    await message.answer("✅ Your OTC order has been posted!")
    await state.clear()
