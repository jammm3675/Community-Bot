from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


def get_contact_kb(user_id):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Contact Seller", url=f"tg://user?id={user_id}")
    )
    return builder.as_markup()
