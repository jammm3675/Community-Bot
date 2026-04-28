import os
from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states.otc_states import OTCStates
from keyboards.menu import get_otc_type_kb, get_main_menu
from loader import db
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils import safe_edit_text, safe_answer

router = Router()

OTC_TOPIC_ID = int(os.getenv("OTC_TOPIC_ID", 1166))
CHAT_ID = int(os.getenv("CHAT_ID", -1003405424179))

@router.callback_query(F.data == "otc_start")
async def otc_start(callback: CallbackQuery, state: FSMContext):
    text = (
        "🤝 <b>OTC Market</b>\n\n"
        "<blockquote>"
        "Choose what you want to do. <tg-emoji id='5368324170671202286'>💎</tg-emoji>\n"
        "You can post your Buy or Sell orders here."
        "</blockquote>"
    )
    await safe_edit_text(callback.message, text, reply_markup=get_otc_type_kb())
    await state.set_state(OTCStates.choosing_type)
    await safe_answer(callback)

@router.callback_query(OTCStates.choosing_type, F.data.startswith("otc_type_"))
async def otc_type_selected(callback: CallbackQuery, state: FSMContext):
    trade_type = callback.data.split("_")[-1]
    await state.update_data(trade_type=trade_type)

    text = (
        f"✅ <b>Type: {trade_type}</b>\n\n"
        f"<blockquote>"
        f"What are you {'selling' if trade_type == 'WTS' else 'buying'}?\n"
        f"<i>Please provide a clear name for the item.</i>"
        f"</blockquote>"
    )
    await safe_edit_text(callback.message, text)
    await state.set_state(OTCStates.entering_item)
    await safe_answer(callback)

@router.message(OTCStates.entering_item)
async def otc_item_entered(message: Message, state: FSMContext):
    await state.update_data(item=message.text)
    text = (
        "💰 <b>Set the Price</b>\n\n"
        "<blockquote>"
        "Enter the desired price (e.g., 2 TON or 100 USDT).\n"
        "<i>Be realistic to attract buyers!</i>"
        "</blockquote>"
    )
    await message.answer(text)
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
    kb.row(InlineKeyboardButton(text="📩 Contact", url=f"tg://user?id={user_id}"))

    text = (
        f"📦 <b>{trade_type} Order</b>\n\n"
        f"<blockquote>"
        f"<b>Item:</b> {item}\n"
        f"<b>Price:</b> {price}\n"
        f"<b>Seller:</b> @{username}"
        f"</blockquote>\n"
        f"#OTC #{trade_type}"
    )

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=OTC_TOPIC_ID,
            text=text,
            reply_markup=kb.as_markup(),
            parse_mode="HTML",
        )
        await message.answer(
            "✅ <b>Order Posted!</b>\n\nYour OTC order has been successfully sent to the channel.",
            reply_markup=get_main_menu(message.from_user.id)
        )
    except Exception as e:
        await message.answer(f"❌ Error posting to channel: {str(e)}")

    await state.clear()
